"""MaByte structured logging — Railway-safe, no secrets in logs."""
from __future__ import annotations

import json
import logging
import os
import re
import traceback
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Any

from config import DATA_DIR

LOG_DIR = os.path.join(str(DATA_DIR), "logs")
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except OSError:
    LOG_DIR = os.path.join("/tmp", "mabyte_logs")
    os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "mabyte.log")

_SECRET_PATTERNS = re.compile(
    r"(api[_-]?key|secret|password|token|authorization|bearer|stripe|oauth)[\s=:\"]+[\w\-\.]+",
    re.I,
)


def _redact(text: str) -> str:
    if not text:
        return ""
    s = str(text)
    s = _SECRET_PATTERNS.sub(r"\1=***REDACTED***", s)
    if len(s) > 2000:
        s = s[:2000] + "…"
    return s


_LOG_RECORD_SKIP = frozenset({
    "name", "msg", "args", "created", "filename", "funcName", "levelname", "levelno",
    "lineno", "module", "msecs", "message", "pathname", "process", "processName",
    "relativeCreated", "stack_info", "exc_info", "exc_text", "thread", "threadName",
    "taskName",
})


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "category": getattr(record, "category", "system"),
            "message": _redact(record.getMessage()),
        }
        if record.exc_info:
            payload["trace"] = _redact("".join(traceback.format_exception(*record.exc_info)))
        for key, val in record.__dict__.items():
            if key in _LOG_RECORD_SKIP or val is None:
                continue
            if key == "category":
                continue
            payload[key] = _redact(str(val))
        return json.dumps(payload, ensure_ascii=False)


logger = logging.getLogger("mabyte")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    fh = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=8, encoding="utf-8")
    fh.setFormatter(JsonFormatter())
    ch = logging.StreamHandler()

    class _ConsoleFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            base = super().format(record)
            bits = [
                getattr(record, "plan_key", None),
                getattr(record, "stripe_error", None),
                getattr(record, "success_url", None),
            ]
            extra = " | ".join(_redact(str(b)) for b in bits if b)
            return f"{base} | {extra}" if extra else base

    ch.setFormatter(_ConsoleFormatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(fh)
    logger.addHandler(ch)


def _log(level: int, category: str, message: str, **extra: Any) -> None:
    logger.log(level, _redact(message), extra={"category": category, **extra})


def log_info(message: str, category: str = "system", **extra: Any) -> None:
    _log(logging.INFO, category, message, **extra)


def log_warning(message: str, category: str = "system", **extra: Any) -> None:
    _log(logging.WARNING, category, message, **extra)


def log_error(message: str, category: str = "system", **extra: Any) -> None:
    _log(logging.ERROR, category, message, **extra)


def log_auth(event: str, username: str = "", success: bool = True, **extra: Any) -> None:
    _log(
        logging.INFO if success else logging.WARNING,
        "auth",
        event,
        user=username or "—",
        event=event,
        **extra,
    )


def log_oauth(event: str, provider: str = "", success: bool = True, **extra: Any) -> None:
    _log(
        logging.INFO if success else logging.WARNING,
        "oauth",
        event,
        provider=provider,
        event=event,
        **extra,
    )


def log_stripe(event: str, username: str = "", success: bool = True, **extra: Any) -> None:
    _log(
        logging.INFO if success else logging.ERROR,
        "stripe",
        event,
        user=username or "—",
        event=event,
        **extra,
    )


def log_api(event: str, provider: str = "", status_code: int | None = None, **extra: Any) -> None:
    _log(
        logging.INFO if (status_code or 200) < 400 else logging.ERROR,
        "api",
        event,
        provider=provider,
        status_code=status_code,
        event=event,
        **extra,
    )


def log_exception(exc: BaseException, *, category: str = "system", page: str = "", user: str = "") -> None:
    _log(
        logging.ERROR,
        category,
        f"{type(exc).__name__}: {exc}",
        page=page,
        user=user,
    )
    try:
        from db.app import record_app_error
        record_app_error(category, type(exc).__name__, str(exc), page=page, username=user)
    except Exception:
        pass


def user_friendly_error(category: str, technical: str = "") -> str:
    """Safe UI messages — never expose stack traces."""
    messages = {
        "auth": "Anmeldung fehlgeschlagen. Bitte Zugangsdaten prüfen.",
        "oauth": "Anmeldung mit Google vorübergehend nicht verfügbar. Bitte erneut versuchen.",
        "stripe": "Zahlung konnte nicht gestartet werden. Bitte später erneut versuchen.",
        "api": "Externer Dienst antwortet nicht. Bitte kurz warten.",
        "football": "Football-Daten temporär nicht verfügbar.",
        "system": "Ein Fehler ist aufgetreten. Bitte Seite neu laden oder Support kontaktieren.",
    }
    base = messages.get(category, messages["system"])
    if os.getenv("MABYTE_DEBUG", "").strip() == "1" and technical:
        return f"{base} ({_redact(technical)[:120]})"
    return base


# ---------------------------------------------------------------------------
# Ops diagnostics — was healthcheck.py (python logger.py --healthcheck)
# ---------------------------------------------------------------------------

def check_path() -> None:
    from config import DATA_DIR, DB_PATH

    print("=== PATH CHECK ===")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"DB_PATH: {DB_PATH}")
    print(f"DATA_DIR exists: {os.path.exists(DATA_DIR)}")
    print(f"DB exists: {os.path.exists(DB_PATH)}")
    if os.path.exists(DATA_DIR):
        print(f"DATA_DIR files: {os.listdir(DATA_DIR)}")


def check_database() -> None:
    import sqlite3
    from config import DB_PATH

    print("\n=== DATABASE CHECK ===")
    if not os.path.exists(DB_PATH):
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
    import urllib.error
    import urllib.request

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
    import sys

    if "--healthcheck" in sys.argv:
        check_env()
        check_path()
        check_database()
        if "--http" in sys.argv:
            ok = check_http_health()
            sys.exit(0 if ok else 1)
