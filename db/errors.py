"""Application error log for admin analytics."""
from db.core import get_connection, now, rows_to_dicts


def record_app_error(
    category: str,
    error_type: str,
    message: str,
    *,
    page: str = "",
    username: str = "",
) -> None:
    msg = (message or "")[:500]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO app_error_logs (category, error_type, message, page, username, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            (category or "system")[:40],
            (error_type or "Error")[:80],
            msg,
            (page or "")[:60],
            (username or "")[:80],
            now(),
        ),
    )
    conn.commit()
    conn.close()


def errors_last_24h(limit: int = 50) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT * FROM app_error_logs
        WHERE created_at >= datetime('now', '-1 day')
        ORDER BY id DESC
        LIMIT ?
        """,
        (int(limit),),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def error_counts_24h() -> dict:
    conn = get_connection()
    cur = conn.cursor()
    total = cur.execute(
        """
        SELECT COUNT(*) AS c FROM app_error_logs
        WHERE created_at >= datetime('now', '-1 day')
        """
    ).fetchone()["c"]
    by_cat = cur.execute(
        """
        SELECT category, COUNT(*) AS c FROM app_error_logs
        WHERE created_at >= datetime('now', '-1 day')
        GROUP BY category
        ORDER BY c DESC
        """
    ).fetchall()
    conn.close()
    return {"total": total, "by_category": {r["category"]: r["c"] for r in by_cat}}
