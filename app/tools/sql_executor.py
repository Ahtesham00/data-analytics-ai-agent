import logging
import os
import sqlite3

logger = logging.getLogger(__name__)

SQLITE_PATH = os.environ.get("SQLITE_PATH", "./data/analytics.db")

_FORBIDDEN = {"INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "ATTACH", "PRAGMA"}


def execute_sql(sql: str, description: str = "") -> dict:
    upper = sql.strip().upper()
    for keyword in _FORBIDDEN:
        if keyword in upper.split() or upper.startswith(keyword):
            logger.warning("Blocked forbidden SQL keyword '%s' in query: %.100s", keyword, sql)
            return {
                "success": False,
                "error": f"'{keyword}' statements are not permitted. Only SELECT is allowed.",
            }

    db_path = os.environ.get("SQLITE_PATH", SQLITE_PATH)
    logger.info("Executing SQL (%s): %.200s", description or "no description", sql)

    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.close()
        logger.info("SQL returned %d rows, columns: %s", len(rows), cols)
        return {"success": True, "row_count": len(rows), "columns": cols, "rows": rows}
    except sqlite3.Error as e:
        logger.error("SQL error: %s | query: %.200s", e, sql)
        return {"success": False, "error": str(e)}
