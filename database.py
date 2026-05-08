# database.py

import sqlite3
from datetime import datetime
import bcrypt

from config import DB_PATH, PLANS


def now():
    return datetime.utcnow().isoformat()


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row):
    return dict(row) if row else None


def validate_password(password):
    if not password:
        return False, "Bitte Passwort eingeben."

    if len(password) < 6:
        return False, "Passwort muss mindestens 6 Zeichen haben."

    if len(password.encode("utf-8")) > 72:
        return False, "Passwort maximal 72 Zeichen."

    return True, ""

def list_users():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, username, email, plan, tokens, role, admin_level, created_at, last_login
    FROM users
    ORDER BY id DESC
    """)

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def set_plan(username, plan):
    conn = get_connection()
    cur = conn.cursor()

    tokens = PLANS.get(plan, PLANS["free"])["tokens"]

    cur.execute("""
    UPDATE users
    SET plan = ?, tokens = ?
    WHERE username = ?
    """, (plan, tokens, username.strip().lower()))

    conn.commit()
    conn.close()


def set_role(username, role, admin_level=0):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET role = ?, admin_level = ?
    WHERE username = ?
    """, (role, int(admin_level), username.strip().lower()))

    conn.commit()
    conn.close()


def ban_user(username, banned=True):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET is_banned = ?
    WHERE username = ?
    """, (1 if banned else 0, username.strip().lower()))

    conn.commit()
    conn.close()


def delete_user(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE username = ?", (username.strip().lower(),))

    conn.commit()
    conn.close()
    return True

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        plan TEXT NOT NULL DEFAULT 'free',
        tokens INTEGER NOT NULL DEFAULT 0,
        role TEXT NOT NULL DEFAULT 'user',
        admin_level INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        last_login TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_user(username, email, password):
    username = username.strip().lower()
    email = email.strip().lower()

    valid, msg = validate_password(password)

    if not valid:
        return False, msg

    conn = get_connection()
    cur = conn.cursor()

    try:
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cur.execute("""
        INSERT INTO users (
            username,
            email,
            password_hash,
            plan,
            tokens,
            role,
            admin_level,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            email,
            password_hash,
            "free",
            PLANS["free"]["tokens"],
            "user",
            0,
            now()
        ))

        conn.commit()

        return True, "Account erstellt."

    except sqlite3.IntegrityError:
        return False, "Username oder Email existiert bereits."

    except Exception as e:
        return False, f"Datenbankfehler: {e}"

    finally:
        conn.close()


def verify_login(username, password):
    username = username.strip().lower()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    user = cur.fetchone()

    if not user:
        conn.close()
        return False, "User nicht gefunden.", None

    try:
        valid = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

    except Exception:
        valid = False

    if not valid:
        conn.close()
        return False, "Falsches Passwort.", None

    cur.execute("""
    UPDATE users
    SET last_login = ?
    WHERE username = ?
    """, (now(), username))

    conn.commit()

    cur.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    updated_user = cur.fetchone()

    conn.close()

    return True, "Login erfolgreich.", row_to_dict(updated_user)


def get_user(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM users
    WHERE username = ?
    """, (username.strip().lower(),))

    user = cur.fetchone()

    conn.close()

    return row_to_dict(user)


def spend_tokens(username, amount):
    user = get_user(username)

    if not user:
        return False, "User nicht gefunden."

    if user["tokens"] < amount:
        return False, "Nicht genug Tokens."

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET tokens = tokens - ?
    WHERE username = ?
    """, (amount, username.strip().lower()))

    conn.commit()
    conn.close()

    return True, "Tokens abgezogen."


init_db()