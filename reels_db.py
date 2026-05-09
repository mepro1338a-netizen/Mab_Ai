from db_manager import fetch_all, execute


def init_reels_table():
    execute("""
    CREATE TABLE IF NOT EXISTS reels (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL,
        topic TEXT,
        niche TEXT,
        platform TEXT,
        style TEXT,
        duration INTEGER,
        content TEXT,
        status TEXT DEFAULT 'draft',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)


def save_reel(username, topic, niche, platform, style, duration, content):
    execute("""
    INSERT INTO reels (
        username, topic, niche, platform, style, duration, content, status
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, 'draft')
    """, (username, topic, niche, platform, style, duration, content))


def list_reels(username):
    return fetch_all(
        "SELECT * FROM reels WHERE username=%s ORDER BY created_at DESC",
        (username,)
    )
