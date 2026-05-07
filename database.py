import sqlite3
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "mabai.db"


# =========================================================
# CONNECTION
# =========================================================

def now():
    return datetime.utcnow().isoformat()


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_value(value):
    if not value:
        return ""
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


# =========================================================
# INIT DATABASE
# =========================================================

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
        role TEXT DEFAULT 'user',
        admin_level INTEGER DEFAULT 0,
        is_verified INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        stripe_customer_id TEXT,
        created_at TEXT,
        last_login TEXT,
        register_ip_hash TEXT,
        device_hash TEXT
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
        assigned_to TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ticket_replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER,
        username TEXT,
        role TEXT,
        message TEXT,
        created_at TEXT
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
        amount INTEGER,
        currency TEXT DEFAULT 'eur',
        status TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        stripe_customer_id TEXT,
        stripe_subscription_id TEXT,
        stripe_price_id TEXT,
        plan TEXT,
        status TEXT,
        current_period_start TEXT,
        current_period_end TEXT,
        created_at TEXT,
        updated_at TEXT
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
        created_at TEXT
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
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS redeem_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        username TEXT,
        redeemed_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        ip_hash TEXT,
        device_hash TEXT,
        success INTEGER DEFAULT 0,
        reason TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor TEXT,
        action TEXT,
        target TEXT,
        details TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS api_key_refs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider TEXT UNIQUE,
        env_name TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================================================
# USERS
# =========================================================

def create_user(username, email, password, ip_address="", device_id=""):
    username = username.strip().lower()
    email = email.strip().lower()

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO users (
            username, email, password, plan, tokens, role, admin_level,
            is_verified, is_banned, created_at, register_ip_hash, device_hash
        )
        VALUES (?, ?, ?, 'free', 0, 'user', 0, 0, 0, ?, ?, ?)
        """, (
            username,
            email,
            password,
            now(),
            hash_value(ip_address),
            hash_value(device_id),
        ))

        conn.commit()
        return True, "Account erstellt."

    except sqlite3.IntegrityError:
        return False, "Username oder Email existiert bereits."

    except Exception as e:
        return False, str(e)

    finally:
        conn.close()


def get_user(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username = ?", (username.strip().lower(),))
    user = cur.fetchone()

    conn.close()
    return user


def get_user_by_email(email):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
    user = cur.fetchone()

    conn.close()
    return user


def list_users():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users ORDER BY id DESC")
    rows = cur.fetchall()

    conn.close()
    return rows


def verify_login(username, password, ip_address="", device_id=""):
    username = username.strip().lower()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()

    if not user:
        log_login_attempt(username, "", ip_address, device_id, False, "user_not_found")
        conn.close()
        return False, "User nicht gefunden.", None

    if user["is_banned"]:
        log_login_attempt(username, user["email"], ip_address, device_id, False, "banned")
        conn.close()
        return False, "Account gesperrt.", None

    if user["password"] != password:
        log_login_attempt(username, user["email"], ip_address, device_id, False, "wrong_password")
        conn.close()
        return False, "Falsches Passwort.", None

    cur.execute(
        "UPDATE users SET last_login = ? WHERE username = ?",
        (now(), username)
    )

    conn.commit()
    conn.close()

    log_login_attempt(username, user["email"], ip_address, device_id, True, "success")

    return True, "Login erfolgreich.", dict(user)


def update_user_plan(username, plan):
    token_map = {
        "free": 0,
        "pro": 1200,
        "grand": 4000,
        "elite": 999999,
    }

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET plan = ?, tokens = ?
    WHERE username = ?
    """, (
        plan,
        token_map.get(plan, 0),
        username.strip().lower(),
    ))

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
    """, (
        int(tokens),
        username.strip().lower(),
    ))

    conn.commit()
    conn.close()


def add_tokens(username, amount):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET tokens = COALESCE(tokens, 0) + ?
    WHERE username = ?
    """, (
        int(amount),
        username.strip().lower(),
    ))

    conn.commit()
    conn.close()


def remove_tokens(username, amount):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET tokens = MAX(COALESCE(tokens, 0) - ?, 0)
    WHERE username = ?
    """, (
        int(amount),
        username.strip().lower(),
    ))

    conn.commit()
    conn.close()


def set_role(username, role, admin_level=0):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET role = ?, admin_level = ?
    WHERE username = ?
    """, (
        role,
        int(admin_level),
        username.strip().lower(),
    ))

    conn.commit()
    conn.close()


def ban_user(username, banned=True):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET is_banned = ?
    WHERE username = ?
    """, (
        1 if banned else 0,
        username.strip().lower(),
    ))

    conn.commit()
    conn.close()


def delete_user(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE username = ?", (username.strip().lower(),))

    conn.commit()
    conn.close()
    return True


# =========================================================
# ANTI MULTIACCOUNT
# =========================================================

def count_accounts_by_ip(ip_address):
    ip_hash = hash_value(ip_address)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT COUNT(*) AS count
    FROM users
    WHERE register_ip_hash = ?
    """, (ip_hash,))

    count = cur.fetchone()["count"]

    conn.close()
    return count


def count_accounts_by_device(device_id):
    device_hash = hash_value(device_id)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT COUNT(*) AS count
    FROM users
    WHERE device_hash = ?
    """, (device_hash,))

    count = cur.fetchone()["count"]

    conn.close()
    return count


def log_login_attempt(username, email, ip_address, device_id, success, reason):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO login_attempts (
        username, email, ip_hash, device_hash, success, reason, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        username,
        email,
        hash_value(ip_address),
        hash_value(device_id),
        1 if success else 0,
        reason,
        now(),
    ))

    conn.commit()
    conn.close()


# =========================================================
# SUPPORT TICKETS
# =========================================================

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
        now(),
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
    return rows


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
    """, (
        status,
        now(),
        int(ticket_id),
    ))

    conn.commit()
    conn.close()


def assign_support_ticket(ticket_id, admin_username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE support_tickets
    SET assigned_to = ?, updated_at = ?
    WHERE id = ?
    """, (
        admin_username,
        now(),
        int(ticket_id),
    ))

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
    """, (
        int(ticket_id),
        username,
        role,
        message,
        now(),
    ))

    cur.execute("""
    UPDATE support_tickets
    SET updated_at = ?
    WHERE id = ?
    """, (
        now(),
        int(ticket_id),
    ))

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
    return rows


def delete_support_message(ticket_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM ticket_replies WHERE ticket_id = ?", (int(ticket_id),))
    cur.execute("DELETE FROM support_tickets WHERE id = ?", (int(ticket_id),))

    conn.commit()
    conn.close()


# =========================================================
# PAYMENTS / SUBSCRIPTIONS
# =========================================================

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
    return rows


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
    return rows


# =========================================================
# USAGE LOGS
# =========================================================

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
    return rows


# =========================================================
# REDEEM CODES
# =========================================================

def create_redeem_code(code_type, value, tokens, plan, max_uses, created_by, days_valid=30):
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
    return rows


def redeem_code(username, code):
    code = code.strip().upper()

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
        """, (
            int(item["tokens"]),
            username,
        ))

    if item["plan"]:
        cur.execute("""
        UPDATE users
        SET plan = ?
        WHERE username = ?
        """, (
            item["plan"],
            username,
        ))

    cur.execute("""
    UPDATE redeem_codes
    SET used_count = used_count + 1
    WHERE code = ?
    """, (code,))

    cur.execute("""
    INSERT INTO redeem_logs (
        code, username, redeemed_at
    )
    VALUES (?, ?, ?)
    """, (
        code,
        username,
        now(),
    ))

    conn.commit()
    conn.close()

    return True, "Code eingelöst."


# =========================================================
# AUDIT LOGS
# =========================================================

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
        now(),
    ))

    conn.commit()
    conn.close()


def list_audit_logs():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM audit_logs ORDER BY id DESC")
    rows = cur.fetchall()

    conn.close()
    return rows


# =========================================================
# API KEY REFERENCES
# =========================================================

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
    """, (
        provider,
        env_name,
        now(),
        now(),
    ))

    conn.commit()
    conn.close()


def list_api_key_refs():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM api_key_refs ORDER BY provider ASC")
    rows = cur.fetchall()

    conn.close()
    return rows


init_db()