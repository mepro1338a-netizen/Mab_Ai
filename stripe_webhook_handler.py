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


# ---------------------------------------------------------------------------
# Dev webhook server (stdlib) — was webhook.py
#   python stripe_webhook_handler.py
# Production: webhook_service.py (aiohttp on Railway)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    from http.server import BaseHTTPRequestHandler, HTTPServer

    from dotenv import load_dotenv

    load_dotenv()

    class _DevWebhookHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = normalize_path(self.path)
            if path == WEBHOOK_PATH:
                self.send_response(405)
                self.end_headers()
                self.wfile.write(b"Method not allowed. Use POST.")
                return
            self.send_response(404)
            self.end_headers()

        def do_POST(self):
            path = normalize_path(self.path)
            if path != WEBHOOK_PATH:
                self.send_response(404)
                self.end_headers()
                return
            length = int(self.headers.get("content-length", 0))
            payload = self.rfile.read(length)
            sig = self.headers.get("Stripe-Signature", "")
            status, msg = process_stripe_webhook(payload, sig)
            self.send_response(status)
            self.end_headers()
            self.wfile.write(msg.encode("utf-8"))

        def log_message(self, format, *args):
            return

    port = int(os.environ.get("WEBHOOK_PORT", "9000"))
    print(f"[MaByte] Dev webhook http://0.0.0.0:{port}{WEBHOOK_PATH}")
    HTTPServer(("0.0.0.0", port), _DevWebhookHandler).serve_forever()
