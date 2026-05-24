"""Login logs and admin audit trail."""
from db.core import get_connection, normalize_username, now, rows_to_dicts

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
