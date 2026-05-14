import logging

logger = logging.getLogger(__name__)

_TRUNCATION_NOTE = {
    "role": "user",
    "content": "[Earlier messages truncated to fit context window.]",
}


def to_llm_format_anthropic(db_messages: list[dict]) -> list[dict]:
    """
    Convert SQLite message rows to Anthropic API message format,
    reconstructing tool_use / tool_result blocks from sql_executed + tool_renders.
    """
    result: list[dict] = []

    for msg in db_messages:
        if msg["role"] == "user":
            result.append({"role": "user", "content": msg["content"]})
            continue

        # Build assistant content blocks
        content_blocks: list[dict] = []

        if msg.get("content"):
            content_blocks.append({"type": "text", "text": msg["content"]})

        # Reconstruct SQL tool call if one was executed
        if msg.get("sql_executed"):
            tc_id = f"tc_sql_{msg['message_id'][:8]}"
            content_blocks.append({
                "type":  "tool_use",
                "id":    tc_id,
                "name":  "execute_sql",
                "input": {"sql": msg["sql_executed"]},
            })
            result.append({"role": "assistant", "content": content_blocks})
            result.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tc_id,
                        "content": "[SQL result — used in the visualisations below]",
                    }
                ],
            })
            content_blocks = []

        # Reconstruct display tool calls
        tool_renders = msg.get("tool_renders", [])
        for render in tool_renders:
            tc_id = f"tc_{render['render_id'][:8]}"
            content_blocks.append({
                "type":  "tool_use",
                "id":    tc_id,
                "name":  render["tool_name"],
                "input": render["props"],
            })

        if content_blocks:
            result.append({"role": "assistant", "content": content_blocks})
            if tool_renders:
                tool_results = [
                    {
                        "type": "tool_result",
                        "tool_use_id": f"tc_{r['render_id'][:8]}",
                        "content": '{"displayed": true}',
                    }
                    for r in tool_renders
                ]
                result.append({"role": "user", "content": tool_results})

    return result


def to_llm_format_openai(db_messages: list[dict]) -> list[dict]:
    """
    Convert SQLite message rows to OpenAI API message format.
    """
    result: list[dict] = []

    for msg in db_messages:
        if msg["role"] == "user":
            result.append({"role": "user", "content": msg["content"]})
            continue

        # Build assistant message with optional tool_calls
        tool_calls = []

        if msg.get("sql_executed"):
            import json
            tc_id = f"call_sql_{msg['message_id'][:8]}"
            tool_calls.append({
                "id": tc_id,
                "type": "function",
                "function": {
                    "name": "execute_sql",
                    "arguments": json.dumps({"sql": msg["sql_executed"]}),
                },
            })

        tool_renders = msg.get("tool_renders", [])
        for render in tool_renders:
            import json
            tc_id = f"call_{render['render_id'][:8]}"
            tool_calls.append({
                "id": tc_id,
                "type": "function",
                "function": {
                    "name": render["tool_name"],
                    "arguments": json.dumps(render["props"]),
                },
            })

        assistant_msg: dict = {"role": "assistant", "content": msg.get("content", "") or None}
        if tool_calls:
            assistant_msg["tool_calls"] = tool_calls
        result.append(assistant_msg)

        # Add tool results
        if msg.get("sql_executed"):
            import json
            tc_id = f"call_sql_{msg['message_id'][:8]}"
            result.append({
                "role": "tool",
                "tool_call_id": tc_id,
                "content": "[SQL result — used in the visualisations below]",
            })

        for render in tool_renders:
            tc_id = f"call_{render['render_id'][:8]}"
            result.append({
                "role": "tool",
                "tool_call_id": tc_id,
                "content": '{"displayed": true}',
            })

    return result


def build_llm_messages(
    db_messages: list[dict],
    provider: str = "anthropic",
    summary: str | None = None,
) -> list[dict]:
    """
    Build the LLM message array with context window management.
    """
    to_llm = to_llm_format_anthropic if provider == "anthropic" else to_llm_format_openai

    if summary:
        summary_block: dict = {
            "role": "user" if provider == "anthropic" else "system",
            "content": f"[Conversation summary: {summary}]",
        }
        recent = to_llm(db_messages[-12:])
        return [summary_block] + recent

    if len(db_messages) <= 20:
        return to_llm(db_messages)

    # Truncation: first 2 + last 12
    # We process head and tail separately then join them to ensure 
    # to_llm doesn't have its assistant->tool sequences broken by the note.
    head = to_llm(db_messages[:2])
    tail = to_llm(db_messages[-12:])
    
    logger.info(
        "Truncated context: %d messages -> %d kept (%d head, %d tail)", 
        len(db_messages), len(head) + len(tail), len(head), len(tail)
    )
    return head + [_TRUNCATION_NOTE] + tail
