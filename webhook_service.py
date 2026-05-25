"""
MaByte Stripe webhook — standalone Railway service.

Stripe endpoint: POST https://<webhook-service>.up.railway.app/stripe-webhook
GET  → 405

Main app runs separately: streamlit run main.py (no gateway proxy).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aiohttp import web

from stripe_webhook_handler import WEBHOOK_PATH, process_stripe_webhook


async def handle_stripe_webhook(request: web.Request) -> web.Response:
    if request.method != "POST":
        return web.Response(status=405, text="Method not allowed. Use POST.")
    payload = await request.read()
    sig = request.headers.get("Stripe-Signature", "")
    status, body = process_stripe_webhook(payload, sig)
    return web.Response(status=status, text=body)


async def healthz(_request: web.Request) -> web.Response:
    return web.Response(text="ok", content_type="text/plain")


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_route("*", WEBHOOK_PATH, handle_stripe_webhook)
    app.router.add_get("/healthz", healthz)
    return app


def bootstrap() -> None:
    try:
        from database import ensure_db_ready

        if not ensure_db_ready():
            print("[MaByte] WARN: webhook DB not ready.", file=sys.stderr)
    except Exception as exc:
        print(f"[MaByte] webhook DB bootstrap: {exc}", file=sys.stderr)


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    bootstrap()
    print(
        f"[MaByte] Webhook service on 0.0.0.0:{port}{WEBHOOK_PATH}",
        file=sys.stderr,
        flush=True,
    )
    web.run_app(create_app(), host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
