import uuid
from datetime import datetime

from database import get_connection, rows_to_dicts


def now():
    return datetime.utcnow().isoformat()


def ensure_queue_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT,
        username TEXT,
        job_type TEXT,
        payload TEXT,
        status TEXT DEFAULT 'queued',
        result TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_job(username, job_type, payload=""):
    ensure_queue_tables()

    conn = get_connection()
    cur = conn.cursor()

    job_id = str(uuid.uuid4())

    cur.execute("""
    INSERT INTO jobs (
        job_id,
        username,
        job_type,
        payload,
        status,
        result,
        created_at,
        updated_at
    )
    VALUES (?, ?, ?, ?, 'queued', '', ?, ?)
    """, (
        job_id,
        username,
        job_type,
        payload,
        now(),
        now(),
    ))

    conn.commit()
    conn.close()

    return job_id


def update_job(job_id, status, result=""):
    ensure_queue_tables()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE jobs
    SET status = ?, result = ?, updated_at = ?
    WHERE job_id = ?
    """, (
        status,
        result,
        now(),
        job_id,
    ))

    conn.commit()
    conn.close()


def list_jobs(username=None, limit=100):
    ensure_queue_tables()

    conn = get_connection()
    cur = conn.cursor()

    if username:
        cur.execute("""
        SELECT * FROM jobs
        WHERE username = ?
        ORDER BY id DESC
        LIMIT ?
        """, (
            username,
            int(limit),
        ))
    else:
        cur.execute("""
        SELECT * FROM jobs
        ORDER BY id DESC
        LIMIT ?
        """, (
            int(limit),
        ))

    rows = cur.fetchall()

    conn.close()

    return rows_to_dicts(rows)

def list_user_jobs(username, limit=50):

    jobs = list_jobs(
        username=username,
        limit=limit,
    )

    return jobs