"""MaByte database facade — backward-compatible imports for `from database import ...`."""
import sys

from db.core import *  # noqa: F403
from db.audit import *  # noqa: F403
from db.support import *  # noqa: F403
from db.billing import *  # noqa: F403
from db.projects import *  # noqa: F403
from db.automations import *  # noqa: F403
from db.users import *  # noqa: F403  # includes secure_set_football_plan
from db.memory import *  # noqa: F403
from db.errors import *  # noqa: F403
from db.bootstrap import force_owner_account
from db.billing import payment_already_paid  # noqa: F401
from db.football_billing import (  # noqa: F401
    get_football_plan,
    set_football_plan,
    get_football_usage_today,
    record_football_api_call,
    record_football_ai_actions,
    record_football_ai_analysis,
)

_db_ready = False


def ensure_db_ready() -> bool:
    """Idempotent DB init — safe for Railway cold starts."""
    global _db_ready
    if _db_ready:
        return True
    try:
        init_db()
        force_owner_account()
        _db_ready = True
        try:
            from logger import log_info
            log_info("Database initialized.")
        except Exception:
            pass
        return True
    except Exception as exc:
        try:
            from logger import log_error
            log_error(f"ensure_db_ready failed: {exc}")
        except Exception:
            print(f"[MaByte] ensure_db_ready failed: {exc}", file=sys.stderr)
        return False
