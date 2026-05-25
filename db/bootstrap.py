"""Startup bootstrap helpers."""
from db.core import OWNER_USERNAME
from db.users import get_user, set_plan, set_role
from db.football_billing import set_football_plan


def force_owner_account():
    user = get_user(OWNER_USERNAME)

    if not user:
        return

    if user.get("role") != "owner" or int(user.get("admin_level") or 0) != 1337:
        set_role(OWNER_USERNAME, "owner", 1337)

    if user.get("plan") != "elite":
        set_plan(OWNER_USERNAME, "elite")
        set_football_plan(OWNER_USERNAME, "football_elite")
