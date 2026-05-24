"""One-off: split database.py into db/* modules and write compatibility facade."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "database.py"
ARCHIVE = ROOT / "archive" / "legacy"
ARCHIVE.mkdir(parents=True, exist_ok=True)

text = SRC.read_text(encoding="utf-8")
lines = text.splitlines(keepends=True)
(ARCHIVE / "database_monolith_backup.py").write_text(text, encoding="utf-8")


def chunk(start: int, end: int) -> str:
    return "".join(lines[start - 1 : end])


CORE = '''"""SQLite connection helpers and schema initialization."""
import sqlite3
from datetime import datetime

from config import DB_PATH

OWNER_USERNAME = "mepro1337"

ROLE_LEVELS = {
    "user": 0,
    "supporter": 1,
    "moderator": 2,
    "admin": 3,
    "owner": 1337,
}


def now():
    return datetime.utcnow().isoformat()


def normalize_username(username):
    return (username or "").strip().lower()


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def row_to_dict(row):
    return dict(row) if row else None


def rows_to_dicts(rows):
    return [dict(row) for row in rows]


''' + chunk(46, 162)

USERS = '''"""Users, auth, roles, tokens."""
import re
import sqlite3
import secrets

import bcrypt

from config import PLANS

from db.core import (
    OWNER_USERNAME,
    ROLE_LEVELS,
    get_connection,
    normalize_username,
    now,
    row_to_dict,
    rows_to_dicts,
)
from db.audit import add_audit_log

''' + chunk(165, 735)

SUPPORT = '''"""Support tickets."""
from db.core import get_connection, normalize_username, now, rows_to_dicts

''' + chunk(737, 837)

BILLING = '''"""Redeem codes, usage analytics, payments."""
import secrets
import sqlite3
from datetime import datetime, timedelta

from db.core import get_connection, normalize_username, now, rows_to_dicts

''' + chunk(840, 1203)

AUDIT = '''"""Login logs and admin audit trail."""
from db.core import get_connection, normalize_username, now, rows_to_dicts

''' + chunk(1205, 1263) + chunk(1789, 1819)

PROJECTS = '''"""Projects, project memory, chat memory."""
from db.core import get_connection, normalize_username, now, row_to_dict, rows_to_dicts

''' + chunk(1265, 1487)

AUTOMATIONS = '''"""Automations and runs."""
from db.core import get_connection, normalize_username, now, rows_to_dicts

''' + chunk(1489, 1672)

MEMORY = '''"""Global memory and automation unlock flags."""
from db.core import get_connection, normalize_username, now, rows_to_dicts

''' + chunk(1674, 1787)

BOOTSTRAP = '''"""Startup bootstrap helpers."""
from db.core import OWNER_USERNAME
from db.users import get_user, set_plan, set_role


def force_owner_account():
    user = get_user(OWNER_USERNAME)

    if not user:
        return

    if user.get("role") != "owner" or int(user.get("admin_level") or 0) != 1337:
        set_role(OWNER_USERNAME, "owner", 1337)

    if user.get("plan") != "elite":
        set_plan(OWNER_USERNAME, "elite")
'''

FACADE = '''"""MaByte database facade — backward-compatible imports for `from database import ...`."""
from db.core import *  # noqa: F403
from db.audit import *  # noqa: F403
from db.support import *  # noqa: F403
from db.billing import *  # noqa: F403
from db.projects import *  # noqa: F403
from db.automations import *  # noqa: F403
from db.memory import *  # noqa: F403
from db.users import *  # noqa: F403
from db.bootstrap import force_owner_account

init_db()
force_owner_account()
'''

DB_PKG = ROOT / "db"
DB_PKG.mkdir(exist_ok=True)
(DB_PKG / "__init__.py").write_text('"""MaByte SQLite data layer (split modules)."""\n', encoding="utf-8")

(DB_PKG / "core.py").write_text(CORE, encoding="utf-8")
(DB_PKG / "audit.py").write_text(AUDIT, encoding="utf-8")
(DB_PKG / "support.py").write_text(SUPPORT, encoding="utf-8")
(DB_PKG / "billing.py").write_text(BILLING, encoding="utf-8")
(DB_PKG / "projects.py").write_text(PROJECTS, encoding="utf-8")
(DB_PKG / "automations.py").write_text(AUTOMATIONS, encoding="utf-8")
(DB_PKG / "memory.py").write_text(MEMORY, encoding="utf-8")
(DB_PKG / "users.py").write_text(USERS, encoding="utf-8")
(DB_PKG / "bootstrap.py").write_text(BOOTSTRAP, encoding="utf-8")
SRC.write_text(FACADE, encoding="utf-8")
print("db split complete")
