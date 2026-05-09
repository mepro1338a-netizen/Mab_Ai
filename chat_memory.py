import json
from datetime import datetime

from db_manager import db


def init_chat_memory():
    db.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)


def save_chat_message(username, role, content):
    db.execute(
        """
        INSERT INTO chat_messages (username, role, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            username,
            role,
            content,
            datetime.utcnow().isoformat(),
        ),
    )


def load_chat_history(username, limit=30):
    rows = db.execute(
        """
        SELECT role, content
        FROM chat_messages
        WHERE username = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (username, int(limit)),
        fetchall=True,
    )

    messages = [{"role": row["role"], "content": row["content"]} for row in rows]
    messages.reverse()

    return [
        {
            "role": "system",
            "content": "Du bist Mabyte, ein hilfreicher deutschsprachiger AI-Assistent. Antworte klar, direkt und praxisnah.",
        }
    ] + messages


def clear_chat_history(username):
    db.execute(
        """
        DELETE FROM chat_messages
        WHERE username = ?
        """,
        (username,),
    )
