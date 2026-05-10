from datetime import datetime, timedelta

from queue_manager import count_active_jobs
from database import list_usage


PLAN_LIMITS = {
    "free": {
        "active_jobs": 1,
        "daily_generations": 10,
    },
    "pro": {
        "active_jobs": 2,
        "daily_generations": 60,
    },
    "grand": {
        "active_jobs": 3,
        "daily_generations": 150,
    },
    "elite": {
        "active_jobs": 5,
        "daily_generations": 500,
    },
}


def today_iso():
    return datetime.utcnow().date().isoformat()


def daily_usage_count(username):
    logs = list_usage(username)
    today = today_iso()

    count = 0

    for log in logs:
        created = str(log.get("created_at", ""))
        status = str(log.get("status", ""))

        if created.startswith(today) and status in ["success", "charged"]:
            count += 1

    return count


def check_generation_allowed(username, plan):
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])

    active = count_active_jobs(username)

    if active >= limits["active_jobs"]:
        return False, f"Zu viele aktive Jobs. Limit: {limits['active_jobs']}"

    used_today = daily_usage_count(username)

    if used_today >= limits["daily_generations"]:
        return False, f"Tageslimit erreicht: {used_today}/{limits['daily_generations']}"

    return True, "OK"