"""Football Premium plan and daily usage tracking."""
from datetime import date

from config import (
    FOOTBALL_PLANS,
    football_daily_ai_limit,
    football_daily_api_limit,
)

from db.core import get_connection, normalize_username, row_to_dict
from db.users import get_user


def _today() -> str:
    return date.today().isoformat()


def get_football_plan(username: str) -> str:
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
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET football_plan = ? WHERE username = ?",
        (plan_key, username),
    )
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
        """
        SELECT api_calls FROM football_daily_usage
        WHERE username = ? AND usage_date = ?
        """,
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
        """
        SELECT ai_analyses FROM football_daily_usage
        WHERE username = ? AND usage_date = ?
        """,
        (username, usage_date),
    ).fetchone()
    conn.close()
    return int(row["ai_analyses"] if row else 1)


def record_football_ai_actions(username: str, amount: int) -> int:
    """Backward-compatible alias."""
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
