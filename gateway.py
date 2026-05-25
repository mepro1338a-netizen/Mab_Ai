"""
MaByte production gateway — single Railway port.

- POST /stripe-webhook  → Stripe (signature verified)
- Everything else        → Streamlit (incl. WebSockets, /_stcore/health)

Start via start.sh:  python gateway.py
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aiohttp import ClientSession, WSMsgType, web
from aiohttp.web import Request, Response, StreamResponse

from stripe_webhook_handler import WEBHOOK_PATH, normalize_path, process_stripe_webhook

STREAMLIT_INTERNAL_PORT = int(os.environ.get("STREAMLIT_INTERNAL_PORT", "8502"))
STREAMLIT_BASE = f"http://127.0.0.1:{STREAMLIT_INTERNAL_PORT}"
STREAMLIT_WS_BASE = f"ws://127.0.0.1:{STREAMLIT_INTERNAL_PORT}"
PUBLIC_PORT = int(os.environ.get("PORT", "8501"))


def configure_production_env() -> None:
    os.environ.setdefault("PORT", str(PUBLIC_PORT))
    os.environ.setdefault("STREAMLIT_SERVER_PORT", str(STREAMLIT_INTERNAL_PORT))
    os.environ.setdefault("STREAMLIT_SERVER_ADDRESS", "127.0.0.1")
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    os.environ.setdefault("STREAMLIT_GLOBAL_DEVELOPMENT_MODE", "false")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLECORS", "false")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLEXSRFPROTECTION", "true")


def bootstrap() -> None:
    try:
        from logger import log_info, log_warning

        base = os.environ.get("APP_BASE_URL", "").strip() or "(not set)"
        log_info(
            f"Gateway boot — public_port={PUBLIC_PORT} "
            f"streamlit_internal={STREAMLIT_INTERNAL_PORT} APP_BASE_URL={base}"
        )
        if not base.startswith("https://"):
            log_warning("APP_BASE_URL sollte https://mabyte.de fuer Production sein.")
    except Exception as exc:
        print(f"[MaByte] gateway logging: {exc}", file=sys.stderr)

    try:
        from database import ensure_db_ready

        if not ensure_db_ready():
            print("[MaByte] WARN: database not ready.", file=sys.stderr)
    except Exception as exc:
        print(f"[MaByte] database bootstrap: {exc}", file=sys.stderr)


def _streamlit_cmd() -> list[str]:
    return [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ROOT / "main.py"),
        f"--server.port={STREAMLIT_INTERNAL_PORT}",
        "--server.address=127.0.0.1",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]


def start_streamlit_subprocess() -> subprocess.Popen[Any]:
    env = os.environ.copy()
    env["MABYTE_GATEWAY_CHILD"] = "1"
    return subprocess.Popen(
        _streamlit_cmd(),
        cwd=str(ROOT),
        env=env,
    )


async def wait_for_streamlit(timeout: float = 120.0) -> bool:
    deadline = time.time() + timeout
    url = f"{STREAMLIT_BASE}/_stcore/health"
    async with ClientSession() as session:
        while time.time() < deadline:
            try:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        return True
            except Exception:
                pass
            await asyncio.sleep(0.5)
    return False


HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


def _proxy_request_headers(request: Request) -> dict[str, str]:
    headers: dict[str, str] = {}
    for key, value in request.headers.items():
        lk = key.lower()
        if lk in HOP_BY_HOP:
            continue
        if lk == "host":
            continue
        headers[key] = value
    # Streamlit behind reverse proxy (Railway / custom domain)
    host = request.headers.get("Host", "")
    if host:
        headers["Host"] = host
    proto = request.headers.get("X-Forwarded-Proto", "https")
    headers["X-Forwarded-Proto"] = proto
    headers["X-Forwarded-Host"] = host or request.host
    headers["X-Forwarded-For"] = request.remote or ""
    return headers


async def handle_stripe_webhook_route(request: Request) -> Response:
    if request.method != "POST":
        return Response(status=405, text="Method not allowed. Use POST.")

    payload = await request.read()
    sig = request.headers.get("Stripe-Signature", "")
    status, body = process_stripe_webhook(payload, sig)
    return Response(status=status, text=body)


async def proxy_http(request: Request) -> StreamResponse:
    target_url = f"{STREAMLIT_BASE}{request.rel_url}"

    async with ClientSession(auto_decompress=False) as session:
        data = await request.read()
        async with session.request(
            method=request.method,
            url=target_url,
            headers=_proxy_request_headers(request),
            data=data if data else None,
            allow_redirects=False,
        ) as upstream:
            body = await upstream.read()
            response = StreamResponse(status=upstream.status)
            skip = HOP_BY_HOP | {"content-encoding", "content-length"}
            for key, value in upstream.headers.items():
                if key.lower() not in skip:
                    response.headers[key] = value
            await response.prepare(request)
            await response.write(body)
            return response


async def proxy_websocket(request: Request) -> web.WebSocketResponse:
    ws_client = web.WebSocketResponse()
    await ws_client.prepare(request)

    ws_url = f"{STREAMLIT_WS_BASE}{request.rel_url}"
    async with ClientSession() as session:
        async with session.ws_connect(
            ws_url,
            headers=_proxy_request_headers(request),
        ) as ws_upstream:

            async def client_to_upstream() -> None:
                async for msg in ws_client:
                    if msg.type == WSMsgType.TEXT:
                        await ws_upstream.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await ws_upstream.send_bytes(msg.data)
                    elif msg.type == WSMsgType.ERROR:
                        break

            async def upstream_to_client() -> None:
                async for msg in ws_upstream:
                    if msg.type == WSMsgType.TEXT:
                        await ws_client.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await ws_client.send_bytes(msg.data)
                    elif msg.type in (WSMsgType.CLOSE, WSMsgType.ERROR):
                        break

            forward = asyncio.gather(client_to_upstream(), upstream_to_client())
            try:
                await forward
            except Exception:
                pass

    return ws_client


async def catch_all(request: Request) -> StreamResponse | web.WebSocketResponse:
    if request.headers.get("Upgrade", "").lower() == "websocket":
        return await proxy_websocket(request)
    return await proxy_http(request)


def create_app() -> web.Application:
    app = web.Application()
    # Exact path before catch-all — non-POST returns 405, not Streamlit 404
    app.router.add_route("*", WEBHOOK_PATH, handle_stripe_webhook_route)
    app.router.add_route("*", "/{tail:.*}", catch_all)
    return app


async def run_gateway() -> None:
    configure_production_env()
    bootstrap()

    proc = start_streamlit_subprocess()
    if not await wait_for_streamlit():
        proc.terminate()
        raise RuntimeError("Streamlit did not become ready on internal port.")

    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PUBLIC_PORT)
    await site.start()

    try:
        from logger import log_info

        log_info(f"Gateway listening on 0.0.0.0:{PUBLIC_PORT} — webhook {WEBHOOK_PATH}")
    except Exception:
        print(f"[MaByte] Gateway on :{PUBLIC_PORT}", file=sys.stderr)

    try:
        while True:
            if proc.poll() is not None:
                raise RuntimeError("Streamlit subprocess exited unexpectedly.")
            await asyncio.sleep(2)
    finally:
        await runner.cleanup()
        proc.terminate()
        proc.wait(timeout=10)


def main() -> None:
    try:
        asyncio.run(run_gateway())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
