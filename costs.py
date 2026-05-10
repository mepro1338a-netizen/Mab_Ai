import sqlite3
from datetime import datetime

from config import DB_PATH


def now():
    return datetime.utcnow().isoformat()


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_costs():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS api_costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        tool TEXT,
        provider TEXT,
        estimated_cost_eur REAL DEFAULT 0,
        tokens_charged INTEGER DEFAULT 0,
        margin_eur REAL DEFAULT 0,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def token_value_eur():
    return 9.99 / 600


def estimate_cost(tool, seconds=0, quality="Standard"):
    if tool == "chat":
        return 0.002

    if tool == "coding":
        return 0.006

    if tool == "image":
        return 0.04

    if tool == "music":
        return 0.03

    if tool == "reels":
        return 0.015

    if tool == "video":
        base = 0.10 + (float(seconds) * 0.014)

        if quality == "High":
            base *= 1.35

        if quality == "Business Level":
            base *= 1.75

        return round(base, 4)

    if tool == "reels_video":
        base = 0.12 + (float(seconds) * 0.014)
        return round(base, 4)

    return 0.01


def record_cost(username, tool, provider, tokens_charged, seconds=0, quality="Standard"):
    init_costs()

    estimated = estimate_cost(tool, seconds, quality)
    revenue = int(tokens_charged) * token_value_eur()
    margin = revenue - estimated

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO api_costs (
        username,
        tool,
        provider,
        estimated_cost_eur,
        tokens_charged,
        margin_eur,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        username,
        tool,
        provider,
        float(estimated),
        int(tokens_charged),
        float(round(margin, 4)),
        now()
    ))

    conn.commit()
    conn.close()

    return {
        "estimated_cost_eur": estimated,
        "revenue_eur": round(revenue, 4),
        "margin_eur": round(margin, 4),
    }