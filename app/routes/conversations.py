import logging
from flask import Blueprint, request, jsonify

from app.repositories.chat_repository import ChatRepository

logger = logging.getLogger(__name__)
conversations_bp = Blueprint("conversations", __name__)
repo = ChatRepository()


@conversations_bp.post("/api/conversations")
def create_conversation():
    body     = request.get_json(silent=True) or {}
    provider = body.get("provider", "anthropic")
    conv     = repo.create_conversation(provider)
    logger.info("Created conversation %s (provider=%s)", conv["conversation_id"], provider)
    return jsonify(conv), 201


@conversations_bp.get("/api/conversations")
def list_conversations():
    convs = repo.list_conversations()
    return jsonify(convs)


@conversations_bp.get("/api/conversations/<conversation_id>")
def get_conversation(conversation_id: str):
    conv = repo.get_conversation(conversation_id)
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404
    messages = repo.get_messages(conversation_id)
    conv["messages"] = messages
    return jsonify(conv)


@conversations_bp.delete("/api/conversations/<conversation_id>")
def delete_conversation(conversation_id: str):
    conv = repo.get_conversation(conversation_id)
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404
    repo.delete_conversation(conversation_id)
    logger.info("Deleted conversation %s", conversation_id)
    return jsonify({"deleted": True})


@conversations_bp.patch("/api/conversations/<conversation_id>")
def update_conversation(conversation_id: str):
    conv = repo.get_conversation(conversation_id)
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404

    body = request.get_json(silent=True) or {}

    if "provider" in body:
        repo.set_provider(conversation_id, body["provider"])
        logger.info("Updated provider for %s → %s", conversation_id, body["provider"])

    if "title" in body:
        repo.set_title(conversation_id, body["title"])
        logger.info("Updated title for %s", conversation_id)

    updated = repo.get_conversation(conversation_id)
    return jsonify(updated)
