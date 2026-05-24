"""MaByte database facade — backward-compatible imports for `from database import ...`."""
from db.core import *  # noqa: F403
from db.audit import *  # noqa: F403
from db.support import *  # noqa: F403
from db.billing import *  # noqa: F403
from db.projects import *  # noqa: F403
from db.automations import *  # noqa: F403
from db.users import *  # noqa: F403
from db.memory import *  # noqa: F403
from db.bootstrap import force_owner_account

init_db()
force_owner_account()
