import sqlite3
import secrets
from datetime import datetime, timedelta
import bcrypt

from config import DB_PATH, PLANS

# =========================================================
# MISSION CONTROL / ACTIVITY
# =========================================================

def usage_summary(username=None, days=7):
    conn = get_connection()
    cur = conn.cursor()

    since = (datetime.utcnow() - timedelta(days=int(days))).isoformat()

    if username:
        rows = cur.execute("""
            SELECT
                tool,
                COUNT(*) AS runs,
                SUM(cost_tokens) AS total_tokens
            FROM usage_logs
            WHERE username = ?
            AND created_at >= ?
            GROUP BY tool
            ORDER BY runs DESC
        """, (
            (username or "").strip().lower(),
            since,
        )).fetchall()
    else:
        rows = cur.execute("""
            SELECT
                tool,
                COUNT(*) AS runs,
                SUM(cost_tokens) AS total_tokens
            FROM usage_logs
            WHERE created_at >= ?
            GROUP BY tool
            ORDER BY runs DESC
        """, (
            since,
        )).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def recent_activity(username=None, limit=8):
    conn = get_connection()
    cur = conn.cursor()

    if username:
        rows = cur.execute("""
            SELECT
                tool,
                prompt,
                cost_tokens,
                api_provider,
                status,
                created_at
            FROM usage_logs
            WHERE username = ?
            ORDER BY id DESC
            LIMIT ?
        """, (
            (username or "").strip().lower(),
            int(limit),
        )).fetchall()
    else:
        rows = cur.execute("""
            SELECT
                tool,
                prompt,
                cost_tokens,
                api_provider,
                status,
                created_at
            FROM usage_logs
            ORDER BY id DESC
            LIMIT ?
        """, (
            int(limit),
        )).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def total_tokens_used(username=None):
    conn = get_connection()
    cur = conn.cursor()

    if username:
        row = cur.execute("""
            SELECT SUM(cost_tokens) AS total
            FROM usage_logs
            WHERE username = ?
            AND cost_tokens > 0
        """, (
            (username or "").strip().lower(),
        )).fetchone()
    else:
        row = cur.execute("""
            SELECT SUM(cost_tokens) AS total
            FROM usage_logs
            WHERE cost_tokens > 0
        """).fetchone()

    conn.close()
    return int(row["total"] or 0)


def successful_jobs_count(username=None):
    conn = get_connection()
    cur = conn.cursor()

    if username:
        row = cur.execute("""
            SELECT COUNT(*) AS total
            FROM usage_logs
            WHERE username = ?
            AND status IN ('success', 'charged')
        """, (
            (username or "").strip().lower(),
        )).fetchone()
    else:
        row = cur.execute("""
            SELECT COUNT(*) AS total
            FROM usage_logs
            WHERE status IN ('success', 'charged')
        """).fetchone()

    conn.close()
    return int(row["total"] or 0)


def failed_jobs_count(username=None):
    conn = get_connection()
    cur = conn.cursor()

    if username:
        row = cur.execute("""
            SELECT COUNT(*) AS total
            FROM usage_logs
            WHERE username = ?
            AND status IN ('failed', 'error', 'refunded')
        """, (
            (username or "").strip().lower(),
        )).fetchone()
    else:
        row = cur.execute("""
            SELECT COUNT(*) AS total
            FROM usage_logs
            WHERE status IN ('failed', 'error', 'refunded')
        """).fetchone()

    conn.close()
    return int(row["total"] or 0)


def workspace_activity_score(username=None):
    summary = usage_summary(username=username, days=7)

    score = 0

    for row in summary:
        runs = int(row.get("runs") or 0)
        tokens = int(row.get("total_tokens") or 0)
        score += runs * 5
        score += min(tokens // 10, 100)

    return min(score, 100)


def latest_tool_used(username=None):
    activity = recent_activity(username=username, limit=1)

    if not activity:
        return "None"

    return activity[0].get("tool", "None")

def now():
    return datetime.utcnow().isoformat()


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_dict(row):
    return dict(row) if row else None


def rows_to_dicts(rows):
    return [dict(row) for row in rows]


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
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT,
        plan TEXT DEFAULT 'free',
        tokens INTEGER DEFAULT 0,
        role TEXT DEFAULT 'user',
        admin_level INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        created_at TEXT,
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

    conn.commit()
    conn.close()


def create_user(username, email, password):
    username = (username or "").strip().lower()
    email = (email or "").strip().lower()

    if not username or not email or not password:
        return False, "Bitte alle Felder ausfüllen."

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
            is_banned,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            email,
            password_hash,
            "free",
            int(PLANS["free"]["tokens"]),
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
        conn.commit()
        conn.close()


def verify_login(username, password):
    username = (username or "").strip().lower()

    if not username or not password:
        return False, "Bitte Username und Passwort eingeben.", None

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()

    if not user:
        conn.close()
        return False, "User nicht gefunden.", None

    if int(user["is_banned"] or 0) == 1:
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

    cur.execute(
        "UPDATE users SET last_login = ? WHERE username = ?",
        (now(), username)
    )

    conn.commit()

    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    updated_user = cur.fetchone()

    conn.close()
    return True, "Login erfolgreich.", row_to_dict(updated_user)


def get_user(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username = ?",
        ((username or "").strip().lower(),)
    )

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
        (int(tokens), (username or "").strip().lower())
    )

    conn.commit()
    conn.close()


def spend_tokens(username, amount):
    user = get_user(username)

    if not user:
        return False, "User nicht gefunden."

    if int(user["tokens"] or 0) < int(amount):
        return False, "Nicht genug Tokens."

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET tokens = tokens - ? WHERE username = ?",
        (int(amount), (username or "").strip().lower())
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
        (plan, int(tokens), (username or "").strip().lower())
    )

    conn.commit()
    conn.close()


def set_role(username, role, admin_level=0):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET role = ?, admin_level = ? WHERE username = ?",
        (role, int(admin_level), (username or "").strip().lower())
    )

    conn.commit()
    conn.close()


def make_admin(username):
    set_role(username, "admin", 999)


def ban_user(username, banned=True):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET is_banned = ? WHERE username = ?",
        (1 if banned else 0, (username or "").strip().lower())
    )

    conn.commit()
    conn.close()


def delete_user(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM users WHERE username = ?",
        ((username or "").strip().lower(),)
    )

    conn.commit()
    conn.close()

    return True


def create_support_message(username, email, category, subject, message):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO support_tickets (
        username,
        email,
        category,
        subject,
        message,
        status,
        priority,
        created_at,
        updated_at
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

    total = cur.execute(
        "SELECT COUNT(*) AS c FROM support_tickets"
    ).fetchone()["c"]

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

    cur.execute(
        "DELETE FROM support_tickets WHERE id = ?",
        (int(ticket_id),)
    )

    conn.commit()
    conn.close()


def create_redeem_code(
    code_type,
    value="",
    tokens=0,
    plan="",
    max_uses=1,
    created_by="",
    days_valid=30
):
    code = secrets.token_hex(4).upper()
    expires_at = (datetime.utcnow() + timedelta(days=int(days_valid))).isoformat()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO redeem_codes (
        code,
        code_type,
        plan,
        tokens,
        max_uses,
        used_count,
        created_by,
        expires_at,
        is_active,
        created_at
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
        now()
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
    code = (code or "").strip().upper()
    username = (username or "").strip().lower()

    conn = get_connection()
    cur = conn.cursor()

    item = cur.execute(
        "SELECT * FROM redeem_codes WHERE code = ? AND is_active = 1",
        (code,)
    ).fetchone()

    if not item:
        conn.close()
        return False, "Code ungültig."

    if int(item["used_count"] or 0) >= int(item["max_uses"] or 1):
        conn.close()
        return False, "Code wurde bereits zu oft genutzt."

    if item["expires_at"] and datetime.fromisoformat(item["expires_at"]) < datetime.utcnow():
        conn.close()
        return False, "Code ist abgelaufen."

    if int(item["tokens"] or 0) > 0:
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


def save_usage(
    username,
    tool,
    prompt,
    tokens_used=0,
    cost_tokens=0,
    api_provider="",
    status="success"
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO usage_logs (
        username,
        tool,
        prompt,
        tokens_used,
        cost_tokens,
        api_provider,
        status,
        created_at
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
            ((username or "").strip().lower(),)
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
        actor,
        action,
        target,
        details,
        created_at
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
        username,
        plan,
        amount,
        stripe_session_id,
        payment_status,
        status,
        created_at
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
            ((username or "").strip().lower(),)
        )
    else:
        cur.execute("SELECT * FROM payments ORDER BY id DESC")

    rows = cur.fetchall()
    conn.close()

    return rows_to_dicts(rows)

def ensure_owner_tables():
    conn = get_connection()
    cur = conn.cursor()

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

    conn.commit()
    conn.close()


def record_login_event(username, ip_address="", user_agent="", success=True):
    ensure_owner_tables()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO login_logs (
        username,
        ip_address,
        user_agent,
        success,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        (username or "").strip().lower(),
        ip_address,
        user_agent,
        1 if success else 0,
        now(),
    ))

    conn.commit()
    conn.close()


def list_login_logs(username=None, limit=200):
    ensure_owner_tables()

    conn = get_connection()
    cur = conn.cursor()

    if username:
        cur.execute("""
        SELECT * FROM login_logs
        WHERE username = ?
        ORDER BY id DESC
        LIMIT ?
        """, ((username or "").strip().lower(), int(limit)))
    else:
        cur.execute("""
        SELECT * FROM login_logs
        ORDER BY id DESC
        LIMIT ?
        """, (int(limit),))

    rows = cur.fetchall()
    conn.close()

    return rows_to_dicts(rows)
# =========================================================
# PROJECTS
# =========================================================

def ensure_project_tables():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        title TEXT,
        description TEXT,
        workspace TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS project_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        username TEXT,
        workspace TEXT,
        memory_type TEXT,
        content TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_project(username, title, description="", workspace="general"):

    ensure_project_tables()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO projects (
        username,
        title,
        description,
        workspace,
        created_at,
        updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        (username or "").strip().lower(),
        title,
        description,
        workspace,
        now(),
        now(),
    ))

    conn.commit()

    project_id = cur.lastrowid

    conn.close()

    return project_id


def list_projects(username):

    ensure_project_tables()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM projects
    WHERE username = ?
    ORDER BY id DESC
    """, (
        (username or "").strip().lower(),
    ))

    rows = cur.fetchall()

    conn.close()

    return rows_to_dicts(rows)


def get_project(project_id):

    ensure_project_tables()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM projects
    WHERE id = ?
    """, (
        int(project_id),
    ))

    row = cur.fetchone()

    conn.close()

    return row_to_dict(row)


def save_project_memory(
    project_id,
    username,
    workspace,
    memory_type,
    content,
):

    ensure_project_tables()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO project_memory (
        project_id,
        username,
        workspace,
        memory_type,
        content,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        int(project_id),
        (username or "").strip().lower(),
        workspace,
        memory_type,
        content,
        now(),
    ))

    conn.commit()
    conn.close()


def list_project_memory(project_id):

    ensure_project_tables()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM project_memory
    WHERE project_id = ?
    ORDER BY id DESC
    """, (
        int(project_id),
    ))

    rows = cur.fetchall()

    conn.close()

    return rows_to_dicts(rows)

# =========================================================
# PROJECT CHAT MEMORY
# =========================================================

def ensure_chat_memory_tables():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS project_chat_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        username TEXT,
        role TEXT,
        message TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_project_chat_message(
    project_id,
    username,
    role,
    message,
):

    ensure_chat_memory_tables()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO project_chat_memory (
        project_id,
        username,
        role,
        message,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        int(project_id),
        (username or "").strip().lower(),
        role,
        message,
        now(),
    ))

    conn.commit()
    conn.close()


def list_project_chat_memory(
    project_id,
    limit=30,
):

    ensure_chat_memory_tables()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM project_chat_memory
    WHERE project_id = ?
    ORDER BY id DESC
    LIMIT ?
    """, (
        int(project_id),
        int(limit),
    ))

    rows = cur.fetchall()

    conn.close()

    rows = rows_to_dicts(rows)

    rows.reverse()

    return rows


# =========================================================
# AUTOMATION LAB
# =========================================================

def ensure_automation_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS automations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        project_id INTEGER,
        name TEXT,
        automation_type TEXT,
        source_workspace TEXT,
        target_workspace TEXT,
        trigger_text TEXT,
        status TEXT DEFAULT 'active',
        created_at TEXT,
        updated_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS automation_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        automation_id INTEGER,
        username TEXT,
        status TEXT,
        result TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_automation(
    username,
    project_id,
    name,
    automation_type,
    source_workspace,
    target_workspace,
    trigger_text,
):
    ensure_automation_tables()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO automations (
        username,
        project_id,
        name,
        automation_type,
        source_workspace,
        target_workspace,
        trigger_text,
        status,
        created_at,
        updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
    """, (
        (username or "").strip().lower(),
        int(project_id or 0),
        name,
        automation_type,
        source_workspace,
        target_workspace,
        trigger_text,
        now(),
        now(),
    ))

    conn.commit()
    automation_id = cur.lastrowid
    conn.close()

    return automation_id


def list_automations(username=None):
    ensure_automation_tables()

    conn = get_connection()
    cur = conn.cursor()

    if username:
        cur.execute("""
        SELECT * FROM automations
        WHERE username = ?
        ORDER BY id DESC
        """, ((username or "").strip().lower(),))
    else:
        cur.execute("""
        SELECT * FROM automations
        ORDER BY id DESC
        """)

    rows = cur.fetchall()
    conn.close()

    return rows_to_dicts(rows)


def update_automation_status(automation_id, status):
    ensure_automation_tables()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE automations
    SET status = ?, updated_at = ?
    WHERE id = ?
    """, (
        status,
        now(),
        int(automation_id),
    ))

    conn.commit()
    conn.close()


def create_automation_run(automation_id, username, status, result=""):
    ensure_automation_tables()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO automation_runs (
        automation_id,
        username,
        status,
        result,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        int(automation_id),
        (username or "").strip().lower(),
        status,
        result,
        now(),
    ))

    conn.commit()
    run_id = cur.lastrowid
    conn.close()

    return run_id


def list_automation_runs(username=None, limit=100):
    ensure_automation_tables()

    conn = get_connection()
    cur = conn.cursor()

    if username:
        cur.execute("""
        SELECT * FROM automation_runs
        WHERE username = ?
        ORDER BY id DESC
        LIMIT ?
        """, ((username or "").strip().lower(), int(limit)))
    else:
        cur.execute("""
        SELECT * FROM automation_runs
        ORDER BY id DESC
        LIMIT ?
        """, (int(limit),))

    rows = cur.fetchall()
    conn.close()

    return rows_to_dicts(rows)
# =========================================================
# GLOBAL MEMORY ENGINE
# =========================================================

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


def save_global_memory(
    username,
    memory_type,
    content,
    importance=1,
):

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
        (username or "").strip().lower(),
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

    cur.execute("""
    SELECT * FROM global_memory
    WHERE username = ?
    ORDER BY importance DESC, id DESC
    LIMIT ?
    """, (
        (username or "").strip().lower(),
        int(limit),
    ))

    rows = cur.fetchall()

    conn.close()

    return rows_to_dicts(rows)

init_db()

user = get_user("mepro1337")

if user:
    make_admin("mepro1337")

    if user.get("plan") != "elite":
        set_plan("mepro1337", "elite")


