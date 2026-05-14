import logging
from uuid import uuid4

from app.tools.definitions import DISPLAY_TOOL_NAMES
from app.tools.sql_executor import execute_sql

logger = logging.getLogger(__name__)


def dispatch_tool(name: str, tool_input: dict) -> tuple[dict, dict | None]:
    """
    Execute a tool by name.
    Returns (llm_result, display_event_or_None).
    display_event is the dict to stream as a tool_display SSE event.
    """
    logger.info("Dispatching tool: %s | input keys: %s", name, list(tool_input.keys()))

    if name == "execute_sql":
        result = execute_sql(
            sql=tool_input.get("sql", ""),
            description=tool_input.get("description", ""),
        )
        return result, None

    if name in DISPLAY_TOOL_NAMES:
        render_id = f"r_{uuid4().hex[:8]}"
        display_event = {
            "render_id": render_id,
            "tool_name": name,
            "props": tool_input,
        }
        logger.debug("Display tool %s → render_id=%s", name, render_id)
        return {"displayed": True, "render_id": render_id}, display_event

    logger.warning("Unknown tool called: %s", name)
    return {"error": f"Unknown tool: {name}"}, None
