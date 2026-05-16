from database import create_user, verify_login, get_user


def login_user(username, password):
    return verify_login(username, password)


def register_user(username, email, password):
    return create_user(
        username=username,
        email=email,
        password=password,
        role="user",
        plan="free",
    )


def current_user(username):
    if not username:
        return None
    return get_user(username)


def is_admin_user(user):
    if not user:
        return False

    role = user.get("role", "user")
    admin_level = int(user.get("admin_level", 0))

    return role in ["supporter", "moderator", "admin", "owner"] or admin_level > 0


def is_owner_user(user):
    if not user:
        return False

    role = user.get("role", "user")
    admin_level = int(user.get("admin_level", 0))

    return role == "owner" or admin_level >= 3

