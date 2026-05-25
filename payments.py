import os
import stripe
from config import PLANS, FOOTBALL_PLANS, APP_BASE_URL
from database import payment_already_paid, record_purchase, set_plan, set_football_plan, update_tokens
from logger import log_stripe, user_friendly_error

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


def is_checkout_plan(plan_key: str) -> bool:
    return plan_key in PLANS or plan_key in FOOTBALL_PLANS


def is_football_plan(plan_key: str) -> bool:
    return plan_key in FOOTBALL_PLANS


def _plan_config(plan_key: str) -> dict | None:
    if plan_key in PLANS:
        return PLANS[plan_key]
    if plan_key in FOOTBALL_PLANS:
        return FOOTBALL_PLANS[plan_key]
    return None


def create_checkout_session(username, plan_key):
    if plan_key == "free" or not is_checkout_plan(plan_key):
        return None, "Ungültiger Plan."

    if not stripe.api_key:
        return None, "Stripe ist noch nicht konfiguriert. Setze STRIPE_SECRET_KEY in Railway Variables."

    plan = _plan_config(plan_key) or {}
    price_env = plan.get("stripe_price_env")
    price_id = os.getenv(price_env or "")
    if not price_id:
        return None, f"Stripe Price-ID fehlt. Setze {price_env} in Railway Variables."

    category = "football" if is_football_plan(plan_key) else "normal"

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=(
                f"{APP_BASE_URL}?payment_success=1"
                f"&session_id={{CHECKOUT_SESSION_ID}}&plan={plan_key}"
                f"&category={category}"
            ),
            cancel_url=f"{APP_BASE_URL}?payment_cancel=1",
            client_reference_id=username,
            metadata={
                "username": username,
                "plan": plan_key,
                "category": category,
            },
        )
        record_purchase(username, plan_key, 0, session.id, "created", "created")
        log_stripe("checkout_created", username=username, success=True)
        return session.url, None
    except Exception as e:
        log_stripe("checkout_failed", username=username, success=False)
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
        return False, "STRIPE_WEBHOOK_SECRET fehlt."

    if not stripe.api_key:
        return False, "STRIPE_SECRET_KEY fehlt."

    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        return False, "Ungueltige Stripe Signatur."
    except Exception as exc:
        return False, str(exc)

    if event.type == "checkout.session.completed":
        session_id = event.data.object.get("id")
        if session_id:
            ok, msg = confirm_checkout_session(session_id)
            return ok, msg

    return True, f"Event ignoriert: {event.type}"
