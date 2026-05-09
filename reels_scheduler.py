from db_manager import execute, fetch_all


def init_scheduler_table():
    execute("""
    CREATE TABLE IF NOT EXISTS scheduled_reels (
        id SERIAL PRIMARY KEY,
        username TEXT,
        platform TEXT,
        content TEXT,
        scheduled_time TIMESTAMP,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)


def schedule_reel(username, platform, content, scheduled_time):
    execute("""
    INSERT INTO scheduled_reels (
        username,
        platform,
        content,
        scheduled_time,
        status
    )
    VALUES (%s, %s, %s, %s, 'pending')
    """, (
        username,
        platform,
        content,
        scheduled_time,
    ))


def list_scheduled_reels(username):
    return fetch_all("""
    SELECT *
    FROM scheduled_reels
    WHERE username=%s
    ORDER BY scheduled_time ASC
    """, (username,))
