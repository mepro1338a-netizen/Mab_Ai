"""Stripe webhook HTTP handler — used by webhook_service.py (Railway)."""
from __future__ import annotations

from payments import handle_stripe_webhook

WEBHOOK_PATH = "/stripe-webhook"


def normalize_path(path: str) -> str:
    p = (path or "").split("?", 1)[0].rstrip("/") or "/"
    return p


def process_stripe_webhook(
    payload: bytes,
    signature: str,
) -> tuple[int, str]:
    """
    Returns (status_code, response_body).
    200 on success, 400 on verification/handling errors.
    """
    if not payload:
        return 400, "Empty payload."

    sig = (signature or "").strip()
    if not sig:
        return 400, "Missing Stripe-Signature header."

    ok, msg = handle_stripe_webhook(payload, sig)
    return (200 if ok else 400), str(msg or "")
