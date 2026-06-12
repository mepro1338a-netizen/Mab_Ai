"""Support tickets + replies timeline."""
from db.core import get_connection, normalize_username, now, rows_to_dicts

PRIORITIES = ("low", "normal", "high", "urgent")
STATUSES = ("open", "in_progress", "closed")


def create_support_message(
    username,
    email,
    category,
    subject,
    message,
    priority: str = "normal",
):
    priority = (priority or "normal").strip().lower()
    if priority not in PRIORITIES:
        priority = "normal"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO support_tickets (
        username,
        email,
        category,
        subject,
        message,
        status,
        priority,
        created_at,
        updated_at
    )
    VALUES (?, ?, ?, ?, ?, 'open', ?, ?, ?)
    """, (
        normalize_username(username),
        email,
        category,
        subject,
        message,
        priority,
        now(),
        now(),
    ))

    ticket_id = cur.lastrowid
    conn.commit()
    conn.close()

    return True, f"Ticket #{ticket_id} erstellt."


def list_support_messages(status_filter="all"):
    conn = get_connection()
    cur = conn.cursor()

    if status_filter == "all":
        rows = cur.execute(
            "SELECT * FROM support_tickets ORDER BY id DESC"
        ).fetchall()
    else:
        rows = cur.execute(
            "SELECT * FROM support_tickets WHERE status = ? ORDER BY id DESC",
            (status_filter,),
        ).fetchall()

    conn.close()
    return rows_to_dicts(rows)


def support_counts():
    conn = get_connection()
    cur = conn.cursor()

    total = cur.execute(
        "SELECT COUNT(*) AS c FROM support_tickets"
    ).fetchone()["c"]

    open_count = cur.execute(
        "SELECT COUNT(*) AS c FROM support_tickets WHERE status IN ('open', 'in_progress')"
    ).fetchone()["c"]

    closed_count = cur.execute(
        "SELECT COUNT(*) AS c FROM support_tickets WHERE status='closed'"
    ).fetchone()["c"]

    conn.close()

    return {
        "total": total,
        "open": open_count,
        "closed": closed_count,
        "unread": open_count,
    }


def set_support_status(ticket_id, status):
    status = (status or "open").strip().lower()
    if status not in STATUSES:
        status = "open"

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE support_tickets SET status = ?, updated_at = ? WHERE id = ?",
        (status, now(), int(ticket_id)),
    )

    conn.commit()
    conn.close()


def set_support_priority(ticket_id, priority: str):
    priority = (priority or "normal").strip().lower()
    if priority not in PRIORITIES:
        priority = "normal"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE support_tickets SET priority = ?, updated_at = ? WHERE id = ?",
        (priority, now(), int(ticket_id)),
    )
    conn.commit()
    conn.close()


def add_ticket_reply(ticket_id: int, author: str, body: str, *, is_staff: bool = False):
    body = (body or "").strip()
    if not body:
        return False, "Nachricht leer."

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO support_ticket_replies (ticket_id, author, body, is_staff, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (int(ticket_id), normalize_username(author), body, 1 if is_staff else 0, now()),
    )
    cur.execute(
        "UPDATE support_tickets SET updated_at = ? WHERE id = ?",
        (now(), int(ticket_id)),
    )
    conn.commit()
    conn.close()
    return True, "Antwort gespeichert."


def list_ticket_replies(ticket_id: int) -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT * FROM support_ticket_replies
        WHERE ticket_id = ?
        ORDER BY id ASC
        """,
        (int(ticket_id),),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def delete_support_message(ticket_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM support_ticket_replies WHERE ticket_id = ?",
        (int(ticket_id),),
    )
    cur.execute(
        "DELETE FROM support_tickets WHERE id = ?",
        (int(ticket_id),),
    )

    conn.commit()
    conn.close()
