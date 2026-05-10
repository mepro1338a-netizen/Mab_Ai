# =========================================================
# costs.py
# =========================================================

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

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS api_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            tool TEXT,
            provider TEXT,
            estimated_cost_eur REAL DEFAULT 0,
            tokens_charged INTEGER DEFAULT 0,
            revenue_eur REAL DEFAULT 0,
            margin_eur REAL DEFAULT 0,
            seconds INTEGER DEFAULT 0,
            quality TEXT,
            created_at TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def token_value_eur():
    return 9.99 / 600


def estimate_cost(tool, seconds=0, quality="Standard"):
    seconds = int(seconds or 0)

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
        cost = 0.10 + (seconds * 0.014)

        if quality == "High":
            cost *= 1.35

        if quality == "Business Level":
            cost *= 1.75

        return round(cost, 4)

    if tool == "reels_video":
        cost = 0.12 + (seconds * 0.014)

        if quality == "High":
            cost *= 1.35

        if quality == "Business Level":
            cost *= 1.75

        return round(cost, 4)

    return 0.01


def record_cost(
    username,
    tool,
    provider,
    tokens_charged,
    seconds=0,
    quality="Standard",
):
    init_costs()

    estimated_cost = estimate_cost(tool, seconds, quality)
    revenue = int(tokens_charged or 0) * token_value_eur()
    margin = revenue - estimated_cost

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO api_costs (
            username,
            tool,
            provider,
            estimated_cost_eur,
            tokens_charged,
            revenue_eur,
            margin_eur,
            seconds,
            quality,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            tool,
            provider,
            float(estimated_cost),
            int(tokens_charged or 0),
            float(round(revenue, 4)),
            float(round(margin, 4)),
            int(seconds or 0),
            quality,
            now(),
        ),
    )

    conn.commit()
    conn.close()

    return {
        "estimated_cost_eur": round(estimated_cost, 4),
        "revenue_eur": round(revenue, 4),
        "margin_eur": round(margin, 4),
    }


def list_costs(limit=500):
    init_costs()

    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute(
        """
        SELECT *
        FROM api_costs
        ORDER BY id DESC
        LIMIT ?
        """,
        (int(limit),),
    ).fetchall()

    conn.close()

    return [dict(r) for r in rows]


def cost_summary():
    init_costs()

    conn = get_connection()
    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT
            COALESCE(SUM(estimated_cost_eur), 0) AS api_costs,
            COALESCE(SUM(revenue_eur), 0) AS revenue,
            COALESCE(SUM(margin_eur), 0) AS margin
        FROM api_costs
        """
    ).fetchone()

    conn.close()

    return {
        "api_costs": round(float(row["api_costs"] or 0), 4),
        "revenue": round(float(row["revenue"] or 0), 4),
        "margin": round(float(row["margin"] or 0), 4),
    }


def emergency_cost_limit_reached(max_daily_cost=50):
    init_costs()

    today = datetime.utcnow().date().isoformat()

    conn = get_connection()
    cur = conn.cursor()

    row = cur.execute(
        """
        SELECT COALESCE(SUM(estimated_cost_eur), 0) AS today_cost
        FROM api_costs
        WHERE created_at LIKE ?
        """,
        (f"{today}%",),
    ).fetchone()

    conn.close()

    today_cost = float(row["today_cost"] or 0)

    return today_cost >= float(max_daily_cost), round(today_cost, 4)