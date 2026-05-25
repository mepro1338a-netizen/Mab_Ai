"""MaByte database facade — backward-compatible imports for `from database import ...`."""
from db.core import *  # noqa: F403
from db.audit import *  # noqa: F403
from db.support import *  # noqa: F403
from db.billing import *  # noqa: F403
from db.projects import *  # noqa: F403
from db.automations import *  # noqa: F403
from db.users import *  # noqa: F403  # includes secure_set_football_plan
from db.memory import *  # noqa: F403
from db.bootstrap import force_owner_account
from db.football_billing import (  # noqa: F401
    get_football_plan,
    set_football_plan,
    get_football_usage_today,
    record_football_api_call,
    record_football_ai_actions,
    record_football_ai_analysis,
)

init_db()
force_owner_account()
