"""Users, auth, roles, tokens."""
import re
import sqlite3
import secrets

import bcrypt

from config import PLANS, FOOTBALL_PLANS

from db.core import (
    OWNER_USERNAME,
    ROLE_LEVELS,
    get_connection,
    normalize_username,
    now,
    row_to_dict,
    rows_to_dicts,
)
from db.audit import add_audit_log

def validate_password(password):
    if not password:
        return False, "Bitte Passwort eingeben."

    if len(password) < 8:
        return False, "Passwort muss mindestens 8 Zeichen haben."

    if len(password.encode("utf-8")) > 72:
        return False, "Passwort maximal 72 Zeichen."

    return True, ""


def register_account(
    *,
    username: str,
    email: str,
    password: str,
    full_name: str,
    company: str = "",
    phone: str = "",
    country: str = "",
    use_case: str = "",
    marketing_opt_in: bool = False,
    terms_accepted: bool = False,
    ip_address: str = "",
    user_agent: str = "",
    utm: dict | None = None,
) -> tuple[bool, str, dict | None]:
    """
    Full registration: user account + lead record (CRM snapshot).
    Returns (ok, message, user_dict).
    """
    import json

    username = normalize_username(username)
    email = (email or "").strip().lower()
    full_name = (full_name or "").strip()
    company = (company or "").strip()
    phone = (phone or "").strip()
    country = (country or "").strip()
    use_case = (use_case or "").strip()

    if not terms_accepted:
        return False, "Bitte AGB und Datenschutz bestätigen.", None

    if not username or not email or not password:
        return False, "Bitte alle Pflichtfelder ausfüllen.", None

    if not full_name or len(full_name) < 2:
        full_name = username

    if not use_case:
        use_case = "Sonstiges"

    valid, msg = validate_password(password)
    if not valid:
        return False, msg, None

    conn = get_connection()
    cur = conn.cursor()
    created_at = now()

    try:
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        cur.execute(
            """
            INSERT INTO users (
                username, email, password_hash, plan, tokens,
                automation_unlocked, role, admin_level, is_banned,
                created_at, display_name, company, phone, country,
                use_case, marketing_opt_in
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                created_at,
                full_name,
                company,
                phone,
                country,
                use_case,
                1 if marketing_opt_in else 0,
            ),
        )

        cur.execute(
            """
            INSERT INTO leads (
                username, email, full_name, company, phone, country,
                use_case, marketing_opt_in, terms_accepted, status, source,
                ip_address, user_agent, referrer, utm_json, meta_json,
                created_at, converted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                email,
                full_name,
                company,
                phone,
                country,
                use_case,
                1 if marketing_opt_in else 0,
                1,
                "registered",
                "web_register",
                (ip_address or "")[:120],
                (user_agent or "")[:500],
                "",
                json.dumps(utm or {}, ensure_ascii=False),
                json.dumps({"registration": "email_password"}, ensure_ascii=False),
                created_at,
                created_at,
            ),
        )

        conn.commit()

        user = cur.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        add_audit_log(
            "system",
            "lead_registered",
            username,
            f"{full_name} · {email} · {use_case}",
        )

        return True, "Konto erfolgreich erstellt.", row_to_dict(user)

    except sqlite3.IntegrityError:
        conn.rollback()
        return False, "Benutzername oder E-Mail ist bereits registriert.", None

    except Exception as e:
        conn.rollback()
        return False, f"Registrierung fehlgeschlagen: {e}", None

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


def verify_login_identifier(identifier: str, password: str):
    """Login via username or email address."""
    identifier = (identifier or "").strip()
    if not identifier or not password:
        return False, "Bitte Benutzername/E-Mail und Passwort eingeben.", None

    if "@" in identifier:
        from security import is_valid_email

        if not is_valid_email(identifier):
            return False, "Ungültige E-Mail-Adresse.", None
        conn = get_connection()
        cur = conn.cursor()
        row = cur.execute(
            "SELECT username FROM users WHERE lower(email) = ?",
            (identifier.lower(),),
        ).fetchone()
        conn.close()
        if not row:
            return False, "Kein Konto mit dieser E-Mail.", None
        return verify_login(row["username"], password)

    return verify_login(identifier, password)


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
            oauth_on_existing = (existing["oauth_provider"] or "").strip()
            if oauth_on_existing and oauth_on_existing != provider:
                return (
                    False,
                    "Diese E-Mail ist mit einem anderen Login verknüpft. "
                    "Bitte die ursprüngliche Anmeldemethode nutzen.",
                    None,
                )
            return (
                False,
                "Diese E-Mail ist bereits registriert. "
                "Bitte mit Username und Passwort anmelden — kein automatisches Verknüpfen.",
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


def secure_set_football_plan(actor, target, football_plan):
    if not can_manage_users(actor):
        return False, "Keine Berechtigung."

    ok, msg = can_modify_target(actor, target)
    if not ok:
        return False, msg

    from db.football_billing import set_football_plan

    plan_key = str(football_plan or "none").strip().lower()
    if plan_key not in FOOTBALL_PLANS:
        plan_key = "none"

    set_football_plan(target, plan_key)
    add_audit_log(actor, "set_football_plan", target, plan_key)
    return True, "Football Plan gespeichert."


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

