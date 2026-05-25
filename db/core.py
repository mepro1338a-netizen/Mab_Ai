"""SQLite connection helpers and schema initialization."""
import sqlite3
from datetime import datetime

from config import DB_PATH

OWNER_USERNAME = "mepro1337"

ROLE_LEVELS = {
    "user": 0,
    "supporter": 1,
    "moderator": 2,
    "admin": 3,
    "owner": 1337,
}


def now():
    return datetime.utcnow().isoformat()


def normalize_username(username):
    return (username or "").strip().lower()


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def row_to_dict(row):
    return dict(row) if row else None


def rows_to_dicts(rows):
    return [dict(row) for row in rows]


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT,
        plan TEXT DEFAULT 'free',
        tokens INTEGER DEFAULT 0,
        automation_unlocked INTEGER DEFAULT 0,
        role TEXT DEFAULT 'user',
        admin_level INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        created_at TEXT,
        last_login TEXT
    )
    """)

    try:
        cur.execute("ALTER TABLE users ADD COLUMN automation_unlocked INTEGER DEFAULT 0")
    except Exception:
        pass

    for column, definition in (
        ("oauth_provider", "TEXT"),
        ("oauth_sub", "TEXT"),
        ("football_plan", "TEXT DEFAULT 'none'"),
    ):
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
        except Exception:
            pass

    cur.execute("""
    CREATE TABLE IF NOT EXISTS football_daily_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        usage_date TEXT NOT NULL,
        api_calls INTEGER DEFAULT 0,
        ai_actions INTEGER DEFAULT 0,
        ai_analyses INTEGER DEFAULT 0,
        UNIQUE(username, usage_date)
    )
    """)

    try:
        cur.execute(
            "ALTER TABLE football_daily_usage ADD COLUMN ai_analyses INTEGER DEFAULT 0"
        )
    except Exception:
        pass

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
        created_at TEXT,
        updated_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS app_error_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        error_type TEXT,
        message TEXT,
        page TEXT,
        username TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS support_ticket_replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER NOT NULL,
        author TEXT,
        body TEXT,
        is_staff INTEGER DEFAULT 0,
        created_at TEXT
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
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        plan TEXT,
        amount INTEGER DEFAULT 0,
        stripe_session_id TEXT,
        payment_status TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        ip_address TEXT,
        user_agent TEXT,
        success INTEGER DEFAULT 0,
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

    conn.commit()
    conn.close()
