"""Projects, project memory, chat memory."""
from db.core import get_connection, normalize_username, now, row_to_dict, rows_to_dicts

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

