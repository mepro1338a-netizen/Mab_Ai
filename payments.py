import time
import stripe

from config import (
    STRIPE_SECRET_KEY,
    STRIPE_PRICE_PRO,
    STRIPE_PRICE_GRAND,
    STRIPE_PRICE_ELITE,
    STRIPE_SUCCESS_URL,
    STRIPE_CANCEL_URL,
)
from database import get_conn


PRICE_MAP = {
    "pro": STRIPE_PRICE_PRO,
    "grand": STRIPE_PRICE_GRAND,
    "elite": STRIPE_PRICE_ELITE,
}


def create_checkout_session(username, plan):
    if plan not in PRICE_MAP:
        return None, "Unknown plan."

    price_id = PRICE_MAP.get(plan)

    if not STRIPE_SECRET_KEY or not price_id:
        return None, "Stripe is not configured yet. Add Stripe keys in .env."

    stripe.api_key = STRIPE_SECRET_KEY

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=STRIPE_SUCCESS_URL,
        cancel_url=STRIPE_CANCEL_URL,
        client_reference_id=username,
        metadata={"username": username, "plan": plan},
    )

    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    INSERT INTO purchases (username, plan, stripe_session_id, status, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (username, plan, session.id, "created", time.time()))
    conn.commit()
    conn.close()

    return session.url, None
