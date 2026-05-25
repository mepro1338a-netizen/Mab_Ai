"""
Stripe Price-ID verification for subscription checkout (mode=subscription only).
One-off (type=one_time) prices must not be used for Abo plans.
"""
from __future__ import annotations

import os
from typing import Any

import stripe

from services.billing_plans import (
    ALL_SUBSCRIPTION_CHECKOUT_KEYS,
    SUBSCRIPTION_CHECKOUT_MODE,
    resolve_stripe_price_id,
    stripe_price_env_name,
)

try:
    from stripe import InvalidRequestError as StripeInvalidRequestError
except ImportError:
    from stripe.error import InvalidRequestError as StripeInvalidRequestError  # type: ignore

ALL_CHECKOUT_KEYS = ALL_SUBSCRIPTION_CHECKOUT_KEYS


def stripe_field(obj: Any, key: str, default: Any = None) -> Any:
    """Stripe SDK v10+ objects have no .get() — use attr or []."""
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
    """
    True only for active Stripe Prices usable with Checkout mode=subscription.
    Rejects one_time / missing recurring.
    """
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
    """
    Check if price_id works with Checkout mode=subscription.
    Returns dict: ok, error, recurring, active, livemode, price_type, recurring_interval
    """
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
    """Full status for one checkout plan."""
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
    """Streamlit session cache — avoids 6x Stripe API per rerun."""
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
    """Use cached verify_all_checkout_plans() result if provided."""
    data = (cache or verify_all_checkout_plans()).get(plan_key, {})
    if data.get("ok"):
        return True, ""
    return False, str(data.get("error") or "Stripe Price nicht gültig (nur recurring für Abos)")
