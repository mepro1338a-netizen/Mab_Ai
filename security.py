import time
import re
from collections import defaultdict

LOGIN_ATTEMPTS = defaultdict(list)
RATE_LIMITS = defaultdict(list)

MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 300

MAX_REQUESTS = 60
REQUEST_WINDOW_SECONDS = 60


def clean_text(value: str, max_length: int = 5000) -> str:
    value = str(value or "").strip()
    value = value[:max_length]
    return value


def is_valid_username(username: str) -> bool:
    username = clean_text(username, 40)
    return bool(re.match(r"^[a-zA-Z0-9_]{3,40}$", username))


def is_valid_email(email: str) -> bool:
    email = clean_text(email, 120)
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def check_login_rate(username: str):
    now = time.time()
    username = clean_text(username, 40).lower()

    LOGIN_ATTEMPTS[username] = [
        t for t in LOGIN_ATTEMPTS[username]
        if now - t < LOGIN_WINDOW_SECONDS
    ]

    if len(LOGIN_ATTEMPTS[username]) >= MAX_LOGIN_ATTEMPTS:
        return False, "Zu viele Login-Versuche. Bitte 5 Minuten warten."

    LOGIN_ATTEMPTS[username].append(now)
    return True, ""


def check_rate_limit(key: str):
    now = time.time()
    key = clean_text(key, 100)

    RATE_LIMITS[key] = [
        t for t in RATE_LIMITS[key]
        if now - t < REQUEST_WINDOW_SECONDS
    ]

    if len(RATE_LIMITS[key]) >= MAX_REQUESTS:
        return False, "Rate Limit erreicht. Bitte kurz warten."

    RATE_LIMITS[key].append(now)
    return True, ""


def is_admin(user: dict) -> bool:
    if not user:
        return False

    role = user.get("role", "user")
    admin_level = int(user.get("admin_level", 0) or 0)

    return role in ["admin", "owner"] or admin_level >= 1


def is_owner(user: dict) -> bool:
    if not user:
        return False

    return user.get("role") == "owner" or int(user.get("admin_level", 0) or 0) >= 999