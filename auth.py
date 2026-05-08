from database import create_user, verify_user


def login_user(username, password):
    return verify_user(username, password)


def register_user(username, email, password):
    return create_user(username, email, password, role="user", plan="free", tokens=0)
