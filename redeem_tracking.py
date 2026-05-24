import sqlite3
from datetime import datetime

from config import DB_PATH


def _connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def redeem_code_tracked(
    username,
    code,
    ip_address="unknown",
    user_agent="unknown",
):
    conn = _connect()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS redeem_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            code TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TEXT
        )
    """)

    c.execute("""
        INSERT INTO redeem_logs (
            username,
            code,
            ip_address,
            user_agent,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        username,
        code,
        ip_address,
        user_agent,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))

    conn.commit()
    conn.close()


def list_redeem_redemptions():
    conn = _connect()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS redeem_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            code TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TEXT
        )
    """)

    c.execute("""
        SELECT *
        FROM redeem_logs
        ORDER BY id DESC
    """)

    rows = c.fetchall()
    conn.close()
    return rows
