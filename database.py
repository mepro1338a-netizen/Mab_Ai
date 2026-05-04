import sqlite3
from datetime import datetime

DB_NAME = "app.db"


def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # USERS
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

    # SUPPORT
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

    # PURCHASES
    c.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        plan TEXT,
        stripe_session TEXT,
        status TEXT DEFAULT 'created',
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- USERS ----------------

def list_users():
    conn = get_conn()
    c = conn.cursor()
    try:
        users = c.execute("SELECT * FROM users").fetchall()
    except:
        users = []
    conn.close()
    return users


def get_user(username):
    conn = get_conn()
    c = conn.cursor()
    user = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return user


# ---------------- SUPPORT ----------------

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
    return True, "ok"


def list_support_messages():
    conn = get_conn()
    c = conn.cursor()
    rows = c.execute("SELECT * FROM support_messages ORDER BY created_at DESC").fetchall()
    conn.close()
    return rows


def support_counts():
    conn = get_conn()
    c = conn.cursor()

    try:
        total = c.execute("SELECT COUNT(*) FROM support_messages").fetchone()[0]
    except:
        total = 0

    conn.close()
    return {"total": total}


# ---------------- PURCHASES ----------------

def list_purchases(username=None):
    conn = get_conn()
    c = conn.cursor()

    if username:
        rows = c.execute(
            "SELECT * FROM purchases WHERE username=? ORDER BY created_at DESC",
            (username,)
        ).fetchall()
    else:
        rows = c.execute(
            "SELECT * FROM purchases ORDER BY created_at DESC"
        ).fetchall()

    conn.close()
    return rows

def set_plan(username, plan):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET plan=? WHERE username=?", (plan, username))
    conn.commit()
    conn.close()


def update_tokens(username, tokens):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET tokens = COALESCE(tokens, 0) + ? WHERE username=?", (tokens, username))
    conn.commit()
    conn.close()


def set_role(username, role):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET role=? WHERE username=?", (role, username))
    conn.commit()
    conn.close()


def delete_user(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()
    return True


def create_user(username, email, password, role="user", plan="free"):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("""
        INSERT INTO users (username, email, password, plan, tokens, role)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (username.strip().lower(), email, password, plan, 0, role))
        conn.commit()
        return True, "User created."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def add_memory(username, key, value):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        key TEXT,
        value TEXT,
        created_at TEXT
    )
    """)
    c.execute(
        "INSERT INTO memories (username, key, value, created_at) VALUES (?, ?, ?, ?)",
        (username, key, value, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def load_memory(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        key TEXT,
        value TEXT,
        created_at TEXT
    )
    """)
    rows = c.execute(
        "SELECT key, value FROM memories WHERE username=? ORDER BY id DESC",
        (username,)
    ).fetchall()
    conn.close()
    return {k: v for k, v in rows}


def create_redeem_code(code_type, value, tokens, plan, max_uses, created_by, days_valid):
    import secrets
    code = secrets.token_hex(4).upper()

    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS redeem_codes (
        code TEXT PRIMARY KEY,
        code_type TEXT,
        value TEXT,
        tokens INTEGER,
        plan TEXT,
        max_uses INTEGER,
        used INTEGER DEFAULT 0,
        created_by TEXT,
        created_at TEXT,
        expires_at TEXT,
        active INTEGER DEFAULT 1
    )
    """)
    c.execute("""
    INSERT INTO redeem_codes
    (code, code_type, value, tokens, plan, max_uses, used, created_by, created_at, expires_at, active)
    VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, 1)
    """, (
        code, code_type, value, int(tokens), plan, int(max_uses),
        created_by, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()
    return code


def list_codes():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS redeem_codes (
        code TEXT PRIMARY KEY,
        code_type TEXT,
        value TEXT,
        tokens INTEGER,
        plan TEXT,
        max_uses INTEGER,
        used INTEGER DEFAULT 0,
        created_by TEXT,
        created_at TEXT,
        expires_at TEXT,
        active INTEGER DEFAULT 1
    )
    """)
    rows = c.execute("SELECT * FROM redeem_codes ORDER BY created_at DESC").fetchall()
    conn.close()
    return rows


def redeem_code(username, code):
    conn = get_conn()
    c = conn.cursor()
    row = c.execute("SELECT * FROM redeem_codes WHERE code=? AND active=1", (code,)).fetchone()

    if not row:
        conn.close()
        return False, "Invalid code."

    code_value = row
    tokens = code_value[3] or 0
    plan = code_value[4]

    if tokens:
        c.execute("UPDATE users SET tokens = COALESCE(tokens, 0) + ? WHERE username=?", (tokens, username))

    if plan:
        c.execute("UPDATE users SET plan=? WHERE username=?", (plan, username))

    c.execute("UPDATE redeem_codes SET used = used + 1 WHERE code=?", (code,))
    conn.commit()
    conn.close()
    return True, "Code redeemed."


def set_support_read(message_id, value):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE support_messages SET is_read=? WHERE id=?", (value, message_id))
    conn.commit()
    conn.close()


def set_support_status(message_id, status):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE support_messages SET status=? WHERE id=?", (status, message_id))
    conn.commit()
    conn.close()


def delete_support_message(message_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM support_messages WHERE id=?", (message_id,))
    conn.commit()
    conn.close()


def list_admin_chat(limit=80):
    return []


def add_admin_chat(username, role, message):
    return True, "Message sent."