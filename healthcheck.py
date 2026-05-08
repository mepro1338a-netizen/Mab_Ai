import os
import sqlite3
from pathlib import Path

from config import DB_PATH, DATA_DIR


def check_path():
    print("=== PATH CHECK ===")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"DB_PATH: {DB_PATH}")
    print(f"DATA_DIR exists: {Path(DATA_DIR).exists()}")
    print(f"DB exists: {Path(DB_PATH).exists()}")

    if Path(DATA_DIR).exists():
        print(f"DATA_DIR files: {os.listdir(DATA_DIR)}")


def check_database():
    print("\n=== DATABASE CHECK ===")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    tables = cur.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table'
    ORDER BY name
    """).fetchall()

    print("Tables:")
    for table in tables:
        print("-", table[0])

    try:
        users = cur.execute("""
        SELECT username, role, admin_level, plan, tokens
        FROM users
        ORDER BY id DESC
        """).fetchall()

        print("\nUsers:")
        for user in users:
            print(user)

    except Exception as e:
        print("Users check failed:", e)

    conn.close()


if __name__ == "__main__":
    check_path()
    check_database()