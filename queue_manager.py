# =========================================================
# queue_manager.py
# =========================================================

import sqlite3
import uuid
from datetime import datetime

from config import DB_PATH


def now():
    return datetime.utcnow().isoformat()


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_queue():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS generation_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE,
            username TEXT,
            tool TEXT,
            prompt TEXT,
            status TEXT DEFAULT 'pending',
            tokens_charged INTEGER DEFAULT 0,
            provider TEXT,
            result TEXT,
            error TEXT,
            created_at TEXT,
            started_at TEXT,
            finished_at TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def create_job(username, tool, prompt, tokens_charged=0, provider="openai"):
    init_queue()

    job_id = str(uuid.uuid4())

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO generation_queue (
            job_id,
            username,
            tool,
            prompt,
            status,
            tokens_charged,
            provider,
            created_at
        )
        VALUES (?, ?, ?, ?, 'pending', ?, ?, ?)
        """,
        (
            job_id,
            username,
            tool,
            prompt,
            int(tokens_charged),
            provider,
            now(),
        ),
    )

    conn.commit()
    conn.close()

    return job_id


def list_user_jobs(username, limit=25):
    init_queue()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM generation_queue
        WHERE username = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (username, int(limit)),
    )

    rows = cur.fetchall()
    conn.close()

    return [dict(r) for r in rows]


def count_active_jobs(username):
    init_queue()

    conn = get_connection()
    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT COUNT(*) AS c
        FROM generation_queue
        WHERE username = ?
        AND status IN ('pending', 'processing')
        """,
        (username,),
    ).fetchone()

    conn.close()

    return int(row["c"] or 0)


def update_job_status(job_id, status, result=None, error=None):
    init_queue()

    conn = get_connection()
    cur = conn.cursor()

    if status == "processing":
        cur.execute(
            """
            UPDATE generation_queue
            SET status = ?, started_at = ?
            WHERE job_id = ?
            """,
            (status, now(), job_id),
        )

    elif status in ["finished", "failed"]:
        cur.execute(
            """
            UPDATE generation_queue
            SET status = ?, result = ?, error = ?, finished_at = ?
            WHERE job_id = ?
            """,
            (status, result, error, now(), job_id),
        )

    else:
        cur.execute(
            """
            UPDATE generation_queue
            SET status = ?
            WHERE job_id = ?
            """,
            (status, job_id),
        )

    conn.commit()
    conn.close()


def get_job(job_id):
    init_queue()

    conn = get_connection()
    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT *
        FROM generation_queue
        WHERE job_id = ?
        """,
        (job_id,),
    ).fetchone()

    conn.close()

    return dict(row) if row else None