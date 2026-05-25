"""Health / diagnostics for Railway and local ops."""
from __future__ import annotations

import os
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path


def check_path() -> None:
    from config import DATA_DIR, DB_PATH

    print("=== PATH CHECK ===")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"DB_PATH: {DB_PATH}")
    print(f"DATA_DIR exists: {Path(DATA_DIR).exists()}")
    print(f"DB exists: {Path(DB_PATH).exists()}")
    if Path(DATA_DIR).exists():
        print(f"DATA_DIR files: {os.listdir(DATA_DIR)}")


def check_database() -> None:
    from config import DB_PATH

    print("\n=== DATABASE CHECK ===")
    if not Path(DB_PATH).exists():
        print("DB file missing — ensure_db_ready not run yet.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    tables = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    print("Tables:", [t[0] for t in tables])
    conn.close()


def check_http_health(port: int | None = None) -> bool:
    """Streamlit 1.28+ health endpoint (Railway healthcheckPath)."""
    port = port or int(os.environ.get("PORT", "8501"))
    url = f"http://127.0.0.1:{port}/_stcore/health"
    print(f"\n=== HTTP HEALTH {url} ===")
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            ok = resp.status == 200
            print(f"Status: {resp.status} OK={ok}")
            return ok
    except urllib.error.URLError as exc:
        print(f"Health check failed: {exc}")
        return False


def check_env() -> None:
    print("\n=== ENV (presence only) ===")
    keys = (
        "PORT",
        "APP_BASE_URL",
        "DATA_DIR",
        "OPENAI_API_KEY",
        "GOOGLE_CLIENT_ID",
        "OAUTH_STATE_SECRET",
        "STRIPE_SECRET_KEY",
        "FOOTBALL_API_KEY",
    )
    for key in keys:
        val = os.environ.get(key, "")
        print(f"{key}: {'set' if val else 'missing'}")


if __name__ == "__main__":
    check_env()
    check_path()
    check_database()
    if "--http" in sys.argv:
        ok = check_http_health()
        sys.exit(0 if ok else 1)
