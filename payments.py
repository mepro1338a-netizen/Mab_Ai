import os
import stripe
from config import PLANS, APP_BASE_URL
from database import record_purchase, set_plan, update_tokens

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")


def create_checkout_session(username, plan_key):
    if plan_key not in PLANS or plan_key == "free":
        return None, "Ungültiger Plan."

    if not stripe.api_key:
        return None, "STRIPE_SECRET_KEY fehlt in Railway Variables."

    price_env = PLANS[plan_key].get("stripe_price_env")
    price_id = os.getenv(price_env or "")
    if not price_id:
        return None, f"{price_env} fehlt in Railway Variables."

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{APP_BASE_URL}?payment_success=1&session_id={{CHECKOUT_SESSION_ID}}&plan={plan_key}",
            cancel_url=f"{APP_BASE_URL}?payment_cancel=1",
            client_reference_id=username,
            metadata={"username": username, "plan": plan_key},
        )
        record_purchase(username, plan_key, 0, session.id, "created", "created")
        return session.url, None
    except Exception as e:
        return None, str(e)


def confirm_checkout_session(session_id):
    if not stripe.api_key:
        return False, "STRIPE_SECRET_KEY fehlt."

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        username = session.get("client_reference_id") or session.get("metadata", {}).get("username")
        plan = session.get("metadata", {}).get("plan")
        status = session.get("payment_status", "unknown")

        if status == "paid" and username and plan in PLANS:
            set_plan(username, plan)
            update_tokens(username, PLANS[plan]["tokens"])
            record_purchase(username, plan, 0, session.id, status, "paid")
            return True, f"{PLANS[plan]['label']} aktiviert."
        record_purchase(username or "", plan or "", 0, session.id, status, "pending")
        return False, f"Zahlung noch nicht bestätigt: {status}"
    except Exception as e:
        return False, str(e)
