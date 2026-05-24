"""Global memory and automation unlock flags."""
from db.core import get_connection, normalize_username, now, rows_to_dicts
from db.users import get_user

def ensure_global_memory_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS global_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        memory_type TEXT,
        content TEXT,
        importance INTEGER DEFAULT 1,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_global_memory(username, memory_type, content, importance=1):
    ensure_global_memory_tables()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO global_memory (
        username,
        memory_type,
        content,
        importance,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        normalize_username(username),
        memory_type,
        content,
        int(importance),
        now(),
    ))

    conn.commit()
    conn.close()


def list_global_memory(username, limit=100):
    ensure_global_memory_tables()

    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("""
    SELECT * FROM global_memory
    WHERE username = ?
    ORDER BY importance DESC, id DESC
    LIMIT ?
    """, (
        normalize_username(username),
        int(limit),
    )).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def search_global_memory(username, query, limit=10):
    ensure_global_memory_tables()

    conn = get_connection()
    cur = conn.cursor()

    q = f"%{(query or '').lower()}%"

    rows = cur.execute("""
    SELECT * FROM global_memory
    WHERE username = ?
    AND LOWER(content) LIKE ?
    ORDER BY importance DESC, id DESC
    LIMIT ?
    """, (
        normalize_username(username),
        q,
        int(limit),
    )).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def unlock_automation(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET automation_unlocked = 1
    WHERE username = ?
    """, (
        normalize_username(username),
    ))

    conn.commit()
    conn.close()


def has_automation_access(username):
    user = get_user(username)

    if not user:
        return False

    return int(user.get("automation_unlocked") or 0) == 1

