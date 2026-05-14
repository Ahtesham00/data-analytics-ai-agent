import logging
from uuid import uuid4

logger = logging.getLogger(__name__)


class AssistantMessageAccumulator:
    """Collects all output produced during one agent turn."""

    def __init__(self):
        self._text: str = ""
        self._tool_calls: list[tuple[str, str, dict]] = []  # (id, name, input)
        self._displays: list[dict] = []  # display tool events → stored in tool_renders
        self._sql_last: str | None = None

    def add_text(self, chunk: str) -> None:
        self._text += chunk

    def add_tool_call(self, tool_id: str, name: str, tool_input: dict) -> None:
        self._tool_calls.append((tool_id, name, tool_input))
        if name == "execute_sql":
            self._sql_last = tool_input.get("sql")

    def add_display(self, event: dict) -> None:
        self._displays.append(event)

    def get_current_turn(self) -> dict:
        """
        Build the LLM-format assistant message for the next loop iteration.
        Anthropic format: content is a list of blocks.
        """
        content_blocks: list[dict] = []

        if self._text:
            content_blocks.append({"type": "text", "text": self._text})

        for tool_id, name, tool_input in self._tool_calls:
            content_blocks.append({
                "type":  "tool_use",
                "id":    tool_id,
                "name":  name,
                "input": tool_input,
            })

        return {"role": "assistant", "content": content_blocks}

    def build_final_message(self) -> dict:
        """Build the SQLite row dict to persist via ChatRepository."""
        return {
            "message_id":   str(uuid4()),
            "role":         "assistant",
            "content":      self._text,
            "sql_executed": self._sql_last,
            "tool_renders": self._displays,
        }

    def reset_for_continuation(self) -> None:
        """Clear text accumulation for the next LLM sub-turn (tool result pending)."""
        self._text = ""
