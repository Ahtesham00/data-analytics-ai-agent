import json
import logging
import os
from typing import Generator

from openai import OpenAI
import openai

from app.llm.base import LLMClient, StreamResponse

logger = logging.getLogger(__name__)


def _to_openai_tool(t: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"],
        },
    }


class OpenAIClient(LLMClient):
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY", "")
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        self.client = OpenAI(api_key=api_key)
        logger.info("OpenAIClient initialised with model=%s", self.model)

    def stream_turn(
        self,
        messages: list[dict],
        tools: list[dict],
        system: str,
    ) -> StreamResponse:
        openai_tools = [_to_openai_tool(t) for t in tools]
        openai_messages = [{"role": "system", "content": system}] + messages
        logger.info(
            "OpenAI stream_turn: model=%s messages=%d tools=%d",
            self.model, len(openai_messages), len(openai_tools),
        )

        def _gen() -> Generator:
            # Accumulate tool calls across chunks: {index: {id, name, args}}
            tool_calls_acc: dict[int, dict] = {}
            stop_reason = "stop"

            try:
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=openai_messages,
                    tools=openai_tools,
                    parallel_tool_calls=False,
                    stream=True,
                )

                for chunk in stream:
                    choice = chunk.choices[0] if chunk.choices else None
                    if not choice:
                        continue

                    delta = choice.delta

                    if delta.content:
                        yield "text", {"content": delta.content}

                    if delta.tool_calls:
                        for tc in delta.tool_calls:
                            idx = tc.index
                            if idx not in tool_calls_acc:
                                tool_calls_acc[idx] = {"id": "", "name": "", "args": ""}
                            if tc.id:
                                tool_calls_acc[idx]["id"] = tc.id
                            if tc.function and tc.function.name:
                                tool_calls_acc[idx]["name"] = tc.function.name
                            if tc.function and tc.function.arguments:
                                tool_calls_acc[idx]["args"] += tc.function.arguments

                    if choice.finish_reason:
                        stop_reason = choice.finish_reason

            except openai.APITimeoutError:
                logger.error("OpenAI API timeout")
                yield "__stop_reason__", "timeout"
                return
            except openai.RateLimitError:
                logger.error("OpenAI rate limit hit")
                yield "__stop_reason__", "rate_limit"
                return
            except openai.AuthenticationError:
                logger.error("OpenAI authentication error")
                yield "__stop_reason__", "auth_error"
                return
            except Exception as exc:
                logger.exception("Unexpected OpenAI error: %s", exc)
                yield "__stop_reason__", "error"
                return

            # Emit completed tool calls after stream ends
            for idx in sorted(tool_calls_acc.keys()):
                tc = tool_calls_acc[idx]
                try:
                    parsed_input = json.loads(tc["args"]) if tc["args"] else {}
                except json.JSONDecodeError:
                    parsed_input = {}
                    logger.warning("Failed to parse tool args for %s: %s", tc["name"], tc["args"][:200])
                logger.info("Tool call complete: %s id=%s", tc["name"], tc["id"])
                yield "tool_call_complete", {
                    "id":    tc["id"],
                    "name":  tc["name"],
                    "input": parsed_input,
                }

            yield "__stop_reason__", stop_reason

        return StreamResponse(_gen())

    def one_shot(self, system: str, user: str) -> str:
        logger.info("OpenAI one_shot: model=%s", self.model)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.exception("OpenAI one_shot error: %s", exc)
            return ""
