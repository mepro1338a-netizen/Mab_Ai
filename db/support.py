"""Support tickets."""
from db.core import get_connection, normalize_username, now, rows_to_dicts

def create_support_message(username, email, category, subject, message):
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
    VALUES (?, ?, ?, ?, ?, 'open', 'normal', ?, ?)
    """, (
        normalize_username(username),
        email,
        category,
        subject,
        message,
        now(),
        now(),
    ))

    conn.commit()
    conn.close()

    return True, "Ticket erstellt."


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
        "SELECT COUNT(*) AS c FROM support_tickets WHERE status='open'"
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
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE support_tickets SET status = ?, updated_at = ? WHERE id = ?",
        (status, now(), int(ticket_id)),
    )

    conn.commit()
    conn.close()


def delete_support_message(ticket_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM support_tickets WHERE id = ?",
        (int(ticket_id),),
    )

    conn.commit()
    conn.close()
