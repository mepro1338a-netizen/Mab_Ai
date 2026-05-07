import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "mabai.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        plan TEXT DEFAULT 'free',
        tokens INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        ip_address TEXT,
        login_time TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS generations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        tool TEXT,
        prompt TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS stripe_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        customer_id TEXT,
        subscription_id TEXT,
        plan TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_user(username, email, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO users (
            username,
            email,
            password,
            plan,
            tokens,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            username,
            email,
            password,
            "free",
            0,
            datetime.utcnow().isoformat()
        ))

        conn.commit()
        conn.close()
        return True

    except Exception:
        conn.close()
        return False


def get_user(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM users
    WHERE username = ?
    """, (username,))

    user = cur.fetchone()

    conn.close()
    return user


def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM users
    WHERE username = ?
    AND password = ?
    """, (
        username,
        password
    ))

    user = cur.fetchone()

    conn.close()
    return user


def update_user_plan(username, plan):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET plan = ?
    WHERE username = ?
    """, (
        plan,
        username
    ))

    conn.commit()
    conn.close()


def update_tokens(username, tokens):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET tokens = ?
    WHERE username = ?
    """, (
        tokens,
        username
    ))

    conn.commit()
    conn.close()


def add_tokens(username, amount):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET tokens = tokens + ?
    WHERE username = ?
    """, (
        amount,
        username
    ))

    conn.commit()
    conn.close()


def remove_tokens(username, amount):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET tokens = MAX(tokens - ?, 0)
    WHERE username = ?
    """, (
        amount,
        username
    ))

    conn.commit()
    conn.close()


def save_generation(username, tool, prompt):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO generations (
        username,
        tool,
        prompt,
        created_at
    )
    VALUES (?, ?, ?, ?)
    """, (
        username,
        tool,
        prompt,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


def get_generations(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM generations
    WHERE username = ?
    ORDER BY id DESC
    """, (username,))

    rows = cur.fetchall()

    conn.close()
    return rows


def save_login_log(username, ip_address):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO login_logs (
        username,
        ip_address,
        login_time
    )
    VALUES (?, ?, ?)
    """, (
        username,
        ip_address,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


def get_login_logs(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM login_logs
    WHERE username = ?
    ORDER BY id DESC
    """, (username,))

    rows = cur.fetchall()

    conn.close()
    return rows


def save_payment(
    username,
    customer_id,
    subscription_id,
    plan,
    status
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO stripe_payments (
        username,
        customer_id,
        subscription_id,
        plan,
        status,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        username,
        customer_id,
        subscription_id,
        plan,
        status,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


def get_payments(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM stripe_payments
    WHERE username = ?
    ORDER BY id DESC
    """, (username,))

    rows = cur.fetchall()

    conn.close()
    return rows


def delete_user(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM users
    WHERE username = ?
    """, (username,))

    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM users
    ORDER BY id DESC
    """)

    rows = cur.fetchall()

    conn.close()
    return rows


init_db()