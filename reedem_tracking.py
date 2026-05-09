from db_manager import execute, fetch_all


def init_redeem_tracking():
    execute("""
    CREATE TABLE IF NOT EXISTS redeem_redemptions (
        id SERIAL PRIMARY KEY,
        username TEXT,
        code TEXT,
        ip_address TEXT,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)


def log_redeem(
    username,
    code,
    ip_address="unknown",
    user_agent="unknown",
):
    execute("""
    INSERT INTO redeem_redemptions (
        username,
        code,
        ip_address,
        user_agent
    )
    VALUES (%s, %s, %s, %s)
    """, (
        username,
        code,
        ip_address,
        user_agent,
    ))


def list_redeem_redemptions():
    return fetch_all("""
    SELECT *
    FROM redeem_redemptions
    ORDER BY created_at DESC
    LIMIT 500
    """)
