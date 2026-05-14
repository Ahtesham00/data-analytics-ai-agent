import logging
import json
from flask import Blueprint, request, Response, stream_with_context

from app.agent.agent import AnalyticsAgent

logger = logging.getLogger(__name__)
chat_bp = Blueprint("chat", __name__)


def sse_event(event_type: str, data: dict) -> str:
    payload = json.dumps(data, default=str)
    return f"event: {event_type}\ndata: {payload}\n\n"


@chat_bp.post("/api/chat/<conversation_id>")
def chat(conversation_id: str):
    body     = request.get_json(silent=True) or {}
    message  = body.get("message", "").strip()
    provider = body.get("provider", "anthropic")

    if not message:
        return {"error": "message is required"}, 400

    logger.info("Chat request: conv=%s provider=%s message=%.80s", conversation_id, provider, message)

    def generate():
        try:
            agent = AnalyticsAgent(provider=provider)
            for event_type, event_data in agent.run(conversation_id, message):
                yield sse_event(event_type, event_data)
        except GeneratorExit:
            logger.info("Client disconnected from conv=%s", conversation_id)
        except Exception as exc:
            logger.exception("Unhandled error in chat stream for conv=%s", conversation_id)
            yield sse_event("error", {"message": "An unexpected error occurred."})

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
