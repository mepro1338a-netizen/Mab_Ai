"""
MaByte production gateway — single Railway port.

- POST /stripe-webhook  → Stripe (signature verified)
- Everything else        → Streamlit (proxy, incl. WebSockets)

Railway: binds PORT immediately so healthchecks pass while Streamlit boots.
"""
from __future__ import annotations

import asyncio
import gzip
import os
import subprocess
import sys
import time
import zlib
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aiohttp import ClientSession, WSMsgType, web
from aiohttp.web import Application, Request, Response

from stripe_webhook_handler import WEBHOOK_PATH, process_stripe_webhook

STREAMLIT_INTERNAL_PORT = int(os.environ.get("STREAMLIT_INTERNAL_PORT", "8502"))
STREAMLIT_BASE = f"http://127.0.0.1:{STREAMLIT_INTERNAL_PORT}"
STREAMLIT_WS_BASE = f"ws://127.0.0.1:{STREAMLIT_INTERNAL_PORT}"

HEALTH_PATHS = {"/_stcore/health", "/healthz", "/"}


def public_port() -> int:
    """Railway injects PORT; local dev fallback 8080."""
    return int(os.environ.get("PORT", "8080"))


def configure_production_env() -> None:
    os.environ.setdefault("PORT", "8080")
    os.environ.setdefault("STREAMLIT_SERVER_PORT", str(STREAMLIT_INTERNAL_PORT))
    os.environ.setdefault("STREAMLIT_SERVER_ADDRESS", "127.0.0.1")
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    os.environ.setdefault("STREAMLIT_GLOBAL_DEVELOPMENT_MODE", "false")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLECORS", "false")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLEXSRFPROTECTION", "false")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLEWEBSOCKETCOMPRESSION", "false")


def bootstrap() -> None:
    try:
        from logger import log_info, log_warning

        base = os.environ.get("APP_BASE_URL", "").strip() or "(not set)"
        log_info(
            f"Gateway boot — public_port={public_port()} "
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
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
        "--server.enableWebsocketCompression=false",
    ]


def start_streamlit_subprocess() -> subprocess.Popen[Any]:
    env = os.environ.copy()
    env["MABYTE_GATEWAY_CHILD"] = "1"
    try:
        from config import DATA_DIR
        log_path = Path(DATA_DIR) / "logs" / "streamlit_subprocess.log"
    except Exception:
        log_path = ROOT / "data" / "logs" / "streamlit_subprocess.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_file = open(log_path, "a", encoding="utf-8")
    except OSError:
        log_file = subprocess.DEVNULL

    return subprocess.Popen(
        _streamlit_cmd(),
        cwd=str(ROOT),
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )


async def wait_for_streamlit(timeout: float = 180.0) -> bool:
    deadline = time.time() + timeout
    url = f"{STREAMLIT_BASE}/_stcore/health"
    async with ClientSession() as session:
        while time.time() < deadline:
            try:
                async with session.get(url, timeout=8) as resp:
                    if resp.status == 200:
                        return True
            except Exception:
                pass
            await asyncio.sleep(1.0)
    return False


HOP_BY_HOP = frozenset({
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
})

# Never forward compression framing — body is always plain bytes to the browser.
PROXY_RESPONSE_SKIP = HOP_BY_HOP | frozenset({
    "content-encoding",
    "content-length",
    "transfer-encoding",
    "vary",
})


def _decompress_body(body: bytes, content_encoding: str | None) -> bytes:
    """Always return plain bytes for the browser (never gzip/br as text)."""
    if not body:
        return body

    def _try(fn) -> bytes | None:
        try:
            return fn()
        except Exception:
            return None

    enc = (content_encoding or "").lower().replace(" ", "")
    if enc:
        for part in enc.split(","):
            part = part.strip()
            if part in ("gzip", "x-gzip"):
                out = _try(lambda b=body: gzip.decompress(b))
                if out is not None:
                    return out
            elif part == "deflate":
                out = _try(lambda b=body: zlib.decompress(b))
                if out is not None:
                    return out
            elif part == "br":
                try:
                    import brotli  # type: ignore[import-untyped]

                    out = _try(lambda b=body: brotli.decompress(b))
                    if out is not None:
                        return out
                except ImportError:
                    pass

    if len(body) >= 2 and body[:2] == b"\x1f\x8b":
        out = _try(lambda: gzip.decompress(body))
        if out is not None:
            return out
    return body


def _proxy_request_headers(request: Request) -> dict[str, str]:
    """Headers for Streamlit upstream — force uncompressed responses."""
    headers: dict[str, str] = {}
    for key, value in request.headers.items():
        lk = key.lower()
        if lk in HOP_BY_HOP or lk in ("host", "accept-encoding"):
            continue
        headers[key] = value
    headers["Host"] = f"127.0.0.1:{STREAMLIT_INTERNAL_PORT}"
    headers["Accept-Encoding"] = "identity"
    headers["X-Forwarded-Proto"] = request.headers.get("X-Forwarded-Proto", "https")
    headers["X-Forwarded-Host"] = request.headers.get("Host", request.host)
    headers["X-Forwarded-For"] = request.remote or ""
    return headers


def _build_client_response_headers(upstream_headers: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in upstream_headers.items():
        if key.lower() not in PROXY_RESPONSE_SKIP:
            out[key] = value
    return out


def _is_health_path(path: str) -> bool:
    p = path.split("?", 1)[0].rstrip("/") or "/"
    return p in HEALTH_PATHS or p == "/_stcore/health"


async def handle_stripe_webhook_route(request: Request) -> Response:
    if request.method != "POST":
        return Response(status=405, text="Method not allowed. Use POST.")
    payload = await request.read()
    sig = request.headers.get("Stripe-Signature", "")
    status, body = process_stripe_webhook(payload, sig)
    return Response(status=status, text=body)


async def handle_boot_health(request: Request) -> Response:
    """Railway healthcheck — always 200 while container is up."""
    app = request.app
    if app["streamlit_ready"]:
        return await proxy_http(request)
    return Response(status=200, text="ok", content_type="text/plain")


async def proxy_http(request: Request) -> Response:
    target_url = f"{STREAMLIT_BASE}{request.rel_url}"
    req_headers = _proxy_request_headers(request)
    data = await request.read()

    async with ClientSession(auto_decompress=False) as session:
        async with session.request(
            method=request.method,
            url=target_url,
            headers=req_headers,
            data=data if data else None,
            allow_redirects=False,
            timeout=120,
        ) as upstream:
            content_encoding = upstream.headers.get("Content-Encoding")
            raw_body = await upstream.read()
            body = _decompress_body(raw_body, content_encoding)

            return Response(
                status=upstream.status,
                body=body,
                headers=_build_client_response_headers(upstream.headers),
            )


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
                    else:
                        break

            async def upstream_to_client() -> None:
                async for msg in ws_upstream:
                    if msg.type == WSMsgType.TEXT:
                        await ws_client.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await ws_client.send_bytes(msg.data)
                    else:
                        break

            await asyncio.gather(client_to_upstream(), upstream_to_client())

    return ws_client


async def catch_all(request: Request) -> Response | web.WebSocketResponse:
    app = request.app

    if _is_health_path(request.path):
        return await handle_boot_health(request)

    if not app["streamlit_ready"]:
        return Response(
            status=503,
            text="MaByte startet… bitte in wenigen Sekunden neu laden.",
            content_type="text/plain",
        )

    if request.headers.get("Upgrade", "").lower() == "websocket":
        return await proxy_websocket(request)
    return await proxy_http(request)


async def _warm_streamlit(app: Application) -> None:
    proc = app["streamlit_proc"]
    try:
        if await wait_for_streamlit():
            app["streamlit_ready"] = True
            try:
                from logger import log_info
                log_info("Streamlit ready — proxy active.")
            except Exception:
                print("[MaByte] Streamlit ready.", file=sys.stderr)
        else:
            try:
                from logger import log_error
                log_error("Streamlit did not become ready in time.")
            except Exception:
                print("[MaByte] Streamlit timeout.", file=sys.stderr)
            if proc and proc.poll() is None:
                proc.terminate()
    except Exception as exc:
        try:
            from logger import log_error
            log_error(f"Streamlit warm error: {exc}")
        except Exception:
            print(f"[MaByte] warm error: {exc}", file=sys.stderr)


async def _watch_streamlit(app: Application) -> None:
    while True:
        proc = app.get("streamlit_proc")
        if proc and proc.poll() is not None:
            try:
                from logger import log_error
                log_error(f"Streamlit exited code={proc.returncode}")
            except Exception:
                print(f"[MaByte] Streamlit exited {proc.returncode}", file=sys.stderr)
            app["streamlit_ready"] = False
            break
        await asyncio.sleep(3)


def create_app() -> Application:
    app = web.Application()
    app["streamlit_ready"] = False
    app["streamlit_proc"] = None
    app.router.add_route("*", WEBHOOK_PATH, handle_stripe_webhook_route)
    app.router.add_route("GET", "/healthz", handle_boot_health)
    app.router.add_route("GET", "/_stcore/health", handle_boot_health)
    app.router.add_route("*", "/{tail:.*}", catch_all)
    return app


async def run_gateway() -> None:
    configure_production_env()
    bootstrap()

    app = create_app()
    app["streamlit_proc"] = start_streamlit_subprocess()

    runner = web.AppRunner(app)
    await runner.setup()
    port = public_port()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    try:
        from logger import log_info
        log_info(f"Gateway listening on 0.0.0.0:{port} (boot health OK)")
    except Exception:
        print(f"[MaByte] Gateway on 0.0.0.0:{port}", file=sys.stderr)

    asyncio.create_task(_warm_streamlit(app))
    asyncio.create_task(_watch_streamlit(app))

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await runner.cleanup()
        proc = app.get("streamlit_proc")
        if proc and proc.poll() is None:
            proc.terminate()


def main() -> None:
    print(
        f"[MaByte] ENTRY gateway.py — public PORT={public_port()} "
        f"(env PORT={os.environ.get('PORT', '(unset)')}) "
        f"streamlit internal={STREAMLIT_INTERNAL_PORT}",
        file=sys.stderr,
        flush=True,
    )
    try:
        asyncio.run(run_gateway())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
