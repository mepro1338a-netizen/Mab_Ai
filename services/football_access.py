"""Football Premium feature guards — Starter / Pro / Elite."""
from __future__ import annotations

from config import (
    FOOTBALL_FEATURES,
    FOOTBALL_PLAN_ORDER,
    FOOTBALL_PLANS,
    football_daily_ai_limit,
    football_daily_api_limit,
    football_feature_meta,
    football_has_feature,
    football_plan_allows,
    football_plan_rank,
    football_priority_cache,
    get_football_plan,
)

from db.football_billing import (
    get_football_plan as db_get_football_plan,
    get_football_usage_today,
    record_football_ai_analysis,
    record_football_api_call,
)
from db.users import is_owner_user

PLAN_LABELS = {key: val.get("label", key) for key, val in FOOTBALL_PLANS.items()}
PLAN_LABELS["none"] = "Kein Football Plan"

# Map legacy action keys to feature ids
ACTION_TO_FEATURE = {
    "match_recap": "ai_match_summary",
    "basic_prediction": "ai_predictions",
    "reel_script": "ai_reel_hooks",
    "viral_hook": "ai_reel_hooks",
    "matchday_package": "ai_match_preview",
    "optimized_package": "ai_match_preview",
    "viral_analysis": "ai_viral_analysis",
    "thumbnail_system": "ai_match_preview",
    "deep_match_analysis": "ai_elite_live_intelligence",
    "full_campaign": "ai_matchday_reports",
    "auto_posting": "automation_triggers",
}


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


def feature_label(feature_id: str) -> str:
    meta = football_feature_meta(feature_id)
    return str(meta.get("label") or feature_id)


def can_access_feature(
    username: str,
    feature_id: str,
    session_plan: str | None = None,
) -> tuple[bool, str, str]:
    """Returns ok, message, required_plan_key."""
    meta = football_feature_meta(feature_id)
    if not meta:
        return False, "Unbekanntes Feature.", "football_starter"

    plan = resolve_football_plan(username, session_plan)
    min_plan = str(meta.get("min_plan") or "football_starter")

    if is_owner_user(username) or football_has_feature(plan, feature_id):
        return True, "", plan

    need = get_football_plan(min_plan) or {}
    return (
        False,
        f"**{feature_label(feature_id)}** erfordert mindestens **{need.get('label', min_plan)}**. "
        f"Dein Plan: **{plan_label(plan)}**.",
        min_plan,
    )


def assert_feature(username: str, feature_id: str, session_plan: str | None = None) -> str:
    ok, msg, _ = can_access_feature(username, feature_id, session_plan)
    if not ok:
        raise FootballAccessError(msg)
    return resolve_football_plan(username, session_plan)


def preflight_api_request(
    username: str,
    feature_id: str,
    session_plan: str | None = None,
    *,
    api_configured: bool = True,
) -> str:
    plan = assert_feature(username, feature_id, session_plan)

    if not api_configured:
        raise FootballAccessError(
            "API-Football ist auf dem Server noch nicht konfiguriert "
            "(FOOTBALL_API_KEY in Railway/.env). Dein Plan bleibt aktiv — "
            "Live-Daten erscheinen sobald der Key gesetzt ist."
        )

    if plan == "none" and not is_owner_user(username):
        raise FootballAccessError("Kein Football Premium Plan aktiv.")

    daily_limit = int(football_daily_api_limit(plan) or 0)
    if daily_limit <= 0 and not is_owner_user(username):
        raise FootballAccessError("Dein Plan enthält keine API-Requests.")

    used = get_football_usage_today(username)["api_calls"]
    if used >= daily_limit and not is_owner_user(username):
        raise FootballAccessError(
            f"Tageslimit API erreicht ({used:,}/{daily_limit:,}). "
            "Morgen Reset oder Upgrade auf Football Elite.".replace(",", ".")
        )
    return plan


def record_api_success(username: str, session_plan: str | None = None) -> dict:
    plan = resolve_football_plan(username, session_plan)
    total = record_football_api_call(username)
    limit = int(football_daily_api_limit(plan) or 0)
    return {"used": total, "limit": limit, "plan": plan}


def _action_feature(action: str) -> str:
    return ACTION_TO_FEATURE.get(action, "ai_match_summary")


def can_run_action(
    username: str,
    action: str,
    session_plan: str | None = None,
) -> tuple[bool, str]:
    feature_id = _action_feature(action)
    ok, msg, _ = can_access_feature(username, feature_id, session_plan)
    if not ok:
        return False, msg

    plan = resolve_football_plan(username, session_plan)
    if plan == "none" and not is_owner_user(username):
        return False, "Kein Football Premium Plan. Upgrade unter Premium."

    daily_limit = int(football_daily_ai_limit(plan) or 0)
    used = get_football_usage_today(username)["ai_analyses"]
    if used >= daily_limit and not is_owner_user(username):
        return False, (
            f"Tageslimit AI-Analysen erreicht ({used}/{daily_limit}). "
            f"Upgrade für mehr Kapazität."
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
    if is_owner_user(username):
        return 1
    return record_football_ai_analysis(username)


def can_export_reels(username: str, session_plan: str | None = None) -> tuple[bool, str]:
    return can_access_feature(username, "export_reels_studio", session_plan)[:2]


def feature_matrix(plan_key: str) -> list[dict]:
    """UI list: each feature with available flag for plan."""
    rank = football_plan_rank(plan_key)
    rows = []
    for fid, meta in FOOTBALL_FEATURES.items():
        min_rank = football_plan_rank(meta.get("min_plan", "football_starter"))
        rows.append({
            "id": fid,
            "label": meta.get("label", fid),
            "category": meta.get("category", "api"),
            "description": meta.get("description", ""),
            "min_plan": meta.get("min_plan"),
            "available": rank >= min_rank,
        })
    return rows


def usage_summary(username: str, session_plan: str | None = None) -> dict:
    plan = resolve_football_plan(username, session_plan)
    cfg = get_football_plan(plan) or {}
    usage = get_football_usage_today(username)
    api_daily = int(football_daily_api_limit(plan) or 0)
    ai_daily = int(football_daily_ai_limit(plan) or 0)
    owner = is_owner_user(username)

    return {
        "plan": plan,
        "plan_label": plan_label(plan),
        "badge": cfg.get("badge", ""),
        "live_api": bool(cfg.get("live_api_access")) or owner,
        "priority_cache": football_priority_cache(plan) or owner,
        "api_used": usage["api_calls"],
        "api_limit": api_daily,
        "ai_used": usage["ai_analyses"],
        "ai_limit": ai_daily if ai_daily < 9000 else "Unbegrenzt",
        "actions_used": usage["ai_analyses"],
        "actions_limit": ai_daily,
        "tier": FOOTBALL_PLAN_ORDER.get(plan, 0),
        "features": {
            fid: football_has_feature(plan, fid) or owner
            for fid in FOOTBALL_FEATURES
        },
    }


def tier_features(plan_key: str) -> list[str]:
    plan = get_football_plan(plan_key)
    if not plan:
        return []
    return list(plan.get("highlights") or [])
