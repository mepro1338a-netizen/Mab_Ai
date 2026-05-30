"""Lead capture — full registration profile stored per signup."""
from __future__ import annotations

import json

from db.core import get_connection, normalize_username, now, rows_to_dicts


def init_leads_table() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT NOT NULL,
        full_name TEXT,
        company TEXT,
        phone TEXT,
        country TEXT,
        use_case TEXT,
        marketing_opt_in INTEGER DEFAULT 0,
        terms_accepted INTEGER DEFAULT 0,
        status TEXT DEFAULT 'registered',
        source TEXT DEFAULT 'web_register',
        ip_address TEXT,
        user_agent TEXT,
        referrer TEXT,
        utm_json TEXT,
        meta_json TEXT,
        created_at TEXT,
        converted_at TEXT
    )
    """)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_leads_username ON leads(username)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at DESC)"
    )
    conn.commit()
    conn.close()


def save_lead(
    *,
    username: str,
    email: str,
    full_name: str,
    company: str = "",
    phone: str = "",
    country: str = "",
    use_case: str = "",
    marketing_opt_in: bool = False,
    terms_accepted: bool = False,
    ip_address: str = "",
    user_agent: str = "",
    referrer: str = "",
    utm: dict | None = None,
    meta: dict | None = None,
    status: str = "registered",
) -> int | None:
    """Persist complete lead snapshot; returns lead id."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO leads (
                username, email, full_name, company, phone, country,
                use_case, marketing_opt_in, terms_accepted, status, source,
                ip_address, user_agent, referrer, utm_json, meta_json,
                created_at, converted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                normalize_username(username),
                (email or "").strip().lower(),
                (full_name or "").strip(),
                (company or "").strip(),
                (phone or "").strip(),
                (country or "").strip(),
                (use_case or "").strip(),
                1 if marketing_opt_in else 0,
                1 if terms_accepted else 0,
                status,
                "web_register",
                (ip_address or "").strip()[:120],
                (user_agent or "").strip()[:500],
                (referrer or "").strip()[:500],
                json.dumps(utm or {}, ensure_ascii=False),
                json.dumps(meta or {}, ensure_ascii=False),
                now(),
                now() if status == "registered" else None,
            ),
        )
        lead_id = int(cur.lastrowid)
        conn.commit()
        return lead_id
    except Exception:
        conn.rollback()
        return None
    finally:
        conn.close()


def list_leads(*, limit: int = 200) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT * FROM leads
        ORDER BY id DESC
        LIMIT ?
        """,
        (int(limit),),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def lead_count() -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) AS c FROM leads").fetchone()
    conn.close()
    return int(row["c"] or 0) if row else 0
