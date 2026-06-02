"""
Central Stripe checkout plan registry — single source for Premium UI + payments.

Grand (STRIPE_PRICE_GRAND) is the reference; all plans use the same checkout path.
"""
from __future__ import annotations

import os
import re
from typing import Any

import stripe

from config import FOOTBALL_PLANS, PLANS, normalize_app_base_url

try:
    from stripe import InvalidRequestError as StripeInvalidRequestError
except ImportError:
    from stripe.error import InvalidRequestError as StripeInvalidRequestError  # type: ignore

_PRICE_ID_RE = re.compile(r"^price_[A-Za-z0-9]+$")

# Display order on Premium page (matches screenshot layout)
AI_CHECKOUT_KEYS = ("pro", "grand", "elite")
FOOTBALL_CHECKOUT_KEYS = ("football_starter", "football_pro", "football_elite")
ALL_SUBSCRIPTION_CHECKOUT_KEYS = (*AI_CHECKOUT_KEYS, *FOOTBALL_CHECKOUT_KEYS)

# All Abo-Pläne: Stripe Checkout nur als Subscription + recurring price_…
SUBSCRIPTION_CHECKOUT_MODE = "subscription"

USER_FRIENDLY_CHECKOUT_ERROR = (
    "Zahlung konnte nicht gestartet werden. Bitte später erneut versuchen."
)


def _is_local_url(url: str) -> bool:
    low = (url or "").lower()
    return "localhost" in low or "127.0.0.1" in low


def _is_production_deploy() -> bool:
    return bool(
        os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("RAILWAY_PROJECT_ID")
        or os.getenv("RAILWAY_SERVICE_NAME")
        or os.getenv("MABYTE_ENV", "").strip().lower() == "production"
    )


def checkout_base_url() -> str:
    """
    APP_BASE_URL first, then STRIPE_SUCCESS_URL fallback.
    Never use localhost/127.0.0.1 on Railway/production.
    """
    app_raw = os.getenv("APP_BASE_URL", "").strip()
    stripe_raw = os.getenv("STRIPE_SUCCESS_URL", "").strip()
    in_prod = _is_production_deploy()

    candidates: list[str] = []
    if app_raw:
        candidates.append(normalize_app_base_url(app_raw))
    if stripe_raw:
        candidates.append(normalize_app_base_url(stripe_raw))
    if in_prod:
        railway_host = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
        if railway_host:
            host = railway_host if railway_host.startswith("http") else f"https://{railway_host}"
            candidates.append(normalize_app_base_url(host))

    for url in candidates:
        if url and (not in_prod or not _is_local_url(url)):
            return url.rstrip("/")

    fallback = normalize_app_base_url(app_raw or stripe_raw or "http://localhost:8501")
    return fallback.rstrip("/")


def stripe_checkout_success_url() -> str:
    base = checkout_base_url()
    return f"{base}/?checkout=success&session_id={{CHECKOUT_SESSION_ID}}"


def stripe_checkout_cancel_url() -> str:
    base = checkout_base_url()
    return f"{base}/?checkout=cancel"


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
    raw = os.getenv(env_name, "").strip().strip('"').strip("'")
    # Railway copy-paste sometimes adds newlines or label prefixes
    if raw.startswith("prod_"):
        return None, env_name
    if raw and not raw.startswith("price_"):
        match = _PRICE_ID_RE.search(raw)
        raw = match.group(0) if match else raw.split()[0] if raw.split() else raw
    price_id = raw.strip() if raw else ""
    return (price_id or None), env_name


def plan_checkout_ready(
    plan_key: str,
    *,
    stripe_cache: dict[str, dict[str, Any]] | None = None,
) -> tuple[bool, str | None]:
    """Per-plan readiness — env set + Stripe API confirms recurring subscription price."""
    if not os.getenv("STRIPE_SECRET_KEY", "").strip():
        return False, "STRIPE_SECRET_KEY"
    env_name = stripe_price_env_name(plan_key)
    if not env_name:
        return False, "no_checkout"
    price_id, _ = resolve_stripe_price_id(plan_key)
    if not price_id:
        return False, env_name

    if stripe_cache is not None:
        ok, err = plan_stripe_ok(plan_key, stripe_cache)
    else:
        row = verify_plan(plan_key)
        ok = bool(row.get("ok"))
        err = str(row.get("error") or "")
    if not ok:
        return False, err or env_name
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


def checkout_plans_status(
    *,
    stripe_cache: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Summary for Premium page warnings (uses recurring price verification)."""
    missing_secret = not os.getenv("STRIPE_SECRET_KEY", "").strip()
    per_plan: dict[str, dict[str, Any]] = {}
    missing_envs: list[str] = []

    for key in ALL_SUBSCRIPTION_CHECKOUT_KEYS:
        ready, reason = plan_checkout_ready(key, stripe_cache=stripe_cache)
        env_name = stripe_price_env_name(key)
        price_id, _ = resolve_stripe_price_id(key)
        per_plan[key] = {
            "ready": ready and not missing_secret,
            "env": env_name,
            "has_price_id": bool(price_id),
            "reason": reason,
            "checkout_mode": SUBSCRIPTION_CHECKOUT_MODE,
        }
        if not ready and reason and reason not in ("no_checkout", "STRIPE_SECRET_KEY"):
            missing_envs.append(reason)

    return {
        "stripe_secret_ok": not missing_secret,
        "checkout_mode": SUBSCRIPTION_CHECKOUT_MODE,
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


# ---------------------------------------------------------------------------
# Inline: services.stripe_verify (checkout price validation)
# ---------------------------------------------------------------------------

ALL_CHECKOUT_KEYS = ALL_SUBSCRIPTION_CHECKOUT_KEYS


def stripe_field(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    try:
        val = getattr(obj, key, None)
        if val is not None:
            return val
    except Exception:
        pass
    try:
        return obj[key]
    except Exception:
        return default


def _stripe_ready() -> bool:
    key = os.getenv("STRIPE_SECRET_KEY", "").strip()
    if key:
        stripe.api_key = key
    return bool(key)


def price_is_recurring_subscription(price: Any) -> tuple[bool, str, dict[str, Any]]:
    meta: dict[str, Any] = {
        "price_type": "",
        "recurring_interval": "",
        "recurring_interval_count": None,
    }
    if price is None:
        return False, "Price nicht gefunden", meta
    price_type = str(stripe_field(price, "type", "") or "").strip().lower()
    meta["price_type"] = price_type
    if price_type == "one_time":
        return (
            False,
            "One-off Price (type=one_time) — für Abos einen Recurring-Preis in Stripe anlegen",
            meta,
        )
    recurring = stripe_field(price, "recurring", None)
    if not recurring:
        return (
            False,
            "Kein Abo-Preis — in Stripe „Recurring“ (monthly/yearly) anlegen, kein One-time",
            meta,
        )
    interval = str(stripe_field(recurring, "interval", "") or "").strip().lower()
    count = stripe_field(recurring, "interval_count", 1)
    meta["recurring_interval"] = interval
    meta["recurring_interval_count"] = count
    if not interval:
        return False, "Recurring-Preis ohne Intervall (month/year)", meta
    if not bool(stripe_field(price, "active", False)):
        return False, "Price ist in Stripe deaktiviert (inactive)", meta
    return True, "", meta


def verify_price_id(price_id: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "ok": False,
        "error": "",
        "price_id": price_id,
        "checkout_mode": SUBSCRIPTION_CHECKOUT_MODE,
        "active": False,
        "recurring": False,
        "livemode": None,
        "price_type": "",
        "recurring_interval": "",
    }
    if not price_id:
        result["error"] = "Keine Price-ID gesetzt"
        return result
    if price_id.startswith("prod_"):
        result["error"] = "Das ist eine Product-ID (prod_…), nicht price_…"
        return result
    if not price_id.startswith("price_"):
        result["error"] = "Ungültiges Format — muss mit price_ beginnen"
        return result
    if not _stripe_ready():
        result["error"] = "STRIPE_SECRET_KEY fehlt"
        return result
    try:
        price = stripe.Price.retrieve(price_id)
        ok, err, meta = price_is_recurring_subscription(price)
        result["active"] = bool(stripe_field(price, "active", False))
        result["recurring"] = ok
        result["livemode"] = stripe_field(price, "livemode", None)
        result["price_type"] = meta.get("price_type", "")
        result["recurring_interval"] = meta.get("recurring_interval", "")
        if not ok:
            result["error"] = err
            return result
        result["ok"] = True
        result["error"] = ""
        return result
    except StripeInvalidRequestError as exc:
        msg = getattr(exc, "user_message", None) or str(exc)
        result["error"] = str(msg) or "Price-ID unbekannt in Stripe"
        return result
    except Exception as exc:
        result["error"] = str(exc) or "Stripe-Prüfung fehlgeschlagen"
        return result


def verify_plan(plan_key: str) -> dict[str, Any]:
    env_name = stripe_price_env_name(plan_key)
    price_id, _ = resolve_stripe_price_id(plan_key)
    base: dict[str, Any] = {
        "plan_key": plan_key,
        "env": env_name,
        "price_id": price_id or "",
        "checkout_mode": SUBSCRIPTION_CHECKOUT_MODE,
        "ok": False,
        "error": "",
    }
    if not env_name:
        base["error"] = "Kein Checkout"
        return base
    if not price_id:
        base["error"] = f"{env_name} leer oder ungültig in Railway"
        return base
    checked = verify_price_id(price_id)
    base.update(checked)
    return base


def verify_all_checkout_plans() -> dict[str, dict[str, Any]]:
    return {key: verify_plan(key) for key in ALL_CHECKOUT_KEYS}


STRIPE_VERIFY_CACHE_KEY = "stripe_plan_verify_cache"


def get_stripe_verify_cache() -> dict[str, dict[str, Any]]:
    try:
        import streamlit as st

        if STRIPE_VERIFY_CACHE_KEY not in st.session_state:
            st.session_state[STRIPE_VERIFY_CACHE_KEY] = verify_all_checkout_plans()
        return st.session_state[STRIPE_VERIFY_CACHE_KEY]
    except Exception:
        return verify_all_checkout_plans()


def refresh_stripe_verify_cache() -> dict[str, dict[str, Any]]:
    try:
        import streamlit as st

        data = verify_all_checkout_plans()
        st.session_state[STRIPE_VERIFY_CACHE_KEY] = data
        return data
    except Exception:
        return verify_all_checkout_plans()


def plan_stripe_ok(plan_key: str, cache: dict[str, dict[str, Any]] | None = None) -> tuple[bool, str]:
    data = (cache or verify_all_checkout_plans()).get(plan_key, {})
    if data.get("ok"):
        return True, ""
    return False, str(data.get("error") or "Stripe Price nicht gültig (nur recurring für Abos)")
