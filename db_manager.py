import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        plan TEXT DEFAULT 'free',
        tokens INTEGER DEFAULT 100,
        role TEXT DEFAULT 'user',
        admin_level INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS redeem_codes (
        id SERIAL PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        tokens INTEGER DEFAULT 0,
        plan TEXT,
        max_uses INTEGER DEFAULT 1,
        used_count INTEGER DEFAULT 0,
        active BOOLEAN DEFAULT TRUE
    )
    """)

    conn.commit()
    cur.close()
    conn.close()


def create_user(username, email, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO users (
        username,
        email,
        password
    )
    VALUES (%s, %s, %s)
    """, (username, email, password))

    conn.commit()
    cur.close()
    conn.close()

    return True


def get_user(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=%s",
        (username,)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    return user


def update_tokens(username, tokens):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET tokens=%s WHERE username=%s",
        (tokens, username)
    )

    conn.commit()

    cur.close()
    conn.close()


init_db()

def create_redeem_code(code, tokens=0, plan=None, max_uses=1):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO redeem_codes (
        code,
        tokens,
        plan,
        max_uses
    )
    VALUES (%s, %s, %s, %s)
    """, (code, tokens, plan, max_uses))

    conn.commit()

    cur.close()
    conn.close()


def redeem_code(username, code):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM redeem_codes WHERE code=%s AND active=TRUE",
        (code,)
    )

    redeem = cur.fetchone()

    if not redeem:
        cur.close()
        conn.close()
        return False, "Code ungültig."

    if redeem["used_count"] >= redeem["max_uses"]:
        cur.close()
        conn.close()
        return False, "Code bereits verbraucht."

    cur.execute(
        "SELECT * FROM users WHERE username=%s",
        (username,)
    )

    user = cur.fetchone()

    new_tokens = user["tokens"] + redeem["tokens"]

    new_plan = user["plan"]

    if redeem["plan"]:
        new_plan = redeem["plan"]

    cur.execute("""
    UPDATE users
    SET tokens=%s, plan=%s
    WHERE username=%s
    """, (new_tokens, new_plan, username))

    cur.execute("""
    UPDATE redeem_codes
    SET used_count = used_count + 1
    WHERE code=%s
    """, (code,))

    conn.commit()

    cur.close()
    conn.close()

    return True, f"{redeem['tokens']} Tokens erhalten."