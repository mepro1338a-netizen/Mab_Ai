from database import create_user, verify_user


def register_user(username, email, password):
    return create_user(username, email, password)


def login_user(username, password):
    return verify_user(username, password)
