"""API reliability — retries, timeouts, graceful fallbacks."""
from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable, TypeVar

import streamlit as st

from logger import log_api, log_exception, user_friendly_error

T = TypeVar("T")


def with_retry(
    fn: Callable[..., T],
    *,
    retries: int = 2,
    delay: float = 0.4,
    category: str = "api",
) -> Callable[..., T]:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        last_exc: Exception | None = None
        for attempt in range(retries + 1):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                last_exc = exc
                log_exception(exc, category=category)
                if attempt < retries:
                    time.sleep(delay * (attempt + 1))
        if last_exc:
            raise last_exc
        raise RuntimeError("retry failed")
    return wrapper


def safe_call(
    fn: Callable[..., T],
    *args,
    default: T | None = None,
    category: str = "api",
    user_message: str | None = None,
    **kwargs,
) -> T | None:
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        log_exception(exc, category=category)
        if user_message:
            st.warning(user_message)
        else:
            st.warning(user_friendly_error(category, str(exc)))
        return default


def show_loading(message: str = "Lädt…") -> Any:
    return st.spinner(message)


def api_status_badge(service: str, ok: bool) -> None:
    color = "#22c55e" if ok else "#f59e0b"
    label = "Online" if ok else "Degraded"
    st.markdown(
        f'<span style="color:{color};font-weight:900;font-size:12px;">{service}: {label}</span>',
        unsafe_allow_html=True,
    )


def record_api_health(service: str, success: bool, status_code: int | None = None) -> None:
    st.session_state.setdefault("api_health", {})
    st.session_state.api_health[service] = {
        "ok": success,
        "status_code": status_code,
        "at": time.time(),
    }
    log_api(
        f"{service} {'ok' if success else 'fail'}",
        provider=service,
        status_code=status_code,
    )
