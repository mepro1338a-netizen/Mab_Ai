# =========================================================
# abuse_guard.py
# =========================================================

from datetime import datetime

from queue_manager import count_active_jobs
from database import list_usage


# =========================================================
# PLAN LIMITS
# =========================================================

PLAN_LIMITS = {
    "free": {
        "active_jobs": 1,
        "daily_generations": 10,
        "max_prompt_length": 1000,
    },

    "pro": {
        "active_jobs": 2,
        "daily_generations": 60,
        "max_prompt_length": 3000,
    },

    "grand": {
        "active_jobs": 3,
        "daily_generations": 150,
        "max_prompt_length": 6000,
    },

    "elite": {
        "active_jobs": 5,
        "daily_generations": 500,
        "max_prompt_length": 12000,
    },
}


# =========================================================
# HELPERS
# =========================================================

def today_iso():
    return datetime.utcnow().date().isoformat()


# =========================================================
# DAILY USAGE
# =========================================================

def daily_usage_count(username):
    logs = list_usage(username)
    today = today_iso()

    count = 0

    for log in logs:
        created = str(log.get("created_at", ""))
        status = str(log.get("status", ""))

        if (
            created.startswith(today)
            and status in ["success", "charged"]
        ):
            count += 1

    return count


# =========================================================
# CHECK GENERATION
# =========================================================

def check_generation_allowed(username, plan):
    limits = PLAN_LIMITS.get(
        plan,
        PLAN_LIMITS["free"],
    )

    # -------------------------
    # ACTIVE JOBS
    # -------------------------

    active = count_active_jobs(username)

    if active >= limits["active_jobs"]:
        return (
            False,
            f"Zu viele aktive Jobs. "
            f"Limit: {limits['active_jobs']}"
        )

    # -------------------------
    # DAILY LIMIT
    # -------------------------

    used_today = daily_usage_count(username)

    if used_today >= limits["daily_generations"]:
        return (
            False,
            f"Tageslimit erreicht: "
            f"{used_today}/{limits['daily_generations']}"
        )

    return True, "OK"


# =========================================================
# PROMPT LIMIT
# =========================================================

def validate_prompt_length(prompt, plan):
    limits = PLAN_LIMITS.get(
        plan,
        PLAN_LIMITS["free"],
    )

    max_len = limits["max_prompt_length"]

    if len(prompt or "") > max_len:
        return (
            False,
            f"Prompt zu lang. "
            f"Maximal {max_len} Zeichen."
        )

    return True, "OK"


# =========================================================
# SPAM CHECK
# =========================================================

def looks_like_spam(prompt):
    if not prompt:
        return True

    text = str(prompt).lower()

    repeated = [
        "aaaaaa",
        "testtesttest",
        "spam",
        ".....",
    ]

    for item in repeated:
        if item in text:
            return True

    return False


# =========================================================
# FULL VALIDATION
# =========================================================

def validate_request(username, plan, prompt):
    # -------------------------
    # SPAM
    # -------------------------

    if looks_like_spam(prompt):
        return False, "Spam erkannt."

    # -------------------------
    # PROMPT LENGTH
    # -------------------------

    ok, msg = validate_prompt_length(
        prompt,
        plan,
    )

    if not ok:
        return False, msg

    # -------------------------
    # PLAN LIMITS
    # -------------------------

    ok, msg = check_generation_allowed(
        username,
        plan,
    )

    if not ok:
        return False, msg

    return True, "OK"
