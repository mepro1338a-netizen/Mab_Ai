"""Consolidated DB helpers (Phase 2 minimization).

This module merges the small db/* modules into one place to reduce file count.
Large modules (`db.users`, `db.video_engine`) stay split for now.
"""

from __future__ import annotations

import json
import secrets
from datetime import date, datetime, timedelta
from typing import Any

from config import FOOTBALL_PLANS, football_daily_ai_limit, football_daily_api_limit
from db.core import (
    OWNER_USERNAME,
    get_connection,
    normalize_username,
    now,
    row_to_dict,
    rows_to_dicts,
)
from db.video_engine import (
    create_video_job,
    get_latest_output,
    get_video_job,
    list_video_jobs,
    update_video_job,
)

# ---------------------------------------------------------------------------
# audit.py (merged)
# ---------------------------------------------------------------------------


def record_login_event(username, ip_address: str = "", user_agent: str = "", success: bool = True) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO login_logs (username, ip_address, user_agent, success, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            normalize_username(username),
            ip_address,
            user_agent,
            1 if success else 0,
            now(),
        ),
    )
    conn.commit()
    conn.close()


def list_login_logs(username: str | None = None, limit: int = 200) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    if username:
        rows = cur.execute(
            """
            SELECT * FROM login_logs
            WHERE username = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (normalize_username(username), int(limit)),
        ).fetchall()
    else:
        rows = cur.execute(
            """
            SELECT * FROM login_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (int(limit),),
        ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def clear_login_logs() -> None:
    conn = get_connection()
    conn.execute("DELETE FROM login_logs")
    conn.commit()
    conn.close()


def add_audit_log(actor, action, target: str = "", details: str = "") -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO audit_logs (actor, action, target, details, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            normalize_username(actor) or str(actor or ""),
            str(action or "")[:120],
            str(target or "")[:120],
            str(details or "")[:2000],
            now(),
        ),
    )
    conn.commit()
    conn.close()


def list_audit_logs(limit: int = 200) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT * FROM audit_logs
        ORDER BY id DESC
        LIMIT ?
        """,
        (int(limit),),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# automations.py (merged)
# ---------------------------------------------------------------------------


def ensure_automation_tables() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
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
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS automation_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            automation_id INTEGER,
            username TEXT,
            status TEXT,
            result TEXT,
            created_at TEXT
        )
        """
    )
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
) -> int:
    ensure_automation_tables()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO automations (
            username, project_id, name, automation_type, source_workspace,
            target_workspace, trigger_text, status, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
        """,
        (
            normalize_username(username),
            int(project_id or 0),
            name,
            automation_type,
            source_workspace,
            target_workspace,
            trigger_text,
            now(),
            now(),
        ),
    )
    conn.commit()
    automation_id = int(cur.lastrowid)
    conn.close()
    return automation_id


def list_automations(username: str | None = None) -> list[dict]:
    ensure_automation_tables()
    conn = get_connection()
    cur = conn.cursor()
    if username:
        rows = cur.execute(
            """
            SELECT * FROM automations
            WHERE username = ?
            ORDER BY id DESC
            """,
            (normalize_username(username),),
        ).fetchall()
    else:
        rows = cur.execute(
            """
            SELECT * FROM automations
            ORDER BY id DESC
            """
        ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def update_automation_status(automation_id, status) -> None:
    ensure_automation_tables()
    conn = get_connection()
    conn.execute(
        "UPDATE automations SET status = ?, updated_at = ? WHERE id = ?",
        (status, now(), int(automation_id)),
    )
    conn.commit()
    conn.close()


def create_automation_run(automation_id, username, status, result: str = "") -> int:
    ensure_automation_tables()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO automation_runs (automation_id, username, status, result, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (int(automation_id), normalize_username(username), status, result, now()),
    )
    conn.commit()
    run_id = int(cur.lastrowid)
    conn.close()
    return run_id


def list_automation_runs(username: str | None = None, limit: int = 100) -> list[dict]:
    ensure_automation_tables()
    conn = get_connection()
    cur = conn.cursor()
    if username:
        rows = cur.execute(
            """
            SELECT * FROM automation_runs
            WHERE username = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (normalize_username(username), int(limit)),
        ).fetchall()
    else:
        rows = cur.execute(
            """
            SELECT * FROM automation_runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (int(limit),),
        ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# projects.py (merged)
# ---------------------------------------------------------------------------


def ensure_project_tables() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            title TEXT,
            description TEXT,
            workspace TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS project_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            username TEXT,
            workspace TEXT,
            memory_type TEXT,
            content TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def create_project(username, title, description: str = "", workspace: str = "general") -> int:
    ensure_project_tables()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO projects (username, title, description, workspace, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (normalize_username(username), title, description, workspace, now(), now()),
    )
    conn.commit()
    project_id = int(cur.lastrowid)
    conn.close()
    return project_id


def list_projects(username) -> list[dict]:
    ensure_project_tables()
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT * FROM projects
        WHERE username = ?
        ORDER BY id DESC
        """,
        (normalize_username(username),),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def get_project(project_id, username: str | None = None) -> dict | None:
    ensure_project_tables()
    conn = get_connection()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (int(project_id),)).fetchone()
    conn.close()
    project = row_to_dict(row)
    if not project:
        return None
    if username and normalize_username(project.get("username")) != normalize_username(username):
        return None
    return project


def save_project_memory(project_id, username, workspace, memory_type, content) -> None:
    ensure_project_tables()
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO project_memory (project_id, username, workspace, memory_type, content, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (int(project_id), normalize_username(username), workspace, memory_type, content, now()),
    )
    conn.commit()
    conn.close()


def list_project_memory(project_id) -> list[dict]:
    ensure_project_tables()
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM project_memory
        WHERE project_id = ?
        ORDER BY id DESC
        """,
        (int(project_id),),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# project chat memory (required by pages/chat.py)
# ---------------------------------------------------------------------------


def ensure_chat_memory_tables() -> None:
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS project_chat_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            username TEXT,
            role TEXT,
            message TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_project_chat_message(project_id, username, role, message) -> None:
    ensure_chat_memory_tables()
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO project_chat_memory (project_id, username, role, message, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (int(project_id), normalize_username(username), role, message, now()),
    )
    conn.commit()
    conn.close()


def list_project_chat_memory(project_id, limit: int = 30) -> list[dict]:
    ensure_chat_memory_tables()
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM project_chat_memory
        WHERE project_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (int(project_id), int(limit)),
    ).fetchall()
    conn.close()
    out = rows_to_dicts(rows)
    out.reverse()
    return out


# ---------------------------------------------------------------------------
# leads.py (merged)
# ---------------------------------------------------------------------------


def init_leads_table() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT NOT NULL,
            full_name TEXT,
            company TEXT,
            phone TEXT,
            country TEXT,
            use_case TEXT,
            marketing_opt_in INTEGER DEFAULT 0,
            terms_accepted INTEGER DEFAULT 0,
            status TEXT DEFAULT 'registered',
            source TEXT DEFAULT 'web_register',
            ip_address TEXT,
            user_agent TEXT,
            referrer TEXT,
            utm_json TEXT,
            meta_json TEXT,
            created_at TEXT,
            converted_at TEXT
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_username ON leads(username)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at DESC)")
    conn.commit()
    conn.close()


def save_lead(
    *,
    username: str,
    email: str,
    full_name: str,
    company: str = "",
    phone: str = "",
    country: str = "",
    use_case: str = "",
    marketing_opt_in: bool = False,
    terms_accepted: bool = False,
    ip_address: str = "",
    user_agent: str = "",
    referrer: str = "",
    utm: dict | None = None,
    meta: dict | None = None,
    status: str = "registered",
) -> int | None:
    conn = get_connection()
    cur = conn.cursor()
    try:
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
                normalize_username(username),
                (email or "").strip().lower(),
                (full_name or "").strip(),
                (company or "").strip(),
                (phone or "").strip(),
                (country or "").strip(),
                (use_case or "").strip(),
                1 if marketing_opt_in else 0,
                1 if terms_accepted else 0,
                status,
                "web_register",
                (ip_address or "").strip()[:120],
                (user_agent or "").strip()[:500],
                (referrer or "").strip()[:500],
                json.dumps(utm or {}, ensure_ascii=False),
                json.dumps(meta or {}, ensure_ascii=False),
                now(),
                now() if status == "registered" else None,
            ),
        )
        lead_id = int(cur.lastrowid)
        conn.commit()
        return lead_id
    except Exception:
        conn.rollback()
        return None
    finally:
        conn.close()


def list_leads(*, limit: int = 200) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM leads ORDER BY id DESC LIMIT ?",
        (int(limit),),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def lead_count() -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) AS c FROM leads").fetchone()
    conn.close()
    return int(row["c"] or 0) if row else 0


# ---------------------------------------------------------------------------
# errors.py (merged)
# ---------------------------------------------------------------------------


def record_app_error(
    category: str,
    error_type: str,
    message: str,
    *,
    page: str = "",
    username: str = "",
) -> None:
    msg = (message or "")[:500]
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO app_error_logs (category, error_type, message, page, username, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            (category or "system")[:40],
            (error_type or "Error")[:80],
            msg,
            (page or "")[:60],
            (username or "")[:80],
            now(),
        ),
    )
    conn.commit()
    conn.close()


def errors_last_24h(limit: int = 50) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM app_error_logs
        WHERE created_at >= datetime('now', '-1 day')
        ORDER BY id DESC
        LIMIT ?
        """,
        (int(limit),),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def error_counts_24h() -> dict:
    conn = get_connection()
    cur = conn.cursor()
    total = cur.execute(
        """
        SELECT COUNT(*) AS c FROM app_error_logs
        WHERE created_at >= datetime('now', '-1 day')
        """
    ).fetchone()["c"]
    by_cat = cur.execute(
        """
        SELECT category, COUNT(*) AS c FROM app_error_logs
        WHERE created_at >= datetime('now', '-1 day')
        GROUP BY category
        ORDER BY c DESC
        """
    ).fetchall()
    conn.close()
    return {"total": total, "by_category": {r["category"]: r["c"] for r in by_cat}}


# ---------------------------------------------------------------------------
# memory.py (merged)
# ---------------------------------------------------------------------------


def ensure_global_memory_tables() -> None:
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS global_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            memory_type TEXT,
            content TEXT,
            importance INTEGER DEFAULT 1,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_global_memory(username, memory_type, content, importance: int = 1) -> None:
    ensure_global_memory_tables()
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO global_memory (username, memory_type, content, importance, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (normalize_username(username), memory_type, content, int(importance), now()),
    )
    conn.commit()
    conn.close()


def list_global_memory(username, limit: int = 100) -> list[dict]:
    ensure_global_memory_tables()
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM global_memory
        WHERE username = ?
        ORDER BY importance DESC, id DESC
        LIMIT ?
        """,
        (normalize_username(username), int(limit)),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def search_global_memory(username, query, limit: int = 10) -> list[dict]:
    ensure_global_memory_tables()
    conn = get_connection()
    q = f"%{(query or '').lower()}%"
    rows = conn.execute(
        """
        SELECT * FROM global_memory
        WHERE username = ?
        AND LOWER(content) LIKE ?
        ORDER BY importance DESC, id DESC
        LIMIT ?
        """,
        (normalize_username(username), q, int(limit)),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def unlock_automation(username) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE users SET automation_unlocked = 1 WHERE username = ?",
        (normalize_username(username),),
    )
    conn.commit()
    conn.close()


def has_automation_access(username) -> bool:
    from db.users import get_user

    user = get_user(username)
    if not user:
        return False
    return int(user.get("automation_unlocked") or 0) == 1


# ---------------------------------------------------------------------------
# billing.py (merged)
# ---------------------------------------------------------------------------


def create_redeem_code(
    code_type,
    value: str = "",
    tokens: int = 0,
    plan: str = "",
    max_uses: int = 1,
    created_by: str = "",
    days_valid: int = 30,
):
    code = secrets.token_hex(4).upper()
    expires_at = (datetime.utcnow() + timedelta(days=int(days_valid))).isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO redeem_codes (
            code, code_type, plan, tokens, max_uses, used_count, created_by,
            expires_at, is_active, created_at
        )
        VALUES (?, ?, ?, ?, ?, 0, ?, ?, 1, ?)
        """,
        (
            code,
            code_type,
            plan,
            int(tokens or 0),
            int(max_uses or 1),
            normalize_username(created_by),
            expires_at,
            now(),
        ),
    )
    conn.commit()
    conn.close()
    return code


def save_usage(
    username,
    tool,
    prompt,
    tokens_used: int = 0,
    cost_tokens: int = 0,
    api_provider: str = "",
    status: str = "success",
) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO usage_logs (username, tool, prompt, tokens_used, cost_tokens, api_provider, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            normalize_username(username),
            tool,
            prompt,
            int(tokens_used or 0),
            int(cost_tokens or 0),
            api_provider,
            status,
            now(),
        ),
    )
    conn.commit()
    conn.close()


def list_usage(username: str | None = None) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    if username:
        rows = cur.execute(
            "SELECT * FROM usage_logs WHERE username = ? ORDER BY id DESC",
            (normalize_username(username),),
        ).fetchall()
    else:
        rows = cur.execute("SELECT * FROM usage_logs ORDER BY id DESC").fetchall()
    conn.close()
    return rows_to_dicts(rows)


def list_purchases(username: str | None = None) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    if username:
        rows = cur.execute(
            "SELECT * FROM payments WHERE username = ? ORDER BY id DESC",
            (normalize_username(username),),
        ).fetchall()
    else:
        rows = cur.execute("SELECT * FROM payments ORDER BY id DESC").fetchall()
    conn.close()
    return rows_to_dicts(rows)


def spend_tokens(username: str, amount: int) -> tuple[bool, str]:
    amount = max(0, int(amount or 0))
    if amount <= 0:
        return True, "OK"
    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT tokens FROM users WHERE username = ?",
        (normalize_username(username),),
    ).fetchone()
    current = int(row["tokens"] or 0) if row else 0
    if current < amount:
        conn.close()
        return False, "Nicht genug Tokens."
    cur.execute(
        "UPDATE users SET tokens = tokens - ? WHERE username = ?",
        (amount, normalize_username(username)),
    )
    conn.commit()
    conn.close()
    return True, "OK"


def update_tokens(username: str, tokens: int) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE users SET tokens = ? WHERE username = ?",
        (int(tokens or 0), normalize_username(username)),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# reel_jobs.py (merged)
# ---------------------------------------------------------------------------


REEL_STATUSES = (
    "draft",
    "queued",
    "rendering",
    "ready",
    "ready_to_publish",
    "scheduled",
    "posted",
    "failed",
)


def create_reel_job(
    username: str,
    *,
    prompt: str,
    platform: str,
    duration_sec: int,
    provider: str = "",
    cost_tokens: int = 0,
    charge_id: str | None = None,
    generation_mode: str = "ai",
    auto_metadata: bool = True,
    user_consent: int = 0,
    auto_post: int = 0,
    scheduled_at: str = "",
) -> dict[str, Any]:
    job = create_video_job(
        username,
        studio_type="reel",
        prompt=prompt,
        platform=platform,
        duration_sec=duration_sec,
        provider=provider,
        cost_tokens=cost_tokens,
        charge_id=charge_id,
        auto_metadata=auto_metadata,
        status="queued",
    )
    fields: dict[str, Any] = {"generation_mode": generation_mode}
    if user_consent:
        fields["user_consent"] = 1
    if auto_post:
        fields["auto_post"] = 1
    if scheduled_at:
        fields["scheduled_at"] = scheduled_at
    update_video_job(job["id"], **fields)
    return get_video_job(job["id"]) or job


def get_reel_job(job_id: str) -> dict[str, Any] | None:
    job = get_video_job(job_id)
    if job and job.get("studio_type") == "reel":
        job["output"] = get_latest_output(job_id)
        return job
    return None


def list_reel_jobs(username: str, *, status: str | None = None, limit: int = 50) -> list[dict]:
    jobs = list_video_jobs(username, studio_type="reel", limit=limit)
    if status:
        jobs = [j for j in jobs if j.get("status") == status]
    return jobs


def list_queued_reel_jobs(username: str, limit: int = 10) -> list[dict]:
    return list_reel_jobs(username, status="queued", limit=limit)


def update_reel_job(job_id: str, **fields: Any) -> None:
    update_video_job(job_id, **fields)


# ---------------------------------------------------------------------------
# football_billing.py + bootstrap.py (merged)
# ---------------------------------------------------------------------------


def _today() -> str:
    return date.today().isoformat()


def get_football_plan(username: str) -> str:
    from db.users import get_user

    user = get_user(username)
    if not user:
        return "none"
    plan = str(user.get("football_plan") or "none").strip().lower()
    if plan not in FOOTBALL_PLANS:
        return "none"
    return plan


def set_football_plan(username: str, plan_key: str) -> None:
    username = normalize_username(username)
    plan_key = str(plan_key or "none").strip().lower()
    if plan_key not in FOOTBALL_PLANS:
        plan_key = "none"
    conn = get_connection()
    conn.execute("UPDATE users SET football_plan = ? WHERE username = ?", (plan_key, username))
    conn.commit()
    conn.close()


def _ensure_usage_row(cur, username: str, usage_date: str) -> None:
    cur.execute(
        """
        INSERT INTO football_daily_usage (username, usage_date, api_calls, ai_actions, ai_analyses)
        SELECT ?, ?, 0, 0, 0
        WHERE NOT EXISTS (
            SELECT 1 FROM football_daily_usage
            WHERE username = ? AND usage_date = ?
        )
        """,
        (username, usage_date, username, usage_date),
    )


def get_football_usage_today(username: str) -> dict:
    username = normalize_username(username)
    usage_date = _today()
    conn = get_connection()
    cur = conn.cursor()
    _ensure_usage_row(cur, username, usage_date)
    conn.commit()
    row = cur.execute(
        """
        SELECT api_calls, ai_actions, ai_analyses FROM football_daily_usage
        WHERE username = ? AND usage_date = ?
        """,
        (username, usage_date),
    ).fetchone()
    conn.close()
    data = row_to_dict(row) if row else {}
    analyses = int(data.get("ai_analyses") or data.get("ai_actions") or 0)
    return {
        "api_calls": int(data.get("api_calls") or 0),
        "ai_actions": int(data.get("ai_actions") or 0),
        "ai_analyses": analyses,
        "usage_date": usage_date,
    }


def record_football_api_call(username: str, count: int = 1) -> int:
    username = normalize_username(username)
    usage_date = _today()
    count = max(1, int(count or 1))
    conn = get_connection()
    cur = conn.cursor()
    _ensure_usage_row(cur, username, usage_date)
    cur.execute(
        """
        UPDATE football_daily_usage
        SET api_calls = api_calls + ?
        WHERE username = ? AND usage_date = ?
        """,
        (count, username, usage_date),
    )
    conn.commit()
    row = cur.execute(
        "SELECT api_calls FROM football_daily_usage WHERE username = ? AND usage_date = ?",
        (username, usage_date),
    ).fetchone()
    conn.close()
    return int(row["api_calls"] if row else count)


def record_football_ai_analysis(username: str) -> int:
    username = normalize_username(username)
    usage_date = _today()
    conn = get_connection()
    cur = conn.cursor()
    _ensure_usage_row(cur, username, usage_date)
    cur.execute(
        """
        UPDATE football_daily_usage
        SET ai_analyses = ai_analyses + 1, ai_actions = ai_actions + 1
        WHERE username = ? AND usage_date = ?
        """,
        (username, usage_date),
    )
    conn.commit()
    row = cur.execute(
        "SELECT ai_analyses FROM football_daily_usage WHERE username = ? AND usage_date = ?",
        (username, usage_date),
    ).fetchone()
    conn.close()
    return int(row["ai_analyses"] if row else 1)


def record_football_ai_actions(username: str, amount: int) -> int:
    for _ in range(max(1, int(amount or 1))):
        record_football_ai_analysis(username)
    return get_football_usage_today(username)["ai_analyses"]


def football_plan_limits(plan_key: str) -> dict:
    plan_key = plan_key if plan_key in FOOTBALL_PLANS else "none"
    return {
        "api_limit": football_daily_api_limit(plan_key),
        "ai_limit": football_daily_ai_limit(plan_key),
        "tier": FOOTBALL_PLANS.get(plan_key, {}).get("tier", 0),
    }


def force_owner_account() -> None:
    from db.users import get_user, set_plan, set_role

    user = get_user(OWNER_USERNAME)
    if not user:
        return
    if user.get("role") != "owner" or int(user.get("admin_level") or 0) != 1337:
        set_role(OWNER_USERNAME, "owner", 1337)
    if user.get("plan") != "elite":
        set_plan(OWNER_USERNAME, "elite")
        set_football_plan(OWNER_USERNAME, "football_elite")

