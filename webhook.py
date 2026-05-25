"""
Legacy standalone webhook server (port 9000).

Production (Railway): use gateway.py — Stripe is served on the same PORT as the app:
  POST https://www.mabyte.de/stripe-webhook

Local test only:
  python webhook.py
"""
from dotenv import load_dotenv

load_dotenv()

from http.server import BaseHTTPRequestHandler, HTTPServer

from stripe_webhook_handler import WEBHOOK_PATH, process_stripe_webhook


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path.rstrip("/") != WEBHOOK_PATH:
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


if __name__ == "__main__":
    port = int(__import__("os").environ.get("WEBHOOK_PORT", "9000"))
    print(f"[MaByte] Legacy webhook on :{port}{WEBHOOK_PATH} — production uses gateway.py")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
