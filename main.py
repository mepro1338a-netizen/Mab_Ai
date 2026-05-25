"""
MaByte — Streamlit UI entry (loaded by gateway or direct `streamlit run main.py`).

Production (Railway):
  python gateway.py   # via start.sh — public PORT + /stripe-webhook

Local dev:
  streamlit run main.py --server.port 8501 --server.address 0.0.0.0
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def configure_production_env() -> None:
    """Railway injects PORT; Streamlit must bind 0.0.0.0 for healthchecks."""
    port = os.environ.get("PORT", "8501").strip() or "8501"
    os.environ.setdefault("PORT", port)
    os.environ.setdefault("STREAMLIT_SERVER_PORT", port)
    os.environ.setdefault("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
    os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "true")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    os.environ.setdefault("STREAMLIT_GLOBAL_DEVELOPMENT_MODE", "false")
    # Custom domain / Railway reverse proxy (HTTPS)
    os.environ.setdefault("STREAMLIT_SERVER_ENABLECORS", "false")
    os.environ.setdefault("STREAMLIT_SERVER_ENABLEXSRFPROTECTION", "true")


def log_startup() -> None:
    try:
        from logger import log_info, log_warning

        port = os.environ.get("PORT", "8501")
        base = os.environ.get("APP_BASE_URL", "").strip() or "(not set)"
        data_dir = os.environ.get("DATA_DIR", "").strip() or "(default)"
        log_info(f"MaByte boot — port={port} APP_BASE_URL={base} DATA_DIR={data_dir}")
        if not base.startswith("https://"):
            log_warning("APP_BASE_URL sollte https://mabyte.de fuer Production sein.")
    except Exception as exc:
        print(f"[MaByte] startup logging failed: {exc}", file=sys.stderr)


def bootstrap_database() -> None:
    try:
        from database import ensure_db_ready

        if not ensure_db_ready():
            print("[MaByte] WARN: database not ready — app starts in degraded mode.", file=sys.stderr)
    except Exception as exc:
        print(f"[MaByte] database bootstrap error: {exc}", file=sys.stderr)
        try:
            from logger import log_error
            log_error(f"Database bootstrap error: {exc}")
        except Exception:
            pass


# When started by gateway.py, env/DB are already initialized.
if not os.environ.get("MABYTE_GATEWAY_CHILD"):
    configure_production_env()
    log_startup()
    bootstrap_database()

# Streamlit executes this file; load the UI layer (ui.py).
import runpy

runpy.run_path(str(ROOT / "ui.py"), run_name="__streamlit__")
