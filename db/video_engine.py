"""Video / Reels engine — jobs, outputs, scheduling, social connections."""
from __future__ import annotations

import json
import uuid
from typing import Any

from db.core import get_connection, now, normalize_username, row_to_dict, rows_to_dicts

JOB_STATUSES = (
    "draft",
    "rendering",
    "ready",
    "scheduled",
    "posted",
    "failed",
    "ready_to_publish",
)

POST_STATUSES = (
    "planned",
    "creating",
    "ready",
    "ready_to_publish",
    "posted",
    "failed",
)


def init_video_engine_tables() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS video_jobs (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        studio_type TEXT NOT NULL,
        prompt TEXT,
        platform TEXT,
        duration_sec INTEGER DEFAULT 7,
        provider TEXT,
        status TEXT DEFAULT 'draft',
        cost_tokens INTEGER DEFAULT 0,
        charge_id TEXT UNIQUE,
        title TEXT,
        caption TEXT,
        hashtags TEXT,
        auto_metadata INTEGER DEFAULT 0,
        error_message TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS video_outputs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT NOT NULL,
        file_path TEXT,
        file_url TEXT,
        mime TEXT DEFAULT 'video/mp4',
        file_size INTEGER DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY (job_id) REFERENCES video_jobs(id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reels (
        id TEXT PRIMARY KEY,
        job_id TEXT,
        username TEXT NOT NULL,
        platform TEXT,
        hook TEXT,
        script_internal TEXT,
        duration_sec INTEGER,
        status TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scheduled_posts (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        job_id TEXT,
        platform TEXT,
        scheduled_at TEXT,
        frequency TEXT,
        prompt_template TEXT,
        hashtag_set TEXT,
        auto_caption INTEGER DEFAULT 1,
        auto_post INTEGER DEFAULT 0,
        user_consent INTEGER DEFAULT 0,
        status TEXT DEFAULT 'planned',
        error_message TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS social_connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        platform TEXT NOT NULL,
        access_token_enc TEXT,
        refresh_token_enc TEXT,
        token_expires_at TEXT,
        scopes TEXT,
        account_label TEXT,
        connected_at TEXT,
        UNIQUE(username, platform)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reel_jobs (
        id TEXT PRIMARY KEY,
        video_job_id TEXT NOT NULL,
        username TEXT NOT NULL,
        platform TEXT,
        duration_sec INTEGER,
        generation_mode TEXT,
        status TEXT,
        retry_count INTEGER DEFAULT 0,
        max_retries INTEGER DEFAULT 2,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    for col, typedef in (
        ("retry_count", "INTEGER DEFAULT 0"),
        ("max_retries", "INTEGER DEFAULT 2"),
        ("generation_mode", "TEXT DEFAULT 'ai'"),
        ("user_consent", "INTEGER DEFAULT 0"),
        ("auto_post", "INTEGER DEFAULT 0"),
        ("scheduled_at", "TEXT"),
    ):
        try:
            cur.execute(f"ALTER TABLE video_jobs ADD COLUMN {col} {typedef}")
        except Exception:
            pass
    for col, typedef in (
        ("retry_count", "INTEGER DEFAULT 0"),
        ("job_id", "TEXT"),
    ):
        try:
            cur.execute(f"ALTER TABLE scheduled_posts ADD COLUMN {col} {typedef}")
        except Exception:
            pass
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_video_jobs_user ON video_jobs(username, created_at DESC)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_video_jobs_status ON video_jobs(username, status)"
    )
    conn.commit()
    conn.close()


def _new_id() -> str:
    return uuid.uuid4().hex[:16]


def create_video_job(
    username: str,
    *,
    studio_type: str,
    prompt: str,
    platform: str,
    duration_sec: int,
    provider: str,
    cost_tokens: int = 0,
    charge_id: str | None = None,
    auto_metadata: bool = False,
    status: str = "draft",
) -> dict[str, Any]:
    job_id = _new_id()
    ts = now()
    cid = charge_id or f"chg_{job_id}"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO video_jobs (
            id, username, studio_type, prompt, platform, duration_sec,
            provider, status, cost_tokens, charge_id, auto_metadata,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            job_id,
            normalize_username(username),
            studio_type,
            prompt[:4000],
            platform,
            int(duration_sec),
            provider,
            status,
            int(cost_tokens),
            cid,
            1 if auto_metadata else 0,
            ts,
            ts,
        ),
    )
    if studio_type == "reel":
        cur.execute(
            """
            INSERT INTO reels (id, job_id, username, platform, duration_sec, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (job_id, job_id, normalize_username(username), platform, int(duration_sec), status, ts, ts),
        )
        try:
            cur.execute(
                """
                INSERT OR REPLACE INTO reel_jobs (
                    id, video_job_id, username, platform, duration_sec,
                    generation_mode, status, retry_count, max_retries, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 'ai', ?, 0, 2, ?, ?)
                """,
                (job_id, job_id, normalize_username(username), platform, int(duration_sec), status, ts, ts),
            )
        except Exception:
            pass
    conn.commit()
    conn.close()
    return get_video_job(job_id) or {}


def get_video_job(job_id: str) -> dict[str, Any] | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM video_jobs WHERE id = ?", (job_id,))
    row = cur.fetchone()
    conn.close()
    return row_to_dict(row)


def update_video_job(job_id: str, **fields: Any) -> None:
    allowed = {
        "status", "provider", "cost_tokens", "title", "caption", "hashtags",
        "error_message", "duration_sec", "prompt", "platform",
        "retry_count", "generation_mode", "user_consent", "auto_post", "scheduled_at",
    }
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    updates["updated_at"] = now()
    cols = ", ".join(f"{k} = ?" for k in updates)
    vals = list(updates.values()) + [job_id]
    conn = get_connection()
    conn.execute(f"UPDATE video_jobs SET {cols} WHERE id = ?", vals)
    conn.commit()
    conn.close()
    job = get_video_job(job_id)
    if job and job.get("studio_type") == "reel":
        conn = get_connection()
        st = updates.get("status")
        if st:
            conn.execute(
                "UPDATE reels SET status = ?, updated_at = ? WHERE job_id = ?",
                (st, now(), job_id),
            )
            conn.commit()
        conn.close()


def list_video_jobs(
    username: str,
    *,
    studio_type: str | None = None,
    limit: int = 40,
) -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    if studio_type:
        cur.execute(
            """
            SELECT * FROM video_jobs WHERE username = ? AND studio_type = ?
            ORDER BY created_at DESC LIMIT ?
            """,
            (normalize_username(username), studio_type, limit),
        )
    else:
        cur.execute(
            """
            SELECT * FROM video_jobs WHERE username = ?
            ORDER BY created_at DESC LIMIT ?
            """,
            (normalize_username(username), limit),
        )
    rows = cur.fetchall()
    conn.close()
    return rows_to_dicts(rows)


def add_video_output(
    job_id: str,
    *,
    file_path: str = "",
    file_url: str = "",
    mime: str = "video/mp4",
    file_size: int = 0,
) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO video_outputs (job_id, file_path, file_url, mime, file_size, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (job_id, file_path, file_url, mime, int(file_size), now()),
    )
    conn.commit()
    conn.close()


def get_latest_output(job_id: str) -> dict[str, Any] | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM video_outputs WHERE job_id = ?
        ORDER BY id DESC LIMIT 1
        """,
        (job_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row_to_dict(row)


def charge_id_used(charge_id: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM video_jobs WHERE charge_id = ? AND cost_tokens > 0 AND status NOT IN ('draft','failed')",
        (charge_id,),
    )
    ok = cur.fetchone() is not None
    conn.close()
    return ok


def create_scheduled_post(
    username: str,
    *,
    job_id: str = "",
    platform: str,
    scheduled_at: str,
    frequency: str = "daily",
    prompt_template: str = "",
    hashtag_set: str = "",
    auto_caption: bool = True,
    auto_post: bool = False,
    user_consent: bool = False,
) -> dict[str, Any]:
    post_id = _new_id()
    ts = now()
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO scheduled_posts (
            id, username, job_id, platform, scheduled_at, frequency,
            prompt_template, hashtag_set, auto_caption, auto_post, user_consent,
            status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'planned', ?, ?)
        """,
        (
            post_id,
            normalize_username(username),
            job_id,
            platform,
            scheduled_at,
            frequency,
            prompt_template[:2000],
            hashtag_set[:500],
            1 if auto_caption else 0,
            1 if auto_post else 0,
            1 if user_consent else 0,
            ts,
            ts,
        ),
    )
    conn.commit()
    conn.close()
    return get_scheduled_post(post_id) or {}


def get_scheduled_post(post_id: str) -> dict[str, Any] | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scheduled_posts WHERE id = ?", (post_id,))
    row = cur.fetchone()
    conn.close()
    return row_to_dict(row)


def update_scheduled_post(post_id: str, **fields: Any) -> None:
    allowed = {"status", "job_id", "error_message", "scheduled_at"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    updates["updated_at"] = now()
    cols = ", ".join(f"{k} = ?" for k in updates)
    vals = list(updates.values()) + [post_id]
    conn = get_connection()
    conn.execute(f"UPDATE scheduled_posts SET {cols} WHERE id = ?", vals)
    conn.commit()
    conn.close()


def list_scheduled_posts(username: str, *, limit: int = 50) -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM scheduled_posts WHERE username = ?
        ORDER BY scheduled_at ASC, created_at DESC LIMIT ?
        """,
        (normalize_username(username), limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows_to_dicts(rows)


def save_social_connection(
    username: str,
    platform: str,
    *,
    access_token_enc: str = "",
    refresh_token_enc: str = "",
    token_expires_at: str = "",
    scopes: str = "",
    account_label: str = "",
) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO social_connections (
            username, platform, access_token_enc, refresh_token_enc,
            token_expires_at, scopes, account_label, connected_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(username, platform) DO UPDATE SET
            access_token_enc = excluded.access_token_enc,
            refresh_token_enc = excluded.refresh_token_enc,
            token_expires_at = excluded.token_expires_at,
            scopes = excluded.scopes,
            account_label = excluded.account_label,
            connected_at = excluded.connected_at
        """,
        (
            normalize_username(username),
            platform,
            access_token_enc,
            refresh_token_enc,
            token_expires_at,
            scopes,
            account_label,
            now(),
        ),
    )
    conn.commit()
    conn.close()


def get_social_connection(username: str, platform: str) -> dict[str, Any] | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM social_connections
        WHERE username = ? AND platform = ?
        """,
        (normalize_username(username), platform),
    )
    row = cur.fetchone()
    conn.close()
    return row_to_dict(row)


def list_social_connections(username: str) -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM social_connections WHERE username = ? ORDER BY platform",
        (normalize_username(username),),
    )
    rows = cur.fetchall()
    conn.close()
    return rows_to_dicts(rows)


def delete_social_connection(username: str, platform: str) -> None:
    conn = get_connection()
    conn.execute(
        "DELETE FROM social_connections WHERE username = ? AND platform = ?",
        (normalize_username(username), platform),
    )
    conn.commit()
    conn.close()
