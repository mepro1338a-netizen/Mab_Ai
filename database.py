import sqlite3
from datetime import datetime

DB_NAME = "app.db"


def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # USERS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        email TEXT,
        password TEXT,
        plan TEXT DEFAULT 'free',
        tokens INTEGER DEFAULT 0,
        role TEXT DEFAULT 'user'
    )
    """)

    # SUPPORT MESSAGES TABLE (DEIN FEHLER WAR HIER)
    c.execute("""
    CREATE TABLE IF NOT EXISTS support_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        category TEXT,
        subject TEXT,
        message TEXT,
        status TEXT DEFAULT 'open',
        is_read INTEGER DEFAULT 0,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------
# SUPPORT SYSTEM
# -------------------------------------------------

def create_support_message(username, email, category, subject, message):
    conn = get_conn()
    c = conn.cursor()

    now = datetime.utcnow().isoformat()

    c.execute("""
    INSERT INTO support_messages
    (username, email, category, subject, message, status, is_read, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, 'open', 0, ?, ?)
    """, (username, email, category, subject, message, now, now))

    conn.commit()
    conn.close()
    return True, "Message sent"


def list_support_messages(status_filter="all"):
    conn = get_conn()
    c = conn.cursor()

    if status_filter == "all":
        rows = c.execute("""
        SELECT * FROM support_messages
        ORDER BY created_at DESC
        """).fetchall()
    else:
        rows = c.execute("""
        SELECT * FROM support_messages
        WHERE status=?
        ORDER BY created_at DESC
        """, (status_filter,)).fetchall()

    conn.close()
    return rows


def support_counts():
    conn = get_conn()
    c = conn.cursor()

    try:
        total = c.execute("SELECT COUNT(*) FROM support_messages").fetchone()[0]
        unread = c.execute("SELECT COUNT(*) FROM support_messages WHERE is_read=0").fetchone()[0]
        open_ = c.execute("SELECT COUNT(*) FROM support_messages WHERE status='open'").fetchone()[0]
        closed = c.execute("SELECT COUNT(*) FROM support_messages WHERE status='closed'").fetchone()[0]
    except:
        total = unread = open_ = closed = 0

    conn.close()

    return {
        "total": total,
        "unread": unread,
        "open": open_,
        "closed": closed
    }


def set_support_read(message_id, value):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    UPDATE support_messages
    SET is_read=?, updated_at=?
    WHERE id=?
    """, (value, datetime.utcnow().isoformat(), message_id))

    conn.commit()
    conn.close()


def set_support_status(message_id, status):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    UPDATE support_messages
    SET status=?, updated_at=?
    WHERE id=?
    """, (status, datetime.utcnow().isoformat(), message_id))

    conn.commit()
    conn.close()


def delete_support_message(message_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("DELETE FROM support_messages WHERE id=?", (message_id,))
    conn.commit()
    conn.close()

# -------------------------------------------------
# USERS (FIX für ImportError)
# -------------------------------------------------

def list_users():
    conn = get_conn()
    c = conn.cursor()

    try:
        users = c.execute("SELECT * FROM users").fetchall()
    except:
        users = []

    conn.close()
    return users