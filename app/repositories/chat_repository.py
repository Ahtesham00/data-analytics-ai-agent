import json
import logging
import os
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

logger = logging.getLogger(__name__)


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class ChatRepository:
    def __init__(self, path: str | None = None):
        self.path = path or os.environ.get("SQLITE_PATH", "./data/analytics.db")

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    # ── Conversations ──────────────────────────────────────────────────

    def create_conversation(self, provider: str = "anthropic") -> dict:
        cid = str(uuid4())
        now = utcnow()
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO conversations (conversation_id, provider, created_at, updated_at) "
                "VALUES (?, ?, ?, ?)",
                [cid, provider, now, now],
            )
        return {
            "conversation_id": cid,
            "title": "New Conversation",
            "provider": provider,
            "created_at": now,
        }

    def get_conversation(self, cid: str) -> dict | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM conversations WHERE conversation_id = ?", [cid]
            ).fetchone()
        return dict(row) if row else None

    def list_conversations(self, limit: int = 50) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT conversation_id, title, provider, created_at, updated_at "
                "FROM conversations ORDER BY updated_at DESC LIMIT ?",
                [limit],
            ).fetchall()
        return [dict(r) for r in rows]

    def set_title(self, cid: str, title: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE conversation_id = ?",
                [title, utcnow(), cid],
            )

    def set_provider(self, cid: str, provider: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE conversations SET provider = ?, updated_at = ? WHERE conversation_id = ?",
                [provider, utcnow(), cid],
            )

    def set_summary(self, cid: str, summary: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE conversations SET summary = ? WHERE conversation_id = ?",
                [summary, cid],
            )

    def delete_conversation(self, cid: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "DELETE FROM conversations WHERE conversation_id = ?", [cid]
            )

    # ── Messages ───────────────────────────────────────────────────────

    def append_message(self, cid: str, message: dict) -> None:
        now = utcnow()
        tool_renders_json = json.dumps(message.get("tool_renders", []), default=str)
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO messages "
                "(message_id, conversation_id, role, content, sql_executed, tool_renders, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    message["message_id"],
                    cid,
                    message["role"],
                    message.get("content", ""),
                    message.get("sql_executed"),
                    tool_renders_json,
                    now,
                ],
            )
            conn.execute(
                "UPDATE conversations SET updated_at = ? WHERE conversation_id = ?",
                [now, cid],
            )
        logger.debug("Appended %s message %s to conv %s", message["role"], message["message_id"], cid)

    def get_messages(self, cid: str) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
                [cid],
            ).fetchall()
        result = []
        for r in rows:
            m = dict(r)
            m["tool_renders"] = json.loads(m["tool_renders"]) if m["tool_renders"] else []
            result.append(m)
        return result
