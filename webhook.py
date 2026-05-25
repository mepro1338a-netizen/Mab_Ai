"""
Local dev webhook server (stdlib). Production: use webhook_service.py on Railway.

  python webhook_service.py
  # or: sh start-webhook.sh
"""
from dotenv import load_dotenv

load_dotenv()

from http.server import BaseHTTPRequestHandler, HTTPServer

from stripe_webhook_handler import WEBHOOK_PATH, process_stripe_webhook


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path == WEBHOOK_PATH:
            self.send_response(405)
            self.end_headers()
            self.wfile.write(b"Method not allowed. Use POST.")
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
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


if __name__ == "__main__":
    import os

    port = int(os.environ.get("WEBHOOK_PORT", "9000"))
    print(f"[MaByte] Dev webhook http://0.0.0.0:{port}{WEBHOOK_PATH}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
