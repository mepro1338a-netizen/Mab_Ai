import sqlite3
import secrets
from datetime import datetime, timedelta
import bcrypt

from config import DB_PATH, PLANS


def now():
    return datetime.utcnow().isoformat()


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_dicts(rows):
    return [dict(row) for row in rows]


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
        is_banned INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        last_login TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        category TEXT,
        subject TEXT,
        message TEXT,
        status TEXT DEFAULT 'open',
        priority TEXT DEFAULT 'normal',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        tool TEXT,
        prompt TEXT,
        tokens_used INTEGER DEFAULT 0,
        cost_tokens INTEGER DEFAULT 0,
        api_provider TEXT,
        status TEXT,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor TEXT,
        action TEXT,
        target TEXT,
        details TEXT,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS redeem_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        code_type TEXT,
        plan TEXT,
        tokens INTEGER DEFAULT 0,
        max_uses INTEGER DEFAULT 1,
        used_count INTEGER DEFAULT 0,
        created_by TEXT,
        expires_at TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        plan TEXT,
        amount INTEGER DEFAULT 0,
        stripe_session_id TEXT,
        payment_status TEXT,
        status TEXT,
        created_at TEXT NOT NULL
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
            username, email, password_hash, plan, tokens,
            role, admin_level, is_banned, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            email,
            password_hash,
            "free",
            PLANS["free"]["tokens"],
            "user",
            0,
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

    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()

    if not user:
        conn.close()
        return False, "User nicht gefunden.", None

    if user["is_banned"]:
        conn.close()
        return False, "Account gesperrt.", None

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

    cur.execute("UPDATE users SET last_login = ? WHERE username = ?", (now(), username))
    conn.commit()

    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    updated_user = cur.fetchone()

    conn.close()
    return True, "Login erfolgreich.", row_to_dict(updated_user)


def get_user(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username.strip().lower(),))
    user = cur.fetchone()
    conn.close()
    return row_to_dict(user)


def list_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows_to_dicts(rows)


def update_tokens(username, tokens):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET tokens = ? WHERE username = ?",
        (int(tokens), username.strip().lower())
    )
    conn.commit()
    conn.close()


def spend_tokens(username, amount):
    user = get_user(username)

    if not user:
        return False, "User nicht gefunden."

    if int(user["tokens"]) < int(amount):
        return False, "Nicht genug Tokens."

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET tokens = tokens - ? WHERE username = ?",
        (int(amount), username.strip().lower())
    )
    conn.commit()
    conn.close()

    return True, "Tokens abgezogen."


def set_plan(username, plan):
    tokens = PLANS.get(plan, PLANS["free"])["tokens"]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET plan = ?, tokens = ? WHERE username = ?",
        (plan, int(tokens), username.strip().lower())
    )
    conn.commit()
    conn.close()


def set_role(username, role, admin_level=0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET role = ?, admin_level = ? WHERE username = ?",
        (role, int(admin_level), username.strip().lower())
    )
    conn.commit()
    conn.close()


def ban_user(username, banned=True):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET is_banned = ? WHERE username = ?",
        (1 if banned else 0, username.strip().lower())
    )
    conn.commit()
    conn.close()


def delete_user(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username = ?", (username.strip().lower(),))
    conn.commit()
    conn.close()
    return True


def create_support_message(username, email, category, subject, message):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO support_tickets (
        username, email, category, subject, message,
        status, priority, created_at, updated_at
    )
    VALUES (?, ?, ?, ?, ?, 'open', 'normal', ?, ?)
    """, (
        username,
        email,
        category,
        subject,
        message,
        now(),
        now()
    ))

    conn.commit()
    conn.close()
    return True, "Ticket erstellt."


def list_support_messages(status_filter="all"):
    conn = get_connection()
    cur = conn.cursor()

    if status_filter == "all":
        cur.execute("SELECT * FROM support_tickets ORDER BY id DESC")
    else:
        cur.execute(
            "SELECT * FROM support_tickets WHERE status = ? ORDER BY id DESC",
            (status_filter,)
        )

    rows = cur.fetchall()
    conn.close()
    return rows_to_dicts(rows)


def support_counts():
    conn = get_connection()
    cur = conn.cursor()

    total = cur.execute("SELECT COUNT(*) AS c FROM support_tickets").fetchone()["c"]
    open_count = cur.execute(
        "SELECT COUNT(*) AS c FROM support_tickets WHERE status='open'"
    ).fetchone()["c"]
    closed_count = cur.execute(
        "SELECT COUNT(*) AS c FROM support_tickets WHERE status='closed'"
    ).fetchone()["c"]

    conn.close()

    return {
        "total": total,
        "open": open_count,
        "closed": closed_count,
        "unread": open_count,
    }


def set_support_status(ticket_id, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE support_tickets SET status = ?, updated_at = ? WHERE id = ?",
        (status, now(), int(ticket_id))
    )
    conn.commit()
    conn.close()


def delete_support_message(ticket_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM support_tickets WHERE id = ?", (int(ticket_id),))
    conn.commit()
    conn.close()


def create_redeem_code(code_type, value="", tokens=0, plan="", max_uses=1, created_by="", days_valid=30):
    code = secrets.token_hex(4).upper()
    expires_at = (datetime.utcnow() + timedelta(days=int(days_valid))).isoformat()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO redeem_codes (
        code, code_type, plan, tokens, max_uses,
        used_count, created_by, expires_at, is_active, created_at
    )
    VALUES (?, ?, ?, ?, ?, 0, ?, ?, 1, ?)
    """, (
        code,
        code_type,
        plan,
        int(tokens or 0),
        int(max_uses or 1),
        created_by,
        expires_at,
        now(),
    ))

    conn.commit()
    conn.close()

    return code


def list_codes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM redeem_codes ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows_to_dicts(rows)


def redeem_code(username, code):
    code = code.strip().upper()
    username = username.strip().lower()

    conn = get_connection()
    cur = conn.cursor()

    item = cur.execute(
        "SELECT * FROM redeem_codes WHERE code = ? AND is_active = 1",
        (code,)
    ).fetchone()

    if not item:
        conn.close()
        return False, "Code ungültig."

    if int(item["used_count"]) >= int(item["max_uses"]):
        conn.close()
        return False, "Code wurde bereits zu oft genutzt."

    if item["expires_at"] and datetime.fromisoformat(item["expires_at"]) < datetime.utcnow():
        conn.close()
        return False, "Code ist abgelaufen."

    if item["tokens"]:
        cur.execute(
            "UPDATE users SET tokens = tokens + ? WHERE username = ?",
            (int(item["tokens"]), username)
        )

    if item["plan"]:
        cur.execute(
            "UPDATE users SET plan = ? WHERE username = ?",
            (item["plan"], username)
        )

    cur.execute(
        "UPDATE redeem_codes SET used_count = used_count + 1 WHERE code = ?",
        (code,)
    )

    conn.commit()
    conn.close()

    return True, "Code eingelöst."


def save_usage(username, tool, prompt, tokens_used=0, cost_tokens=0, api_provider="", status="success"):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO usage_logs (
        username, tool, prompt, tokens_used,
        cost_tokens, api_provider, status, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        username,
        tool,
        prompt,
        int(tokens_used or 0),
        int(cost_tokens or 0),
        api_provider,
        status,
        now()
    ))

    conn.commit()
    conn.close()


def list_usage(username=None):
    conn = get_connection()
    cur = conn.cursor()

    if username:
        cur.execute(
            "SELECT * FROM usage_logs WHERE username = ? ORDER BY id DESC",
            (username,)
        )
    else:
        cur.execute("SELECT * FROM usage_logs ORDER BY id DESC")

    rows = cur.fetchall()
    conn.close()
    return rows_to_dicts(rows)


def add_audit_log(actor, action, target="", details=""):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO audit_logs (
        actor, action, target, details, created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        actor,
        action,
        target,
        details,
        now()
    ))

    conn.commit()
    conn.close()


def list_audit_logs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM audit_logs ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows_to_dicts(rows)


def record_purchase(username, plan, amount, session_id, payment_status, status):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO payments (
        username, plan, amount, stripe_session_id,
        payment_status, status, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        username,
        plan,
        int(amount or 0),
        session_id,
        payment_status,
        status,
        now()
    ))

    conn.commit()
    conn.close()


def list_purchases(username=None):
    conn = get_connection()
    cur = conn.cursor()

    if username:
        cur.execute(
            "SELECT * FROM payments WHERE username = ? ORDER BY id DESC",
            (username,)
        )
    else:
        cur.execute("SELECT * FROM payments ORDER BY id DESC")

    rows = cur.fetchall()
    conn.close()
    return rows_to_dicts(rows)

def make_admin(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET role = 'admin', admin_level = 999
    WHERE username = ?
    """, (username.strip().lower(),))

    conn.commit()
    conn.close()

init_db()
make_admin("mepro1337")