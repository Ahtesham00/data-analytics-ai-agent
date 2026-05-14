from abc import ABC, abstractmethod
from typing import Generator


class StreamResponse:
    """Wraps the streaming generator and holds stop_reason after iteration."""

    def __init__(self, gen: Generator):
        self._gen = gen
        self.stop_reason: str = "end_turn"

    def __iter__(self):
        for item in self._gen:
            if isinstance(item, tuple) and len(item) == 2:
                chunk_type, chunk_data = item
                if chunk_type == "__stop_reason__":
                    self.stop_reason = chunk_data
                else:
                    yield chunk_type, chunk_data
            else:
                yield item


class LLMClient(ABC):
    @abstractmethod
    def stream_turn(
        self,
        messages: list[dict],
        tools: list[dict],
        system: str,
    ) -> StreamResponse:
        """
        Stream one LLM turn.
        Returns a StreamResponse whose iterator yields (chunk_type, chunk_data).
        chunk_type values: "text", "tool_call_complete"
        After full iteration, response.stop_reason is set.
        """

    @abstractmethod
    def one_shot(self, system: str, user: str) -> str:
        """Non-streaming single-turn call. Returns assistant text."""
