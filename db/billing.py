"""Redeem codes, usage analytics, payments."""
import secrets
import sqlite3
from datetime import datetime, timedelta

from db.core import get_connection, normalize_username, now, rows_to_dicts

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
        plan_value = str(item["plan"])
        if plan_value.startswith("football_"):
            from db.football_billing import set_football_plan

            set_football_plan(username, plan_value)
        else:
            cur.execute(
                "UPDATE users SET plan = ? WHERE username = ?",
                (plan_value, username),
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


def payment_already_paid(session_id: str) -> bool:
    session_id = str(session_id or "").strip()
    if not session_id:
        return False

    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute(
        """
        SELECT id FROM payments
        WHERE stripe_session_id = ? AND payment_status = 'paid'
        LIMIT 1
        """,
        (session_id,),
    ).fetchone()
    conn.close()
    return bool(row)


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

