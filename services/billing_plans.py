"""
Central Stripe checkout plan registry — single source for Premium UI + payments.

Grand (STRIPE_PRICE_GRAND) is the reference; all plans use the same checkout path.
"""
from __future__ import annotations

import os
from typing import Any

from config import FOOTBALL_PLANS, PLANS

# Display order on Premium page (matches screenshot layout)
AI_CHECKOUT_KEYS = ("pro", "grand", "elite")
FOOTBALL_CHECKOUT_KEYS = ("football_starter", "football_pro", "football_elite")

USER_FRIENDLY_CHECKOUT_ERROR = (
    "Zahlung konnte nicht gestartet werden. Bitte später erneut versuchen."
)


def plan_catalog(plan_key: str) -> dict[str, Any] | None:
    if plan_key in PLANS:
        return PLANS[plan_key]
    if plan_key in FOOTBALL_PLANS:
        return FOOTBALL_PLANS[plan_key]
    return None


def plan_category(plan_key: str) -> str:
    return "football" if plan_key in FOOTBALL_PLANS else "normal"


def stripe_price_env_name(plan_key: str) -> str:
    cfg = plan_catalog(plan_key) or {}
    return (cfg.get("stripe_price_env") or "").strip()


def resolve_stripe_price_id(plan_key: str) -> tuple[str | None, str | None]:
    """
    Returns (price_id, env_var_name).
    env_var_name is None if plan has no checkout (e.g. free, b2b).
    """
    env_name = stripe_price_env_name(plan_key)
    if not env_name:
        return None, None
    price_id = os.getenv(env_name, "").strip()
    return (price_id or None), env_name


def plan_checkout_ready(plan_key: str) -> tuple[bool, str | None]:
    """Per-plan readiness — Grand can work while Pro is missing a Price ID."""
    if not os.getenv("STRIPE_SECRET_KEY", "").strip():
        return False, "STRIPE_SECRET_KEY"
    env_name = stripe_price_env_name(plan_key)
    if not env_name:
        return False, "no_checkout"
    price_id, _ = resolve_stripe_price_id(plan_key)
    if not price_id:
        return False, env_name
    return True, None


def is_plan_active(
    plan_key: str,
    *,
    user_plan: str,
    football_plan: str,
) -> bool:
    if plan_key in FOOTBALL_PLANS:
        return football_plan == plan_key
    return user_plan == plan_key


def checkout_plans_status() -> dict[str, Any]:
    """Summary for Premium page warnings."""
    missing_secret = not os.getenv("STRIPE_SECRET_KEY", "").strip()
    per_plan: dict[str, dict[str, Any]] = {}
    missing_envs: list[str] = []

    for key in (*AI_CHECKOUT_KEYS, *FOOTBALL_CHECKOUT_KEYS):
        ready, reason = plan_checkout_ready(key)
        env_name = stripe_price_env_name(key)
        price_id, _ = resolve_stripe_price_id(key)
        per_plan[key] = {
            "ready": ready and not missing_secret,
            "env": env_name,
            "has_price_id": bool(price_id),
            "reason": reason,
        }
        if not ready and reason and reason not in ("no_checkout", "STRIPE_SECRET_KEY"):
            missing_envs.append(reason)

    return {
        "stripe_secret_ok": not missing_secret,
        "per_plan": per_plan,
        "missing_envs": sorted(set(missing_envs)),
        "any_ready": any(p["ready"] for p in per_plan.values()) if not missing_secret else False,
    }


def football_metrics_text(plan_key: str, plan: dict[str, Any]) -> tuple[str, str, str]:
    """Bubble label, value, sub — aligned across all football cards."""
    daily = int(plan.get("daily_ai_analyses") or 0)
    if daily >= 9999:
        actions_text = "∞"
    else:
        actions_text = f"{daily:,}".replace(",", ".")
    if plan_key == "football_elite":
        return "Actions + Live API", f"{actions_text} Actions", "API-Football Elite"
    return "AI Analysen / Tag", f"{actions_text}", "Football Premium"
