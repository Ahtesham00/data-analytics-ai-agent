import json
import logging
import os
from typing import Generator

import anthropic

from app.llm.base import LLMClient, StreamResponse
from app.tools.definitions import TOOL_DEFINITIONS

logger = logging.getLogger(__name__)


def _to_anthropic_tool(t: dict) -> dict:
    return {
        "name": t["name"],
        "description": t["description"],
        "input_schema": t["input_schema"],
    }


class AnthropicClient(LLMClient):
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")
        self.client = anthropic.Anthropic(api_key=api_key)
        logger.info("AnthropicClient initialised with model=%s", self.model)

    def stream_turn(
        self,
        messages: list[dict],
        tools: list[dict],
        system: str,
    ) -> StreamResponse:
        anthropic_tools = [_to_anthropic_tool(t) for t in tools]
        logger.info(
            "Anthropic stream_turn: model=%s messages=%d tools=%d",
            self.model, len(messages), len(anthropic_tools),
        )

        def _gen() -> Generator:
            current_tool_id   = None
            current_tool_name = None
            current_tool_args = ""
            stop_reason       = "end_turn"

            try:
                with self.client.messages.stream(
                    model=self.model,
                    max_tokens=4096,
                    system=system,
                    messages=messages,
                    tools=anthropic_tools,
                ) as stream:
                    for event in stream:
                        event_type = event.type

                        if event_type == "content_block_start":
                            block = event.content_block
                            if block.type == "tool_use":
                                current_tool_id   = block.id
                                current_tool_name = block.name
                                current_tool_args = ""

                        elif event_type == "content_block_delta":
                            delta = event.delta
                            if delta.type == "text_delta":
                                yield "text", {"content": delta.text}
                            elif delta.type == "input_json_delta":
                                current_tool_args += delta.partial_json

                        elif event_type == "content_block_stop":
                            if current_tool_id and current_tool_name:
                                try:
                                    parsed_input = json.loads(current_tool_args) if current_tool_args else {}
                                except json.JSONDecodeError:
                                    parsed_input = {}
                                    logger.warning(
                                        "Failed to parse tool args for %s: %s",
                                        current_tool_name, current_tool_args[:200],
                                    )
                                logger.info(
                                    "Tool call complete: %s id=%s", current_tool_name, current_tool_id
                                )
                                yield "tool_call_complete", {
                                    "id":    current_tool_id,
                                    "name":  current_tool_name,
                                    "input": parsed_input,
                                }
                                current_tool_id   = None
                                current_tool_name = None
                                current_tool_args = ""

                        elif event_type == "message_delta":
                            if hasattr(event.delta, "stop_reason") and event.delta.stop_reason:
                                stop_reason = event.delta.stop_reason

            except anthropic.APITimeoutError:
                logger.error("Anthropic API timeout")
                yield "__stop_reason__", "timeout"
                return
            except anthropic.RateLimitError:
                logger.error("Anthropic rate limit hit")
                yield "__stop_reason__", "rate_limit"
                return
            except anthropic.AuthenticationError:
                logger.error("Anthropic authentication error")
                yield "__stop_reason__", "auth_error"
                return
            except Exception as exc:
                logger.exception("Unexpected Anthropic error: %s", exc)
                yield "__stop_reason__", "error"
                return

            yield "__stop_reason__", stop_reason

        return StreamResponse(_gen())

    def one_shot(self, system: str, user: str) -> str:
        logger.info("Anthropic one_shot: model=%s", self.model)
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return response.content[0].text if response.content else ""
        except Exception as exc:
            logger.exception("Anthropic one_shot error: %s", exc)
            return ""
