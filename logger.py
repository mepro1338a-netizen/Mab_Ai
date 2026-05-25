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
        for key in ("user", "page", "provider", "status_code", "event"):
            val = getattr(record, key, None)
            if val is not None:
                payload[key] = _redact(str(val))
        return json.dumps(payload, ensure_ascii=False)


logger = logging.getLogger("mabyte")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    fh = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=8, encoding="utf-8")
    fh.setFormatter(JsonFormatter())
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
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
        from db.errors import record_app_error
        record_app_error(category, type(exc).__name__, str(exc), page=page, username=user)
    except Exception:
        pass


def user_friendly_error(category: str, technical: str = "") -> str:
    """Safe UI messages — never expose stack traces."""
    messages = {
        "auth": "Anmeldung fehlgeschlagen. Bitte Zugangsdaten prüfen.",
        "oauth": "Social Login vorübergehend nicht verfügbar. Bitte erneut versuchen.",
        "stripe": "Zahlung konnte nicht gestartet werden. Bitte später erneut versuchen.",
        "api": "Externer Dienst antwortet nicht. Bitte kurz warten.",
        "football": "Football-Daten temporär nicht verfügbar.",
        "system": "Ein Fehler ist aufgetreten. Bitte Seite neu laden oder Support kontaktieren.",
    }
    base = messages.get(category, messages["system"])
    if os.getenv("MABYTE_DEBUG", "").strip() == "1" and technical:
        return f"{base} ({_redact(technical)[:120]})"
    return base
