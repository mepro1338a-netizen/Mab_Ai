"""Aggregated metrics for Admin Control Panel."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from db.audit import list_login_logs
from db.billing import list_purchases, list_usage, usage_summary
from db.core import get_connection, rows_to_dicts
from db.support import list_support_messages
from db.users import list_users

try:
    from db.errors import error_counts_24h, errors_last_24h
except ImportError:
    def error_counts_24h():
        return {"total": 0, "by_category": {}}

    def errors_last_24h(limit=50):
        return []


def _parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "")[:19])
    except ValueError:
        return None


def platform_metrics() -> dict:
    users = list_users()
    tickets = list_support_messages()
    usage = list_usage()
    payments = list_purchases()
    logins = list_login_logs(limit=500)

    since_24h = datetime.utcnow() - timedelta(hours=24)
    since_7d = datetime.utcnow() - timedelta(days=7)

    plans = Counter(str(u.get("plan") or "free") for u in users)
    fb_plans = Counter(str(u.get("football_plan") or "none") for u in users)
    roles = Counter(str(u.get("role") or "user") for u in users)

    new_7d = 0
    active_24h = set()
    for u in users:
        created = _parse_dt(str(u.get("created_at") or ""))
        if created and created >= since_7d:
            new_7d += 1
        last = _parse_dt(str(u.get("last_login") or ""))
        if last and last >= since_24h:
            active_24h.add(u.get("username"))

    revenue_total = sum(float(p.get("amount") or 0) for p in payments)
    revenue_7d = 0.0
    for p in payments:
        created = _parse_dt(str(p.get("created_at") or ""))
        if created and created >= since_7d:
            revenue_7d += float(p.get("amount") or 0)

    usage_24h = 0
    tokens_7d = 0
    for row in usage:
        created = _parse_dt(str(row.get("created_at") or ""))
        if created and created >= since_24h:
            usage_24h += 1
        if created and created >= since_7d:
            tokens_7d += int(row.get("cost_tokens") or 0)

    failed_logins = len([
        l for l in logins
        if not int(l.get("success") or 0)
        and (_parse_dt(str(l.get("created_at") or "")) or datetime.min) >= since_24h
    ])

    premium_users = sum(
        1 for u in users if str(u.get("plan") or "free") not in ("free", "")
    )
    premium_conversions_7d = sum(
        1 for p in payments
        if (_parse_dt(str(p.get("created_at") or "")) or datetime.min) >= since_7d
        and str(p.get("payment_status") or p.get("status") or "") in ("paid", "complete", "completed")
    )
    err_stats = error_counts_24h()

    return {
        "users_total": len(users),
        "users_new_7d": new_7d,
        "users_active_24h": len(active_24h),
        "users_banned": sum(1 for u in users if int(u.get("is_banned") or 0)),
        "tickets_open": sum(
            1 for t in tickets if str(t.get("status") or "") in ("open", "in_progress")
        ),
        "tickets_total": len(tickets),
        "usage_total": len(usage),
        "usage_24h": usage_24h,
        "tokens_7d": tokens_7d,
        "revenue_total": revenue_total,
        "revenue_7d": revenue_7d,
        "payments_count": len(payments),
        "failed_logins_24h": failed_logins,
        "plans": dict(plans),
        "football_plans": dict(fb_plans),
        "roles": dict(roles),
        "football_paid": sum(
            1 for u in users
            if str(u.get("football_plan") or "none") != "none"
        ),
        "premium_users": premium_users,
        "premium_conversions_7d": premium_conversions_7d,
        "errors_24h": err_stats.get("total", 0),
        "errors_by_category": err_stats.get("by_category", {}),
    }


def staff_directory() -> list[dict]:
    users = list_users()
    staff = []
    for u in users:
        role = str(u.get("role") or "user")
        level = int(u.get("admin_level") or 0)
        if level >= 1 or role in ("supporter", "moderator", "admin", "owner"):
            staff.append(u)
    return sorted(staff, key=lambda x: -int(x.get("admin_level") or 0))


def env_health_snapshot() -> list[tuple[str, bool]]:
    import os
    keys = (
        ("APP_BASE_URL", "APP_BASE_URL"),
        ("OPENAI_API_KEY", "OpenAI"),
        ("STRIPE_SECRET_KEY", "Stripe"),
        ("GOOGLE_CLIENT_ID", "Google OAuth"),
        ("OAUTH_STATE_SECRET", "OAuth State"),
        ("FOOTBALL_API_KEY", "Football API"),
    )
    return [(label, bool(os.getenv(key, "").strip())) for key, label in keys]


def football_usage_aggregate() -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT usage_date,
               SUM(api_calls) AS api_calls,
               SUM(ai_analyses) AS ai_analyses,
               COUNT(DISTINCT username) AS active_users
        FROM football_daily_usage
        WHERE usage_date >= date('now', '-7 days')
        GROUP BY usage_date
        ORDER BY usage_date DESC
    """).fetchall()
    conn.close()
    return rows_to_dicts(rows)
