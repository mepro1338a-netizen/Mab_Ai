"""Automations and runs."""
from db.core import get_connection, normalize_username, now, rows_to_dicts

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

