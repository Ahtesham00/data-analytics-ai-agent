import json
import logging
from typing import Generator
from uuid import uuid4

from app.agent.accumulator import AssistantMessageAccumulator
from app.agent.context_builder import build_llm_messages
from app.agent.system_prompt import SYSTEM_PROMPT
from app.llm import get_llm_client
from app.repositories.chat_repository import ChatRepository
from app.tools.definitions import TOOL_DEFINITIONS, DISPLAY_TOOL_NAMES
from app.tools.executor import dispatch_tool

logger = logging.getLogger(__name__)


class AnalyticsAgent:
    MAX_ITERATIONS = 8

    def __init__(self, provider: str = "anthropic"):
        self.provider = provider
        self.llm      = get_llm_client(provider)
        self.chat     = ChatRepository()

    def run(self, conversation_id: str, user_message: str) -> Generator:
        """
        Generator: yields (event_type, data) tuples.
        event_type: "text" | "tool_display" | "error" | "done"
        """
        # Verify conversation exists
        conv = self.chat.get_conversation(conversation_id)
        if not conv:
            yield "error", {"message": f"Conversation {conversation_id} not found."}
            return

        # 1. Persist the user message
        user_msg = {
            "message_id":  str(uuid4()),
            "role":        "user",
            "content":     user_message,
            "tool_renders": [],
        }
        self.chat.append_message(conversation_id, user_msg)
        logger.info("User message saved for conv=%s", conversation_id)

        # 2. Load history and build LLM messages
        db_messages  = self.chat.get_messages(conversation_id)
        summary      = conv.get("summary")
        llm_messages = build_llm_messages(db_messages, provider=self.provider, summary=summary)

        # 3. Agentic loop
        accumulator   = AssistantMessageAccumulator()
        loop_messages    = llm_messages
        iterations       = 0
        last_sql_result  = None

        while iterations < self.MAX_ITERATIONS:
            iterations += 1
            logger.info(
                "Agent loop iteration %d/%d for conv=%s",
                iterations, self.MAX_ITERATIONS, conversation_id,
            )

            response = self.llm.stream_turn(
                messages=loop_messages,
                tools=TOOL_DEFINITIONS,
                system=SYSTEM_PROMPT,
            )

            # Track only THIS iteration's output — these become the next
            # assistant turn added to loop_messages. The accumulator tracks
            # everything across all iterations for final persistence.
            iter_text: str = ""
            iter_tool_calls: list[dict] = []  # {tool_id, tool_name, tool_input, tool_result}

            for chunk_type, chunk_data in response:
                if chunk_type == "text":
                    iter_text += chunk_data["content"]
                    accumulator.add_text(chunk_data["content"])
                    yield "text", chunk_data

                elif chunk_type == "tool_call_complete":
                    tool_id    = chunk_data["id"]
                    tool_name  = chunk_data["name"]
                    tool_input = chunk_data["input"]

                    # SMART AUTO-FILL: If LLM calls a display tool with missing or empty 'data',
                    # inject the last SQL result. GPT-4o often passes data: [] instead of
                    # omitting the key, so we check for falsy values too.
                    if tool_name in DISPLAY_TOOL_NAMES and not tool_input.get("data"):
                        if last_sql_result:
                            logger.info("Smart Auto-fill: Injecting last_sql_result (%d rows) into %s", len(last_sql_result), tool_name)
                            tool_input["data"] = last_sql_result
                        else:
                            logger.warning("Smart Auto-fill: %s has empty/missing 'data', but no previous SQL result found!", tool_name)

                    if tool_name in DISPLAY_TOOL_NAMES:
                        # Auto-pivot data if needed for charts
                        if "data" in tool_input and "x_key" in tool_input and "y_keys" in tool_input:
                            tool_input["data"] = self._auto_pivot(
                                tool_input["data"], 
                                tool_input["x_key"], 
                                tool_input["y_keys"]
                            )
                        logger.debug("Tool Input for %s: %s", tool_name, json.dumps(tool_input, default=str)[:1000])

                    tool_result, display_event = dispatch_tool(tool_name, tool_input)

                    if tool_name == "execute_sql":
                        last_sql_result = tool_result.get("rows") if isinstance(tool_result, dict) else None
                        if last_sql_result:
                            logger.info("Captured %d rows for potential auto-fill", len(last_sql_result))

                    if display_event:
                        # Extra logging for frontend-bound display events
                        props = display_event.get("props", {})
                        has_data = "data" in props and bool(props["data"])
                        logger.info("Displaying %s: render_id=%s, data_present=%s", 
                                    tool_name, display_event.get("render_id"), has_data)
                        
                        accumulator.add_display(display_event)
                        yield "tool_display", display_event

                    accumulator.add_tool_call(tool_id, tool_name, tool_input)
                    iter_tool_calls.append({
                        "tool_id":     tool_id,
                        "tool_name":   tool_name,
                        "tool_input":  tool_input,
                        "tool_result": tool_result,
                    })

            stop_reason = response.stop_reason

            if stop_reason in ("timeout", "rate_limit", "auth_error", "error"):
                error_messages = {
                    "timeout":    "The AI service timed out. Please try again.",
                    "rate_limit": "Rate limit reached. Please wait a moment.",
                    "auth_error": "API key error. Check your configuration.",
                    "error":      "An unexpected error occurred.",
                }
                yield "error", {"message": error_messages.get(stop_reason, "An error occurred.")}
                return

            if not iter_tool_calls:
                # LLM produced no tool calls — it's done.
                break

            # Build the assistant turn from THIS ITERATION ONLY, in the
            # correct wire format for the active provider.
            assistant_turn = self._build_assistant_turn(iter_text, iter_tool_calls)
            tool_result_messages = self._build_tool_result_messages(
                iter_tool_calls, self.provider
            )
            loop_messages = loop_messages + [assistant_turn] + tool_result_messages

            if stop_reason in ("end_turn", "stop"):
                break

        # 4. Summarise long conversations
        if len(db_messages) > 40 and not summary:
            self._maybe_summarise(conversation_id, db_messages)

        # 5. Persist the completed assistant message
        final_msg = accumulator.build_final_message()
        self.chat.append_message(conversation_id, final_msg)
        logger.info(
            "Agent turn complete for conv=%s: iterations=%d, sql=%s, displays=%d",
            conversation_id, iterations,
            "yes" if final_msg["sql_executed"] else "no",
            len(final_msg["tool_renders"]),
        )

        # 6. Auto-title the conversation on the first exchange
        if len(db_messages) <= 2:
            title = user_message[:60] + ("…" if len(user_message) > 60 else "")
            self.chat.set_title(conversation_id, title)

        yield "done", {"message_id": final_msg["message_id"]}

    def _build_assistant_turn(self, text: str, tool_calls: list[dict]) -> dict:
        """Build an assistant message in the correct wire format for the provider."""
        if self.provider == "anthropic":
            content_blocks: list[dict] = []
            if text:
                content_blocks.append({"type": "text", "text": text})
            for tc in tool_calls:
                content_blocks.append({
                    "type":  "tool_use",
                    "id":    tc["tool_id"],
                    "name":  tc["tool_name"],
                    "input": tc["tool_input"],
                })
            return {"role": "assistant", "content": content_blocks}
        else:
            # OpenAI: tool_calls is a top-level key, content is plain text or null
            openai_tool_calls = [
                {
                    "id":   tc["tool_id"],
                    "type": "function",
                    "function": {
                        "name":      tc["tool_name"],
                        "arguments": json.dumps(tc["tool_input"], default=str),
                    },
                }
                for tc in tool_calls
            ]
            return {
                "role":       "assistant",
                "content":    text or None,
                "tool_calls": openai_tool_calls,
            }

    def _build_tool_result_messages(
        self, tool_calls: list[dict], provider: str
    ) -> list[dict]:
        """Build tool result messages in provider format."""
        if provider == "anthropic":
            return [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tc["tool_id"],
                            "content": json.dumps(tc["tool_result"], default=str),
                        }
                        for tc in tool_calls
                    ],
                }
            ]
        else:
            # OpenAI format: separate tool messages
            return [
                {
                    "role": "tool",
                    "tool_call_id": tc["tool_id"],
                    "content": json.dumps(tc["tool_result"], default=str),
                }
                for tc in tool_calls
            ]

    def _maybe_summarise(self, conversation_id: str, db_messages: list[dict]) -> None:
        try:
            oldest = db_messages[:-10]
            summary_text = self.llm.one_shot(
                system=(
                    "Summarise this analytics conversation in 5 bullet points covering: "
                    "what data was explored, which queries ran, and key findings."
                ),
                user="\n\n".join(
                    f"{m['role'].upper()}: {m['content']}" for m in oldest if m.get("content")
                ),
            )
            if summary_text:
                self.chat.set_summary(conversation_id, summary_text)
                logger.info("Summarised conversation %s", conversation_id)
        except Exception as exc:
            logger.warning("Failed to summarise conversation %s: %s", conversation_id, exc)

    def _auto_pivot(self, data: list[dict], x_key: str, y_keys: list[dict]) -> list[dict]:
        """
        Transforms 'long' data into 'wide' data for Recharts.
        Handles both simple pivots (Category) and composite pivots (Category_Region).
        """
        if not data or not isinstance(data, list):
            return data
            
        y_key_names = {str(yk.get("key")) for yk in y_keys}
        first_row   = data[0]
        
        # If the data already has the requested keys, no pivot needed.
        if any(k in y_key_names for k in first_row.keys()):
            return data

        # Identify roles for each column
        cat_cols = [c for c, v in first_row.items() if c != x_key and not isinstance(v, (int, float))]
        num_cols = [c for c, v in first_row.items() if isinstance(v, (int, float))]
        
        if not cat_cols or not num_cols:
            return data
            
        value_col = num_cols[0] # Usually 'sales' or 'total_sales'
        
        logger.info("Auto-pivoting: cat_cols=%s, value_col=%s", cat_cols, value_col)
        
        pivoted = {}
        for row in data:
            x_val = row.get(x_key)
            if x_val not in pivoted:
                pivoted[x_val] = {x_key: x_val}
            
            # 1. Try matching individual category columns
            # 2. Try matching combinations (with underscores or spaces)
            cat_vals = [str(row.get(c)) for c in cat_cols]
            
            matched_key = None
            
            # Check combinations first (more specific)
            # Try: "Furniture_Central", "Furniture Central", etc.
            potential_combos = [
                "_".join(cat_vals),
                " ".join(cat_vals),
                "_".join(cat_vals).replace(" ", "_"), # Handles "Office Supplies_Central" -> "Office_Supplies_Central"
            ]
            
            for combo in potential_combos:
                if combo in y_key_names:
                    matched_key = combo
                    break
            
            # If no combo matches, try individual values
            if not matched_key:
                for val in cat_vals:
                    if val in y_key_names:
                        matched_key = val
                        break
                    # Try space -> underscore mapping
                    val_slug = val.replace(" ", "_")
                    if val_slug in y_key_names:
                        matched_key = val_slug
                        break

            if matched_key:
                pivoted[x_val][matched_key] = row.get(value_col)

        return sorted(pivoted.values(), key=lambda x: str(x.get(x_key, "")))
