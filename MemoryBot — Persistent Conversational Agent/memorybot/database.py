"""
SQLite layer — raw message persistence.

Think of this as the diary: every message goes in, nothing gets lost.
The vector store (Pinecone) is the brain that recalls relevant memories;
SQLite is the full, faithful record.

Tables
------
users    (id, name, created_at)
messages (id, user_id, role, content, timestamp, summarized)
"""

import sqlite3
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # safe concurrent reads
    return conn


# ---------------------------------------------------------------------------
# Schema init
# ---------------------------------------------------------------------------

def init_db(db_path: str = "memorybot.db") -> sqlite3.Connection:
    """Create tables if they don't exist. Return the open connection."""
    conn = _connect(db_path)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL UNIQUE,
            created_at TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            role        TEXT    NOT NULL CHECK(role IN ('human', 'ai')),
            content     TEXT    NOT NULL,
            timestamp   TEXT    NOT NULL,
            summarized  INTEGER NOT NULL DEFAULT 0   -- 0=no, 1=yes
        );

        CREATE INDEX IF NOT EXISTS idx_messages_user
            ON messages (user_id, timestamp);
        """
    )
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------

def get_or_create_user(conn: sqlite3.Connection, name: str) -> int:
    """Return the user's integer ID, creating the row if needed."""
    row = conn.execute(
        "SELECT id FROM users WHERE name = ?", (name,)
    ).fetchone()
    if row:
        return row["id"]
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO users (name, created_at) VALUES (?, ?)", (name, now)
    )
    conn.commit()
    return cur.lastrowid


# ---------------------------------------------------------------------------
# Message helpers
# ---------------------------------------------------------------------------

def save_message(
    conn: sqlite3.Connection,
    user_id: int,
    role: str,
    content: str,
) -> None:
    """Persist a single chat message."""
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO messages (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, role, content, now),
    )
    conn.commit()


def load_recent_messages(
    conn: sqlite3.Connection,
    user_id: int,
    limit: int = 20,
) -> list[dict]:
    """Return the most recent `limit` messages for a user, oldest first."""
    rows = conn.execute(
        """
        SELECT role, content, timestamp
          FROM messages
         WHERE user_id = ?
         ORDER BY id DESC
         LIMIT ?
        """,
        (user_id, limit),
    ).fetchall()
    return [dict(r) for r in reversed(rows)]


def get_unsummarized_messages(
    conn: sqlite3.Connection,
    user_id: int,
) -> list[dict]:
    """Return messages not yet included in a Pinecone summary."""
    rows = conn.execute(
        """
        SELECT id, role, content
          FROM messages
         WHERE user_id = ?
           AND summarized = 0
         ORDER BY id ASC
        """,
        (user_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def mark_messages_summarized(
    conn: sqlite3.Connection,
    message_ids: list[int],
) -> None:
    """Flag rows as summarized so they aren't re-processed."""
    if not message_ids:
        return
    placeholders = ",".join("?" * len(message_ids))
    conn.execute(
        f"UPDATE messages SET summarized = 1 WHERE id IN ({placeholders})",
        message_ids,
    )
    conn.commit()


def count_unsummarized(conn: sqlite3.Connection, user_id: int) -> int:
    """How many un-summarized USER messages does this user have?
    Only counts human turns — AI replies are not included in the threshold."""
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM messages WHERE user_id = ? AND summarized = 0 AND role = 'human'",
        (user_id,),
    ).fetchone()
    return row["n"]


def get_stored_facts(conn: sqlite3.Connection, user_id: int) -> list[str]:
    """
    Pull the most recent AI turns to display as 'what I remember'.
    In a richer implementation this would be a dedicated facts table;
    here we surface the last few assistant statements as a proxy.
    """
    rows = conn.execute(
        """
        SELECT content FROM messages
         WHERE user_id = ? AND role = 'ai'
         ORDER BY id DESC
         LIMIT 5
        """,
        (user_id,),
    ).fetchall()
    return [r["content"] for r in reversed(rows)]
