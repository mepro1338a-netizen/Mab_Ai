import os

import stripe

from config import FOOTBALL_PLANS, PLANS
from database import (
    payment_already_paid,
    record_purchase,
    set_football_plan,
    set_plan,
    update_tokens,
)
from logger import log_stripe, user_friendly_error
from services.billing_plans import (
    SUBSCRIPTION_CHECKOUT_MODE,
    USER_FRIENDLY_CHECKOUT_ERROR,
    checkout_base_url,
    plan_catalog,
    plan_category,
    plan_checkout_ready,
    resolve_stripe_price_id,
    stripe_checkout_cancel_url,
    stripe_checkout_success_url,
    stripe_price_env_name,
)
from services.stripe_verify import stripe_field, verify_price_id

_stripe_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
stripe.api_key = _stripe_key
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


def is_checkout_plan(plan_key: str) -> bool:
    return plan_key in PLANS or plan_key in FOOTBALL_PLANS


def is_football_plan(plan_key: str) -> bool:
    return plan_key in FOOTBALL_PLANS


def _log_checkout_failure(
    event: str,
    *,
    username: str,
    plan_key: str,
    price_id: str | None,
    success_url: str,
    cancel_url: str,
    stripe_error: str = "",
    **extra,
) -> None:
    log_stripe(
        event,
        username=username,
        success=False,
        plan_key=plan_key,
        price_id_present=bool(price_id),
        price_id=price_id or "",
        used_price_id=price_id or "",
        success_url=success_url,
        cancel_url=cancel_url,
        stripe_error=stripe_error,
        checkout_base=checkout_base_url(),
        **extra,
    )


def create_checkout_session(username: str, plan_key: str):
    success_url = stripe_checkout_success_url()
    cancel_url = stripe_checkout_cancel_url()

    if plan_key == "free" or not is_checkout_plan(plan_key):
        _log_checkout_failure(
            "checkout_invalid_plan",
            username=username,
            plan_key=plan_key,
            price_id=None,
            success_url=success_url,
            cancel_url=cancel_url,
            stripe_error="invalid plan_key",
        )
        return None, USER_FRIENDLY_CHECKOUT_ERROR

    ready, reason = plan_checkout_ready(plan_key)
    if not ready:
        _log_checkout_failure(
            "checkout_not_ready",
            username=username,
            plan_key=plan_key,
            price_id=None,
            success_url=success_url,
            cancel_url=cancel_url,
            stripe_error=reason or "unknown",
        )
        return None, USER_FRIENDLY_CHECKOUT_ERROR

    price_id, price_env = resolve_stripe_price_id(plan_key)
    if not price_id or not price_env:
        _log_checkout_failure(
            "checkout_missing_price",
            username=username,
            plan_key=plan_key,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            stripe_error=f"missing {stripe_price_env_name(plan_key)}",
            price_env=price_env or "",
        )
        return None, USER_FRIENDLY_CHECKOUT_ERROR

    plan = plan_catalog(plan_key) or {}
    category = plan_category(plan_key)

    price_check = verify_price_id(price_id)
    if not price_check.get("ok"):
        err_msg = price_check.get("error") or "invalid price"
        _log_checkout_failure(
            "checkout_price_rejected",
            username=username,
            plan_key=plan_key,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            stripe_error=err_msg,
            price_env=price_env,
        )
        return None, USER_FRIENDLY_CHECKOUT_ERROR

    try:
        session = stripe.checkout.Session.create(
            mode=SUBSCRIPTION_CHECKOUT_MODE,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=username,
            metadata={
                "username": username,
                "plan": plan_key,
                "category": category,
                "checkout_mode": SUBSCRIPTION_CHECKOUT_MODE,
            },
        )
        session_mode = str(stripe_field(session, "mode", "") or "")
        if session_mode != SUBSCRIPTION_CHECKOUT_MODE:
            _log_checkout_failure(
                "checkout_wrong_mode",
                username=username,
                plan_key=plan_key,
                price_id=price_id,
                success_url=success_url,
                cancel_url=cancel_url,
                stripe_error=f"expected {SUBSCRIPTION_CHECKOUT_MODE}, got {session_mode}",
                price_env=price_env,
            )
            return None, USER_FRIENDLY_CHECKOUT_ERROR
        sid = stripe_field(session, "id", None) or ""
        try:
            record_purchase(username, plan_key, 0, sid, "created", "created")
        except Exception as db_exc:
            log_stripe(
                "checkout_db_warn",
                username=username,
                success=True,
                plan_key=plan_key,
                stripe_error=str(db_exc),
            )

        log_stripe(
            f"checkout_created plan={plan_key} price={price_id}",
            username=username,
            success=True,
            plan_key=plan_key,
            price_id_present=True,
            price_id=price_id,
            used_price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            price_env=price_env,
            session_id=sid,
        )
        return stripe_field(session, "url", None), None
    except Exception as e:
        _log_checkout_failure(
            "checkout_failed",
            username=username,
            plan_key=plan_key,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            stripe_error=str(e),
            price_env=price_env,
            label=plan.get("label", plan_key),
        )
        return None, user_friendly_error("stripe", str(e))


def confirm_checkout_session(session_id):
    if not stripe.api_key:
        return False, "STRIPE_SECRET_KEY fehlt."

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        sid = stripe_field(session, "id", session_id) or session_id
        session_mode = str(stripe_field(session, "mode", "") or "")
        if session_mode != SUBSCRIPTION_CHECKOUT_MODE:
            return (
                False,
                f"Ungültige Checkout-Session (mode={session_mode or 'unknown'}; "
                f"nur {SUBSCRIPTION_CHECKOUT_MODE} für Abos).",
            )

        metadata = stripe_field(session, "metadata", {}) or {}
        username = stripe_field(session, "client_reference_id", None) or stripe_field(
            metadata, "username", None
        )
        plan = stripe_field(metadata, "plan", None)
        status = str(stripe_field(session, "payment_status", "unknown") or "unknown")

        if status == "paid" and username and is_checkout_plan(plan):
            if payment_already_paid(sid):
                label = FOOTBALL_PLANS.get(plan, {}).get("label") or PLANS.get(plan, {}).get("label", plan)
                return True, f"{label} war bereits aktiv (keine Doppelbuchung)."

            if is_football_plan(plan):
                set_football_plan(username, plan)
                label = FOOTBALL_PLANS[plan].get("label", plan)
                record_purchase(username, plan, 0, sid, status, "paid")
                return True, f"{label} aktiviert."
            set_plan(username, plan)
            update_tokens(username, PLANS[plan]["tokens"])
            record_purchase(username, plan, 0, sid, status, "paid")
            return True, f"{PLANS[plan]['label']} aktiviert."

        record_purchase(username or "", plan or "", 0, sid, status, "pending")
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
        obj = event.data.object
        session_id = stripe_field(obj, "id", None)
        session_mode = str(stripe_field(obj, "mode", "") or "")
        if session_mode and session_mode != SUBSCRIPTION_CHECKOUT_MODE:
            log_stripe(
                f"webhook_skip_non_subscription:{session_mode}",
                success=True,
            )
            return True, f"Ignoriert: Checkout mode={session_mode}"
        if session_id:
            ok, msg = confirm_checkout_session(session_id)
            log_stripe(
                f"webhook_checkout_{'ok' if ok else 'fail'}",
                success=ok,
            )
            return ok, msg

    return True, f"Event ignoriert: {event_type}"
