from dotenv import load_dotenv
load_dotenv()

from http.server import BaseHTTPRequestHandler, HTTPServer
from payments import handle_stripe_webhook

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/stripe-webhook":
            self.send_response(404); self.end_headers(); return
        length = int(self.headers.get("content-length", 0))
        payload = self.rfile.read(length)
        sig = self.headers.get("Stripe-Signature", "")
        ok, msg = handle_stripe_webhook(payload, sig)
        self.send_response(200 if ok else 400)
        self.end_headers()
        self.wfile.write(msg.encode())

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 9000), Handler).serve_forever()
