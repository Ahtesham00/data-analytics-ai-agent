import csv
import os
import sqlite3
import sys
from datetime import datetime

# Allow running from any directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv()

SQLITE_PATH = os.environ.get("SQLITE_PATH", "./data/analytics.db")
CSV_PATH    = os.environ.get("CSV_PATH",    "./data/superstore.csv")


def utcnow() -> str:
    return datetime.utcnow().isoformat() + "Z"


def normalise_date(raw: str) -> str:
    for fmt in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw


def seed():
    db_dir = os.path.dirname(os.path.abspath(SQLITE_PATH))
    os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(SQLITE_PATH)
    cur  = conn.cursor()

    # ── Analytics table ───────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS superstore (
            row_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id      TEXT NOT NULL,
            order_date    TEXT NOT NULL,
            ship_date     TEXT NOT NULL,
            ship_mode     TEXT,
            customer_id   TEXT,
            customer_name TEXT,
            segment       TEXT,
            city          TEXT,
            state         TEXT,
            region        TEXT,
            category      TEXT,
            sub_category  TEXT,
            product_name  TEXT,
            sales         REAL,
            quantity      INTEGER,
            discount      REAL,
            profit        REAL
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ss_order_date ON superstore (order_date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ss_region     ON superstore (region)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ss_category   ON superstore (category)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ss_segment    ON superstore (segment)")

    # ── Chat tables ───────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            title           TEXT NOT NULL DEFAULT 'New Conversation',
            provider        TEXT NOT NULL DEFAULT 'anthropic',
            created_at      TEXT NOT NULL,
            updated_at      TEXT NOT NULL,
            summary         TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id      TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role            TEXT NOT NULL,
            content         TEXT NOT NULL DEFAULT '',
            sql_executed    TEXT,
            tool_renders    TEXT,
            created_at      TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                ON DELETE CASCADE
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_msg_conv_time ON messages (conversation_id, created_at ASC)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_conv_updated  ON conversations (updated_at DESC)")

    # ── WAL mode ──────────────────────────────────────────────────────
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    # ── Seed analytics data if empty ──────────────────────────────────
    cur.execute("SELECT COUNT(*) FROM superstore")
    count = cur.fetchone()[0]

    if count > 0:
        print(f"[seed] superstore already has {count} rows — skipping CSV import.")
        conn.commit()
        conn.close()
        return

    if not os.path.exists(CSV_PATH):
        print(f"[seed] WARNING: CSV not found at {CSV_PATH}. Superstore table will be empty.")
        conn.commit()
        conn.close()
        return

    print(f"[seed] Importing {CSV_PATH} …")
    rows = []
    with open(CSV_PATH, newline="", encoding="cp1252") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append((
                row["Order ID"],
                normalise_date(row["Order Date"]),
                normalise_date(row["Ship Date"]),
                row.get("Ship Mode", ""),
                row.get("Customer ID", ""),
                row.get("Customer Name", ""),
                row.get("Segment", ""),
                row.get("City", ""),
                row.get("State", ""),
                row.get("Region", ""),
                row.get("Category", ""),
                row.get("Sub-Category", ""),
                row.get("Product Name", ""),
                float(row.get("Sales", 0) or 0),
                int(float(row.get("Quantity", 0) or 0)),
                float(row.get("Discount", 0) or 0),
                float(row.get("Profit", 0) or 0),
            ))

    cur.executemany("""
        INSERT INTO superstore
        (order_id, order_date, ship_date, ship_mode, customer_id, customer_name,
         segment, city, state, region, category, sub_category, product_name,
         sales, quantity, discount, profit)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, rows)

    conn.commit()
    print(f"[seed] Inserted {len(rows)} rows into superstore.")
    conn.close()
    print("[seed] Done.")


if __name__ == "__main__":
    seed()
