import sqlite3
from config import DB_PATH


def column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cur.fetchall()]
    return column in columns


def run_migrations():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Running migrations...")

    # USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user',
        admin_level INTEGER DEFAULT 0,
        plan TEXT DEFAULT 'free',
        tokens INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ADD MISSING COLUMNS
    migrations = [
        ("users", "role", "TEXT DEFAULT 'user'"),
        ("users", "admin_level", "INTEGER DEFAULT 0"),
        ("users", "plan", "TEXT DEFAULT 'free'"),
        ("users", "tokens", "INTEGER DEFAULT 0"),
    ]

    for table, column, definition in migrations:
        if not column_exists(cur, table, column):
            print(f"Adding column: {column}")

            cur.execute(f"""
            ALTER TABLE {table}
            ADD COLUMN {column} {definition}
            """)

    conn.commit()
    conn.close()

    print("Migrations complete.")

run_migrations()

