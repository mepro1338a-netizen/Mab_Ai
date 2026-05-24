import re
import sqlite3
import secrets
from datetime import datetime, timedelta

import bcrypt

from config import DB_PATH, PLANS


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
    ):
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
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


def validate_password(password):
    if not password:
        return False, "Bitte Passwort eingeben."

    if len(password) < 6:
        return False, "Passwort muss mindestens 6 Zeichen haben."

    if len(password.encode("utf-8")) > 72:
        return False, "Passwort maximal 72 Zeichen."

    return True, ""


def create_user(username, email, password):
    username = normalize_username(username)
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
            bcrypt.gensalt(),
        ).decode("utf-8")

        cur.execute("""
        INSERT INTO users (
            username,
            email,
            password_hash,
            plan,
            tokens,
            automation_unlocked,
            role,
            admin_level,
            is_banned,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            email,
            password_hash,
            "free",
            int(PLANS["free"]["tokens"]),
            0,
            "user",
            0,
            0,
            now(),
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
    username = normalize_username(username)

    if not username or not password:
        return False, "Bitte Username und Passwort eingeben.", None

    conn = get_connection()
    cur = conn.cursor()

    user = cur.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    ).fetchone()

    if not user:
        conn.close()
        return False, "User nicht gefunden.", None

    if int(user["is_banned"] or 0) == 1:
        conn.close()
        return False, "Account gesperrt.", None

    try:
        valid = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8"),
        )
    except Exception:
        valid = False

    if not valid:
        conn.close()
        return False, "Falsches Passwort.", None

    cur.execute(
        "UPDATE users SET last_login = ? WHERE username = ?",
        (now(), username),
    )

    conn.commit()

    updated_user = cur.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,),
    ).fetchone()

    conn.close()
    return True, "Login erfolgreich.", row_to_dict(updated_user)


def _username_from_email(email: str) -> str:
    local = (email or "").split("@")[0].lower()
    local = re.sub(r"[^a-z0-9_]", "_", local)
    local = re.sub(r"_+", "_", local).strip("_")

    if len(local) < 3:
        local = f"user_{secrets.token_hex(3)}"

    return local[:40]


def _unique_username(base: str) -> str:
    username = base[:40]
    if not get_user(username):
        return username

    for _ in range(20):
        candidate = f"{base[:32]}_{secrets.token_hex(2)}"
        if not get_user(candidate):
            return candidate

    return f"user_{secrets.token_hex(4)}"


def oauth_login_or_register(email, display_name, provider, provider_sub):
    email = (email or "").strip().lower()
    provider = (provider or "").strip().lower()
    provider_sub = str(provider_sub or "").strip()
    display_name = (display_name or "").strip()

    if not provider or not provider_sub:
        return False, "OAuth Daten unvollständig.", None

    conn = get_connection()
    cur = conn.cursor()

    user = cur.execute(
        "SELECT * FROM users WHERE oauth_provider = ? AND oauth_sub = ?",
        (provider, provider_sub),
    ).fetchone()

    if not user and email:
        existing = cur.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()

        if existing:
            conn.close()
            return (
                False,
                "Diese Email ist bereits registriert. Bitte mit Passwort anmelden.",
                None,
            )

    if user:
        if int(user["is_banned"] or 0) == 1:
            conn.close()
            return False, "Account gesperrt.", None

        cur.execute(
            "UPDATE users SET last_login = ? WHERE username = ?",
            (now(), user["username"]),
        )
        conn.commit()
        updated = cur.execute(
            "SELECT * FROM users WHERE username = ?",
            (user["username"],),
        ).fetchone()
        conn.close()
        return True, "Login erfolgreich.", row_to_dict(updated)

    if not email:
        conn.close()
        return False, "Keine Email vom Provider erhalten.", None

    base_username = _username_from_email(email)
    if display_name:
        cleaned = re.sub(r"[^a-zA-Z0-9_]", "", display_name.replace(" ", "_").lower())
        if len(cleaned) >= 3:
            base_username = cleaned[:40]

    username = _unique_username(base_username)
    password_hash = bcrypt.hashpw(
        secrets.token_urlsafe(32).encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    try:
        cur.execute(
            """
            INSERT INTO users (
                username, email, password_hash, plan, tokens,
                automation_unlocked, role, admin_level, is_banned,
                created_at, last_login, oauth_provider, oauth_sub
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                email,
                password_hash,
                "free",
                int(PLANS["free"]["tokens"]),
                0,
                "user",
                0,
                0,
                now(),
                now(),
                provider,
                provider_sub,
            ),
        )
        conn.commit()
        created = cur.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        conn.close()
        return True, "Account erstellt.", row_to_dict(created)

    except sqlite3.IntegrityError:
        conn.close()
        return False, "Account konnte nicht erstellt werden.", None

    except Exception as exc:
        conn.close()
        return False, f"Datenbankfehler: {exc}", None


def get_user(username):
    conn = get_connection()
    cur = conn.cursor()

    user = cur.execute(
        "SELECT * FROM users WHERE username = ?",
        (normalize_username(username),),
    ).fetchone()

    conn.close()
    return row_to_dict(user)


def list_users():
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT * FROM users ORDER BY id DESC"
    ).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def get_role_level(username):
    username = normalize_username(username)

    if username == OWNER_USERNAME:
        return 1337

    user = get_user(username)

    if not user:
        return 0

    role = str(user.get("role") or "user").lower()
    return int(user.get("admin_level") or ROLE_LEVELS.get(role, 0))


def is_owner_user(username):
    username = normalize_username(username)
    return username == OWNER_USERNAME or get_role_level(username) >= 1337


def can_manage_support(actor):
    return get_role_level(actor) >= 1


def can_manage_users(actor):
    return get_role_level(actor) >= 2


def can_manage_roles(actor):
    return get_role_level(actor) >= 3


def can_assign_role(actor, target, new_role):
    actor = normalize_username(actor)
    target = normalize_username(target)
    new_role = str(new_role or "user").lower()

    if not can_manage_roles(actor):
        return False, "Keine Berechtigung für Rollen."

    if target == OWNER_USERNAME and not is_owner_user(actor):
        return False, "Owner ist geschützt."

    if new_role == "owner" and not is_owner_user(actor):
        return False, "Nur Owner darf Owner vergeben."

    if new_role not in ROLE_LEVELS:
        return False, "Ungültige Rolle."

    return True, ""


def is_protected_account(username):
    username = normalize_username(username)
    return username == OWNER_USERNAME or is_owner_user(username)


def can_modify_target(actor, target):
    actor = normalize_username(actor)
    target = normalize_username(target)

    if is_protected_account(target) and not is_owner_user(actor):
        return False, "Dieser Account ist geschuetzt."

    if actor == target:
        return True, ""

    actor_level = get_role_level(actor)
    target_level = get_role_level(target)

    if target_level >= actor_level and not is_owner_user(actor):
        return False, "Keine Berechtigung fuer gleich/hoehergestellte User."

    return True, ""


def set_role(username, role, admin_level=None):
    username = normalize_username(username)
    role = str(role or "user").lower()

    if role not in ROLE_LEVELS:
        role = "user"

    if username == OWNER_USERNAME:
        role = "owner"
        level = 1337
    else:
        level = ROLE_LEVELS.get(role, 0)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET role = ?, admin_level = ? WHERE username = ?",
        (role, int(level), username),
    )

    conn.commit()
    conn.close()


def secure_set_role(actor, target, new_role):
    ok, msg = can_assign_role(actor, target, new_role)

    if not ok:
        return False, msg

    ok, msg = can_modify_target(actor, target)
    if not ok:
        return False, msg

    set_role(target, new_role)
    add_audit_log(actor, "set_role", target, new_role)
    return True, "Rolle gespeichert."


def make_admin(username):
    username = normalize_username(username)

    if username == OWNER_USERNAME:
        set_role(username, "owner", 1337)
    else:
        set_role(username, "admin", 3)


def set_plan(username, plan):
    username = normalize_username(username)

    if plan not in PLANS:
        plan = "free"

    tokens = int(PLANS.get(plan, PLANS["free"]).get("tokens", 0))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET plan = ?, tokens = ? WHERE username = ?",
        (plan, tokens, username),
    )

    conn.commit()
    conn.close()


def update_tokens(username, tokens):
    tokens = max(0, int(tokens))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET tokens = ? WHERE username = ?",
        (tokens, normalize_username(username)),
    )

    conn.commit()
    conn.close()


def secure_update_tokens(actor, target, tokens):
    if not can_manage_users(actor):
        return False, "Keine Berechtigung."

    ok, msg = can_modify_target(actor, target)
    if not ok:
        return False, msg

    update_tokens(target, tokens)
    add_audit_log(actor, "update_tokens", target, f"tokens={max(0, int(tokens))}")
    return True, "Tokens gespeichert."


def secure_set_plan(actor, target, plan):
    if not can_manage_users(actor):
        return False, "Keine Berechtigung."

    ok, msg = can_modify_target(actor, target)
    if not ok:
        return False, msg

    set_plan(target, plan)
    add_audit_log(actor, "set_plan", target, str(plan))
    return True, "Plan gespeichert."


def spend_tokens(username, amount):
    username = normalize_username(username)
    amount = int(amount)

    if amount <= 0:
        return False, "Ungueltiger Token-Betrag."

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET tokens = tokens - ?
    WHERE username = ?
    AND tokens >= ?
    """, (
        amount,
        username,
        amount,
    ))

    if cur.rowcount == 0:
        conn.rollback()
        conn.close()
        return False, "Nicht genug Tokens."

    conn.commit()
    conn.close()

    return True, "Tokens abgezogen."


def ban_user(username, banned=True):
    username = normalize_username(username)

    if is_protected_account(username):
        return False

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET is_banned = ? WHERE username = ?",
        (1 if banned else 0, username),
    )

    conn.commit()
    conn.close()

    return True


def secure_ban_user(actor, target, banned=True):
    if not can_manage_users(actor):
        return False, "Keine Berechtigung."

    target = normalize_username(target)

    ok, msg = can_modify_target(actor, target)
    if not ok:
        return False, msg

    if not ban_user(target, banned):
        return False, "Account ist geschuetzt."

    action = "ban_user" if banned else "unban_user"
    add_audit_log(actor, action, target, "")
    return True, "Status geaendert."


def delete_user(username):
    username = normalize_username(username)

    if is_protected_account(username):
        return False

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM users WHERE username = ?",
        (username,),
    )

    conn.commit()
    conn.close()

    return True


def secure_delete_user(actor, target):
    if not can_manage_roles(actor):
        return False, "Keine Berechtigung."

    target = normalize_username(target)

    ok, msg = can_modify_target(actor, target)
    if not ok:
        return False, msg

    if not delete_user(target):
        return False, "Account ist geschuetzt."

    add_audit_log(actor, "delete_user", target, "")
    return True, "User geloescht."


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
        normalize_username(username),
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
        rows = cur.execute(
            "SELECT * FROM support_tickets ORDER BY id DESC"
        ).fetchall()
    else:
        rows = cur.execute(
            "SELECT * FROM support_tickets WHERE status = ? ORDER BY id DESC",
            (status_filter,),
        ).fetchall()

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
        (status, now(), int(ticket_id)),
    )

    conn.commit()
    conn.close()


def delete_support_message(ticket_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM support_tickets WHERE id = ?",
        (int(ticket_id),),
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
    days_valid=30,
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
        normalize_username(created_by),
        expires_at,
        now(),
    ))

    conn.commit()
    conn.close()

    return code


def list_codes():
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT * FROM redeem_codes ORDER BY id DESC"
    ).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def redeem_code(username, code):
    username = normalize_username(username)
    code = (code or "").strip().upper()

    conn = get_connection()
    cur = conn.cursor()

    item = cur.execute(
        "SELECT * FROM redeem_codes WHERE code = ? AND is_active = 1",
        (code,),
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
            (int(item["tokens"]), username),
        )

    if item["plan"]:
        cur.execute(
            "UPDATE users SET plan = ? WHERE username = ?",
            (item["plan"], username),
        )

    cur.execute(
        "UPDATE redeem_codes SET used_count = used_count + 1 WHERE code = ?",
        (code,),
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
    status="success",
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
        normalize_username(username),
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
        rows = cur.execute(
            "SELECT * FROM usage_logs WHERE username = ? ORDER BY id DESC",
            (normalize_username(username),),
        ).fetchall()
    else:
        rows = cur.execute(
            "SELECT * FROM usage_logs ORDER BY id DESC"
        ).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def usage_summary(username=None, days=7):
    conn = get_connection()
    cur = conn.cursor()

    since = (datetime.utcnow() - timedelta(days=int(days))).isoformat()

    if username:
        rows = cur.execute("""
        SELECT tool, COUNT(*) AS runs, SUM(cost_tokens) AS total_tokens
        FROM usage_logs
        WHERE username = ?
        AND created_at >= ?
        GROUP BY tool
        ORDER BY runs DESC
        """, (
            normalize_username(username),
            since,
        )).fetchall()
    else:
        rows = cur.execute("""
        SELECT tool, COUNT(*) AS runs, SUM(cost_tokens) AS total_tokens
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
        SELECT tool, prompt, cost_tokens, api_provider, status, created_at
        FROM usage_logs
        WHERE username = ?
        ORDER BY id DESC
        LIMIT ?
        """, (
            normalize_username(username),
            int(limit),
        )).fetchall()
    else:
        rows = cur.execute("""
        SELECT tool, prompt, cost_tokens, api_provider, status, created_at
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
            normalize_username(username),
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
            normalize_username(username),
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
            normalize_username(username),
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
        normalize_username(username),
        plan,
        int(amount or 0),
        session_id,
        payment_status,
        status,
        now(),
    ))

    conn.commit()
    conn.close()


def list_purchases(username=None):
    conn = get_connection()
    cur = conn.cursor()

    if username:
        rows = cur.execute(
            "SELECT * FROM payments WHERE username = ? ORDER BY id DESC",
            (normalize_username(username),),
        ).fetchall()
    else:
        rows = cur.execute(
            "SELECT * FROM payments ORDER BY id DESC"
        ).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def record_login_event(username, ip_address="", user_agent="", success=True):
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
        normalize_username(username),
        ip_address,
        user_agent,
        1 if success else 0,
        now(),
    ))

    conn.commit()
    conn.close()


def list_login_logs(username=None, limit=200):
    conn = get_connection()
    cur = conn.cursor()

    if username:
        rows = cur.execute("""
        SELECT * FROM login_logs
        WHERE username = ?
        ORDER BY id DESC
        LIMIT ?
        """, (
            normalize_username(username),
            int(limit),
        )).fetchall()
    else:
        rows = cur.execute("""
        SELECT * FROM login_logs
        ORDER BY id DESC
        LIMIT ?
        """, (
            int(limit),
        )).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def clear_login_logs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM login_logs")
    conn.commit()
    conn.close()


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
        normalize_username(username),
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

    rows = cur.execute("""
    SELECT * FROM projects
    WHERE username = ?
    ORDER BY id DESC
    """, (
        normalize_username(username),
    )).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def get_project(project_id, username=None):
    ensure_project_tables()

    conn = get_connection()
    cur = conn.cursor()

    row = cur.execute("""
    SELECT * FROM projects
    WHERE id = ?
    """, (
        int(project_id),
    )).fetchone()

    conn.close()
    project = row_to_dict(row)

    if not project:
        return None

    if username and normalize_username(project.get("username")) != normalize_username(username):
        return None

    return project


def save_project_memory(project_id, username, workspace, memory_type, content):
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
        normalize_username(username),
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

    rows = cur.execute("""
    SELECT * FROM project_memory
    WHERE project_id = ?
    ORDER BY id DESC
    """, (
        int(project_id),
    )).fetchall()

    conn.close()
    return rows_to_dicts(rows)


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


def save_project_chat_message(project_id, username, role, message):
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
        normalize_username(username),
        role,
        message,
        now(),
    ))

    conn.commit()
    conn.close()


def list_project_chat_memory(project_id, limit=30):
    ensure_chat_memory_tables()

    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("""
    SELECT * FROM project_chat_memory
    WHERE project_id = ?
    ORDER BY id DESC
    LIMIT ?
    """, (
        int(project_id),
        int(limit),
    )).fetchall()

    conn.close()

    rows = rows_to_dicts(rows)
    rows.reverse()

    return rows


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
        normalize_username(username),
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
        rows = cur.execute("""
        SELECT * FROM automations
        WHERE username = ?
        ORDER BY id DESC
        """, (
            normalize_username(username),
        )).fetchall()
    else:
        rows = cur.execute("""
        SELECT * FROM automations
        ORDER BY id DESC
        """).fetchall()

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
        normalize_username(username),
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
        rows = cur.execute("""
        SELECT * FROM automation_runs
        WHERE username = ?
        ORDER BY id DESC
        LIMIT ?
        """, (
            normalize_username(username),
            int(limit),
        )).fetchall()
    else:
        rows = cur.execute("""
        SELECT * FROM automation_runs
        ORDER BY id DESC
        LIMIT ?
        """, (
            int(limit),
        )).fetchall()

    conn.close()
    return rows_to_dicts(rows)


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


def save_global_memory(username, memory_type, content, importance=1):
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
        normalize_username(username),
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

    rows = cur.execute("""
    SELECT * FROM global_memory
    WHERE username = ?
    ORDER BY importance DESC, id DESC
    LIMIT ?
    """, (
        normalize_username(username),
        int(limit),
    )).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def search_global_memory(username, query, limit=10):
    ensure_global_memory_tables()

    conn = get_connection()
    cur = conn.cursor()

    q = f"%{(query or '').lower()}%"

    rows = cur.execute("""
    SELECT * FROM global_memory
    WHERE username = ?
    AND LOWER(content) LIKE ?
    ORDER BY importance DESC, id DESC
    LIMIT ?
    """, (
        normalize_username(username),
        q,
        int(limit),
    )).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def unlock_automation(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE users
    SET automation_unlocked = 1
    WHERE username = ?
    """, (
        normalize_username(username),
    ))

    conn.commit()
    conn.close()


def has_automation_access(username):
    user = get_user(username)

    if not user:
        return False

    return int(user.get("automation_unlocked") or 0) == 1


def add_audit_log(actor, action, target="", details=""):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO audit_logs (actor, action, target, details, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (
        normalize_username(actor) or str(actor or ""),
        str(action or "")[:120],
        str(target or "")[:120],
        str(details or "")[:2000],
        now(),
    ))

    conn.commit()
    conn.close()


def list_audit_logs(limit=200):
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("""
    SELECT * FROM audit_logs
    ORDER BY id DESC
    LIMIT ?
    """, (int(limit),)).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def force_owner_account():
    user = get_user(OWNER_USERNAME)

    if not user:
        return

    if user.get("role") != "owner" or int(user.get("admin_level") or 0) != 1337:
        set_role(OWNER_USERNAME, "owner", 1337)

    if user.get("plan") != "elite":
        set_plan(OWNER_USERNAME, "elite")


init_db()
force_owner_account()