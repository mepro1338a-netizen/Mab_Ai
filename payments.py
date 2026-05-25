import os
from urllib.parse import quote

import stripe

from config import APP_BASE_URL, FOOTBALL_PLANS, PLANS
from database import (
    payment_already_paid,
    record_purchase,
    set_football_plan,
    set_plan,
    update_tokens,
)
from logger import log_stripe, user_friendly_error
from services.billing_plans import (
    USER_FRIENDLY_CHECKOUT_ERROR,
    plan_catalog,
    plan_category,
    plan_checkout_ready,
    resolve_stripe_price_id,
    stripe_price_env_name,
)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


def is_checkout_plan(plan_key: str) -> bool:
    return plan_key in PLANS or plan_key in FOOTBALL_PLANS


def is_football_plan(plan_key: str) -> bool:
    return plan_key in FOOTBALL_PLANS


def stripe_checkout_success_url(plan_key: str, category: str) -> str:
    """Plain HTTPS URL for Stripe — no markdown, no brackets."""
    base = APP_BASE_URL
    plan = quote(plan_key, safe="")
    cat = quote(category, safe="")
    return (
        f"{base}/?payment_success=1"
        f"&session_id={{CHECKOUT_SESSION_ID}}"
        f"&plan={plan}&category={cat}"
    )


def stripe_checkout_cancel_url() -> str:
    return f"{APP_BASE_URL}/?payment_cancel=1"


def _validate_stripe_price(price_id: str, plan_key: str) -> str | None:
    """Return error message if price invalid; None if OK."""
    try:
        price = stripe.Price.retrieve(price_id)
        if not price.get("active"):
            return f"Stripe Price inaktiv ({price_id})"
        if not price.get("recurring"):
            return f"Stripe Price muss recurring/subscription sein ({price_id})"
        return None
    except stripe.error.InvalidRequestError as e:
        return str(e)
    except Exception as e:
        return str(e)


def create_checkout_session(username: str, plan_key: str):
    if plan_key == "free" or not is_checkout_plan(plan_key):
        return None, USER_FRIENDLY_CHECKOUT_ERROR

    ready, reason = plan_checkout_ready(plan_key)
    if not ready:
        log_stripe(
            "checkout_not_ready",
            username=username,
            success=False,
            plan=plan_key,
            reason=reason or "unknown",
        )
        return None, USER_FRIENDLY_CHECKOUT_ERROR

    price_id, price_env = resolve_stripe_price_id(plan_key)
    if not price_id or not price_env:
        log_stripe(
            "checkout_missing_price",
            username=username,
            success=False,
            plan=plan_key,
            price_env=stripe_price_env_name(plan_key),
        )
        return None, USER_FRIENDLY_CHECKOUT_ERROR

    plan = plan_catalog(plan_key) or {}
    category = plan_category(plan_key)

    price_err = _validate_stripe_price(price_id, plan_key)
    if price_err:
        log_stripe(
            "checkout_invalid_price",
            username=username,
            success=False,
            plan=plan_key,
            price_env=price_env,
            price_id=price_id,
            error=price_err,
        )
        return None, USER_FRIENDLY_CHECKOUT_ERROR

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=stripe_checkout_success_url(plan_key, category),
            cancel_url=stripe_checkout_cancel_url(),
            client_reference_id=username,
            metadata={
                "username": username,
                "plan": plan_key,
                "category": category,
            },
        )
        record_purchase(username, plan_key, 0, session.id, "created", "created")
        log_stripe(
            "checkout_created",
            username=username,
            success=True,
            plan=plan_key,
            price_env=price_env,
            session_id=session.id,
        )
        return session.url, None
    except Exception as e:
        log_stripe(
            "checkout_failed",
            username=username,
            success=False,
            plan=plan_key,
            price_env=price_env,
            price_id=price_id,
            error=str(e),
            label=plan.get("label", plan_key),
        )
        return None, user_friendly_error("stripe", str(e))


def confirm_checkout_session(session_id):
    if not stripe.api_key:
        return False, "STRIPE_SECRET_KEY fehlt."

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        username = session.get("client_reference_id") or session.get("metadata", {}).get("username")
        plan = session.get("metadata", {}).get("plan")
        status = session.get("payment_status", "unknown")

        if status == "paid" and username and is_checkout_plan(plan):
            if payment_already_paid(session.id):
                label = FOOTBALL_PLANS.get(plan, {}).get("label") or PLANS.get(plan, {}).get("label", plan)
                return True, f"{label} war bereits aktiv (keine Doppelbuchung)."

            if is_football_plan(plan):
                set_football_plan(username, plan)
                label = FOOTBALL_PLANS[plan].get("label", plan)
                record_purchase(username, plan, 0, session.id, status, "paid")
                return True, f"{label} aktiviert."
            set_plan(username, plan)
            update_tokens(username, PLANS[plan]["tokens"])
            record_purchase(username, plan, 0, session.id, status, "paid")
            return True, f"{PLANS[plan]['label']} aktiviert."

        record_purchase(username or "", plan or "", 0, session.id, status, "pending")
        return False, f"Zahlung noch nicht bestätigt: {status}"
    except Exception as e:
        return False, str(e)


def handle_stripe_webhook(payload, sig):
    if not STRIPE_WEBHOOK_SECRET:
        log_stripe("webhook_missing_secret", success=False)
        return False, "STRIPE_WEBHOOK_SECRET fehlt."

    if not stripe.api_key:
        log_stripe("webhook_missing_api_key", success=False)
        return False, "STRIPE_SECRET_KEY fehlt."

    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        log_stripe("webhook_invalid_signature", success=False)
        return False, "Ungueltige Stripe Signatur."
    except Exception as exc:
        log_stripe("webhook_parse_error", success=False)
        return False, str(exc)

    event_type = getattr(event, "type", "unknown")
    log_stripe(f"webhook_received:{event_type}", success=True)

    if event_type == "checkout.session.completed":
        session_id = event.data.object.get("id")
        if session_id:
            ok, msg = confirm_checkout_session(session_id)
            log_stripe(
                f"webhook_checkout_{'ok' if ok else 'fail'}",
                success=ok,
            )
            return ok, msg

    return True, f"Event ignoriert: {event_type}"
