import sqlite3
import secrets
from datetime import datetime, timedelta
from passlib.hash import bcrypt

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
        return False, "Passwort ist zu lang. Bitte maximal 72 Zeichen verwenden."

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
        is_verified INTEGER NOT NULL DEFAULT 0,
        is_banned INTEGER NOT NULL DEFAULT 0,
        stripe_customer_id TEXT,
        created_at TEXT NOT NULL,
        last_login TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        tool TEXT NOT NULL,
        prompt TEXT,
        tokens_used INTEGER DEFAULT 0,
        cost_tokens INTEGER DEFAULT 0,
        api_provider TEXT,
        status TEXT,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        category TEXT,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'open',
        priority TEXT DEFAULT 'normal',
        assigned_to TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ticket_replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER NOT NULL,
        username TEXT,
        role TEXT,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS redeem_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
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
    CREATE TABLE IF NOT EXISTS redeem_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        username TEXT,
        redeemed_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        stripe_customer_id TEXT,
        stripe_session_id TEXT,
        stripe_subscription_id TEXT,
        stripe_price_id TEXT,
        plan TEXT,
        amount INTEGER DEFAULT 0,
        currency TEXT DEFAULT 'eur',
        status TEXT,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        stripe_customer_id TEXT,
        stripe_subscription_id TEXT UNIQUE,
        stripe_price_id TEXT,
        plan TEXT,
        status TEXT,
        current_period_start TEXT,
        current_period_end TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor TEXT,
        action TEXT NOT NULL,
        target TEXT,
        details TEXT,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS api_key_refs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT UNIQUE,
        env_name TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def create_user(username, email, password, role="user", plan="free", tokens=None):
    username = (username or "").strip().lower()
    email = (email or "").strip().lower()

    if not username or not email or not password:
        return False, "Bitte alle Felder ausfüllen."

    valid, msg = validate_password(password)
    if not valid:
        return False, msg

    if tokens is None:
        tokens = PLANS.get(plan, PLANS["free"])["tokens"]

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO users (
            username, email, password_hash, plan, tokens, role,
            admin_level, is_verified, is_banned, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0, ?)
        """, (
            username,
            email,
            bcrypt.hash(password),
            plan,
            int(tokens),
            role,
            now(),
        ))

        conn.commit()
        return True, "Account erstellt."

    except sqlite3.IntegrityError:
        return False, "Username oder E-Mail existiert bereits."

    except Exception as e:
        return False, f"Datenbankfehler: {e}"

    finally:
        conn.close()


def verify_login(username, password):
    username = (username or "").strip().lower()

    if not username or not password:
        return False, "Bitte Username und Passwort eingeben.", None

    valid, msg = validate_password(password)
    if not valid:
        return False, msg, None

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
        valid_login = bcrypt.verify(password, user["password_hash"])
    except Exception:
        valid_login = False

    if not valid_login:
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
    cur.execute("SELECT * FROM users WHERE username = ?", ((username or "").strip().lower(),))
    user = cur.fetchone()
    conn.close()
    return row_to_dict(user)


def get_user_by_email(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", ((email or "").strip().lower(),))
    user = cur.fetchone()
    conn.close()
    return row_to_dict(user)


def list_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT id, username, email, plan, tokens, role, admin_level,
           is_verified, is_banned, created_at, last_login
    FROM users
    ORDER BY id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_user_plan(username, plan):
    tokens = PLANS.get(plan, PLANS["free"])["tokens"]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    UPDATE users
    SET plan = ?, tokens = ?
    WHERE username = ?
    """, (plan, int(tokens), username.strip().lower()))
    conn.commit()
    conn.close()


def set_plan(username, plan):
    update_user_plan(username, plan)


def update_tokens(username, tokens):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    UPDATE users
    SET tokens = ?
    WHERE username = ?
    """, (int(tokens), username.strip().lower()))
    conn.commit()
    conn.close()


def add_tokens(username, amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    UPDATE users
    SET tokens = COALESCE(tokens, 0) + ?
    WHERE username = ?
    """, (int(amount), username.strip().lower()))
    conn.commit()
    conn.close()


def remove_tokens(username, amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    UPDATE users
    SET tokens = CASE
        WHEN COALESCE(tokens, 0) - ? < 0 THEN 0
        ELSE COALESCE(tokens, 0) - ?
    END
    WHERE username = ?
    """, (int(amount), int(amount), username.strip().lower()))
    conn.commit()
    conn.close()


def spend_tokens(username, amount):
    user = get_user(username)

    if not user:
        return False, "User nicht gefunden."

    if int(user["tokens"]) < int(amount):
        return False, "Nicht genug Tokens."

    remove_tokens(username, amount)
    return True, "Tokens abgezogen."


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


def create_support_message(username, email, category, subject, message):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO support_tickets (
        username, email, category, subject, message,
        status, priority, created_at, updated_at
    )
    VALUES (?, ?, ?, ?, ?, 'open', 'normal', ?, ?)
    """, (username, email, category, subject, message, now(), now()))

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
    return [dict(row) for row in rows]


def support_counts():
    conn = get_connection()
    cur = conn.cursor()

    total = cur.execute("SELECT COUNT(*) AS c FROM support_tickets").fetchone()["c"]
    open_count = cur.execute("SELECT COUNT(*) AS c FROM support_tickets WHERE status='open'").fetchone()["c"]
    closed_count = cur.execute("SELECT COUNT(*) AS c FROM support_tickets WHERE status='closed'").fetchone()["c"]

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
    cur.execute("""
    UPDATE support_tickets
    SET status = ?, updated_at = ?
    WHERE id = ?
    """, (status, now(), int(ticket_id)))
    conn.commit()
    conn.close()


def assign_support_ticket(ticket_id, admin_username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    UPDATE support_tickets
    SET assigned_to = ?, updated_at = ?
    WHERE id = ?
    """, (admin_username, now(), int(ticket_id)))
    conn.commit()
    conn.close()


def add_ticket_reply(ticket_id, username, role, message):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO ticket_replies (
        ticket_id, username, role, message, created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (int(ticket_id), username, role, message, now()))

    cur.execute("""
    UPDATE support_tickets
    SET updated_at = ?
    WHERE id = ?
    """, (now(), int(ticket_id)))

    conn.commit()
    conn.close()


def list_ticket_replies(ticket_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT * FROM ticket_replies
    WHERE ticket_id = ?
    ORDER BY id ASC
    """, (int(ticket_id),))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_support_message(ticket_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ticket_replies WHERE ticket_id = ?", (int(ticket_id),))
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
    return [dict(row) for row in rows]


def redeem_code(username, code):
    code = code.strip().upper()
    username = username.strip().lower()

    conn = get_connection()
    cur = conn.cursor()

    item = cur.execute("""
    SELECT * FROM redeem_codes
    WHERE code = ? AND is_active = 1
    """, (code,)).fetchone()

    if not item:
        conn.close()
        return False, "Code ungültig."

    if item["used_count"] >= item["max_uses"]:
        conn.close()
        return False, "Code wurde bereits zu oft genutzt."

    if item["expires_at"] and datetime.fromisoformat(item["expires_at"]) < datetime.utcnow():
        conn.close()
        return False, "Code ist abgelaufen."

    if item["tokens"]:
        cur.execute("""
        UPDATE users
        SET tokens = COALESCE(tokens, 0) + ?
        WHERE username = ?
        """, (int(item["tokens"]), username))

    if item["plan"]:
        cur.execute("""
        UPDATE users
        SET plan = ?
        WHERE username = ?
        """, (item["plan"], username))

    cur.execute("""
    UPDATE redeem_codes
    SET used_count = used_count + 1
    WHERE code = ?
    """, (code,))

    cur.execute("""
    INSERT INTO redeem_logs (code, username, redeemed_at)
    VALUES (?, ?, ?)
    """, (code, username, now()))

    conn.commit()
    conn.close()

    return True, "Code eingelöst."


def save_payment(username, email, customer_id, session_id, subscription_id, price_id, plan, amount, currency, status):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO payments (
        username, email, stripe_customer_id, stripe_session_id,
        stripe_subscription_id, stripe_price_id, plan, amount,
        currency, status, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        username,
        email,
        customer_id,
        session_id,
        subscription_id,
        price_id,
        plan,
        int(amount or 0),
        currency,
        status,
        now(),
    ))

    conn.commit()
    conn.close()


def record_purchase(username, plan, amount, session_id, payment_status, status):
    save_payment(
        username=username,
        email="",
        customer_id="",
        session_id=session_id,
        subscription_id="",
        price_id="",
        plan=plan,
        amount=amount,
        currency="eur",
        status=status or payment_status,
    )


def list_purchases(username=None):
    conn = get_connection()
    cur = conn.cursor()

    if username:
        cur.execute("""
        SELECT * FROM payments
        WHERE username = ?
        ORDER BY id DESC
        """, (username,))
    else:
        cur.execute("SELECT * FROM payments ORDER BY id DESC")

    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def upsert_subscription(username, customer_id, subscription_id, price_id, plan, status, period_start="", period_end=""):
    conn = get_connection()
    cur = conn.cursor()

    existing = cur.execute("""
    SELECT id FROM subscriptions
    WHERE stripe_subscription_id = ?
    """, (subscription_id,)).fetchone()

    if existing:
        cur.execute("""
        UPDATE subscriptions
        SET status = ?, plan = ?, stripe_price_id = ?,
            current_period_start = ?, current_period_end = ?, updated_at = ?
        WHERE stripe_subscription_id = ?
        """, (
            status,
            plan,
            price_id,
            period_start,
            period_end,
            now(),
            subscription_id,
        ))
    else:
        cur.execute("""
        INSERT INTO subscriptions (
            username, stripe_customer_id, stripe_subscription_id,
            stripe_price_id, plan, status, current_period_start,
            current_period_end, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            customer_id,
            subscription_id,
            price_id,
            plan,
            status,
            period_start,
            period_end,
            now(),
            now(),
        ))

    conn.commit()
    conn.close()


def list_subscriptions(username=None):
    conn = get_connection()
    cur = conn.cursor()

    if username:
        cur.execute("""
        SELECT * FROM subscriptions
        WHERE username = ?
        ORDER BY id DESC
        """, (username,))
    else:
        cur.execute("SELECT * FROM subscriptions ORDER BY id DESC")

    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


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
        now(),
    ))

    conn.commit()
    conn.close()


def increment_usage(username, tool):
    save_usage(username, tool, "", 0, 0, "", "success")


def list_usage(username=None):
    conn = get_connection()
    cur = conn.cursor()

    if username:
        cur.execute("""
        SELECT * FROM usage_logs
        WHERE username = ?
        ORDER BY id DESC
        """, (username,))
    else:
        cur.execute("SELECT * FROM usage_logs ORDER BY id DESC")

    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_audit_log(actor, action, target="", details=""):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO audit_logs (
        actor, action, target, details, created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (actor, action, target, details, now()))

    conn.commit()
    conn.close()


def list_audit_logs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM audit_logs ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_api_key_ref(provider, env_name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO api_key_refs (
        provider, env_name, is_active, created_at, updated_at
    )
    VALUES (?, ?, 1, ?, ?)
    ON CONFLICT(provider) DO UPDATE SET
        env_name = excluded.env_name,
        is_active = 1,
        updated_at = excluded.updated_at
    """, (provider, env_name, now(), now()))

    conn.commit()
    conn.close()


def list_api_key_refs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM api_key_refs ORDER BY provider ASC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


init_db()