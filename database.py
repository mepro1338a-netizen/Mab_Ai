"""MaByte database facade — backward-compatible imports for `from database import ...`."""
import sys

from db.core import *  # noqa: F403
from db.users import *  # noqa: F403  # includes secure_set_football_plan, register_account
from db.video_engine import *  # noqa: F403
from db.app import *  # noqa: F403

from db.app import force_owner_account  # noqa: F401

# Keep compatibility for payments module
from db.billing import record_purchase  # noqa: F401
from db.billing import payment_already_paid  # noqa: F401
from db.billing import list_usage, recent_activity, usage_summary  # noqa: F401

# Back-compat explicit imports (some modules import from database directly)
from db.app import (  # noqa: F401
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
