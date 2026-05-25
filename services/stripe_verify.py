"""
Stripe Price-ID verification — explains why Grand works but Pro/Elite may not.
"""
from __future__ import annotations

import os
from typing import Any

import stripe

from services.billing_plans import (
    AI_CHECKOUT_KEYS,
    FOOTBALL_CHECKOUT_KEYS,
    resolve_stripe_price_id,
    stripe_price_env_name,
)

ALL_CHECKOUT_KEYS = (*AI_CHECKOUT_KEYS, *FOOTBALL_CHECKOUT_KEYS)


def _stripe_ready() -> bool:
    return bool(os.getenv("STRIPE_SECRET_KEY", "").strip())


def verify_price_id(price_id: str) -> dict[str, Any]:
    """
    Check if price_id works with Checkout subscription mode.
    Returns dict: ok (bool), error (str), recurring (bool), active (bool), livemode (bool|None)
    """
    result: dict[str, Any] = {
        "ok": False,
        "error": "",
        "price_id": price_id,
        "active": False,
        "recurring": False,
        "livemode": None,
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
        result["active"] = bool(price.get("active"))
        result["recurring"] = bool(price.get("recurring"))
        result["livemode"] = price.get("livemode")
        if not result["active"]:
            result["error"] = "Price ist in Stripe deaktiviert (inactive)"
            return result
        if not result["recurring"]:
            result["error"] = "Kein Abo-Preis — in Stripe „Recurring/monthly“ anlegen"
            return result
        result["ok"] = True
        return result
    except stripe.error.InvalidRequestError as exc:
        result["error"] = str(exc.user_message or exc) or "Price-ID unbekannt in Stripe"
        return result
    except Exception as exc:
        result["error"] = str(exc)
        return result


def verify_plan(plan_key: str) -> dict[str, Any]:
    """Full status for one checkout plan."""
    env_name = stripe_price_env_name(plan_key)
    price_id, _ = resolve_stripe_price_id(plan_key)
    base: dict[str, Any] = {
        "plan_key": plan_key,
        "env": env_name,
        "price_id": price_id or "",
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


def plan_stripe_ok(plan_key: str, cache: dict[str, dict[str, Any]] | None = None) -> tuple[bool, str]:
    """Use cached verify_all_checkout_plans() result if provided."""
    data = (cache or verify_all_checkout_plans()).get(plan_key, {})
    if data.get("ok"):
        return True, ""
    return False, str(data.get("error") or "Stripe Price nicht gültig")
