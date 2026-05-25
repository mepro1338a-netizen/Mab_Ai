"""Football Premium access control — live API only on Elite."""
from __future__ import annotations

from config import (
    FOOTBALL_PLAN_ORDER,
    FOOTBALL_PLANS,
    football_action_cost,
    football_actions_for_plan,
    football_api_limit,
    football_has_live_api,
    get_football_plan,
)

from db.football_billing import (
    get_football_plan as db_get_football_plan,
    get_football_usage_today,
    record_football_ai_actions,
    record_football_api_call,
)
from db.users import is_owner_user

# Minimum football plan per AI action type
ACTION_MIN_PLAN: dict[str, str] = {
    "basic_stats": "football_starter",
    "basic_prediction": "football_starter",
    "ai_caption": "football_starter",
    "viral_hook": "football_starter",
    "match_recap": "football_starter",
    "thumbnail_system": "football_pro",
    "viral_analysis": "football_pro",
    "reel_script": "football_pro",
    "matchday_package": "football_pro",
    "optimized_package": "football_pro",
    "deep_match_analysis": "football_pro",
    "auto_posting": "football_pro",
    "full_campaign": "football_elite",
}

PLAN_LABELS = {key: val.get("label", key) for key, val in FOOTBALL_PLANS.items()}
PLAN_LABELS["none"] = "Kein Football Plan"


class FootballAccessError(Exception):
    """User-facing gate for Football Premium features."""


def resolve_football_plan(username: str, session_plan: str | None = None) -> str:
    if is_owner_user(username):
        return "football_elite"
    if session_plan and session_plan in FOOTBALL_PLANS:
        return session_plan
    return db_get_football_plan(username)


def plan_label(plan_key: str) -> str:
    return PLAN_LABELS.get(plan_key, plan_key)


def can_use_live_api(username: str, session_plan: str | None = None) -> bool:
    plan = resolve_football_plan(username, session_plan)
    if is_owner_user(username):
        return True
    return football_has_live_api(plan)


def assert_live_api_access(username: str, session_plan: str | None = None) -> str:
    plan = resolve_football_plan(username, session_plan)
    if can_use_live_api(username, session_plan):
        return plan

    raise FootballAccessError(
        "Live Match Data (API-Football) ist nur in **Football Elite** enthalten. "
        "Starter und Pro nutzen die **AI Content Engine** mit manueller Eingabe. "
        "Upgrade unter Premium → Football Elite."
    )


def preflight_api_request(username: str, session_plan: str | None = None) -> str:
    plan = resolve_football_plan(username, session_plan)
    assert_live_api_access(username, session_plan)

    limit = int(football_api_limit(plan) or 0)
    if limit <= 0:
        raise FootballAccessError("Dein Plan enthält keine API-Requests.")

    used = get_football_usage_today(username)["api_calls"]
    if used >= limit and not is_owner_user(username):
        raise FootballAccessError(
            f"Tageslimit API-Requests erreicht ({used:,}/{limit:,}). "
            "Morgen reset oder höheres Football Elite Kontingent."
        )
    return plan


def record_api_success(username: str, session_plan: str | None = None) -> dict:
    preflight_api_request(username, session_plan)
    total = record_football_api_call(username)
    plan = resolve_football_plan(username, session_plan)
    limit = int(football_api_limit(plan) or 0)
    return {"used": total, "limit": limit, "plan": plan}


def can_run_action(
    username: str,
    action: str,
    session_plan: str | None = None,
) -> tuple[bool, str]:
    action = str(action or "").strip().lower()
    min_plan = ACTION_MIN_PLAN.get(action, "football_starter")
    plan = resolve_football_plan(username, session_plan)

    if FOOTBALL_PLAN_ORDER.get(plan, 0) < FOOTBALL_PLAN_ORDER.get(min_plan, 1):
        need = get_football_plan(min_plan) or {}
        return False, (
            f"Diese Funktion benötigt mindestens **{need.get('label', min_plan)}**. "
            f"Dein Plan: **{plan_label(plan)}**."
        )

    cost = football_action_cost(action)
    actions_limit = int(football_actions_for_plan(plan) or 0)
    if actions_limit <= 0 and not is_owner_user(username):
        return False, "Kein aktiver Football Premium Plan."

    used = get_football_usage_today(username)["ai_actions"]
    if used + cost > actions_limit and not is_owner_user(username):
        return False, (
            f"Football AI Actions aufgebraucht ({used:,}+{cost} > {actions_limit:,}/Monat-Tag). "
            "Upgrade für mehr Actions."
        )

    return True, ""


def consume_action(
    username: str,
    action: str,
    session_plan: str | None = None,
) -> int:
    ok, msg = can_run_action(username, action, session_plan)
    if not ok:
        raise FootballAccessError(msg)

    cost = football_action_cost(action)
    if is_owner_user(username):
        return cost
    return record_football_ai_actions(username, cost)


def usage_summary(username: str, session_plan: str | None = None) -> dict:
    plan = resolve_football_plan(username, session_plan)
    cfg = get_football_plan(plan) or {}
    usage = get_football_usage_today(username)
    api_limit = int(football_api_limit(plan) or 0)
    actions_limit = int(football_actions_for_plan(plan) or 0)

    return {
        "plan": plan,
        "plan_label": plan_label(plan),
        "badge": cfg.get("badge", ""),
        "live_api": football_has_live_api(plan) or is_owner_user(username),
        "api_used": usage["api_calls"],
        "api_limit": api_limit,
        "actions_used": usage["ai_actions"],
        "actions_limit": actions_limit,
        "tier": FOOTBALL_PLAN_ORDER.get(plan, 0),
    }


def tier_features(plan_key: str) -> list[str]:
    plan = get_football_plan(plan_key)
    if not plan:
        return []
    return list(plan.get("highlights") or plan.get("features") or [])
