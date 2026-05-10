import sqlite3
import secrets
import string
from datetime import datetime

import pandas as pd
import streamlit as st

from config import DB_PATH


ROLE_NAMES = {
    1: "Supporter",
    2: "Moderator",
    3: "Admin",
    1337: "Owner",
}


def conn():
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def query(sql, params=()):
    c = conn()
    cur = c.cursor()

    cur.execute(sql, params)

    rows = cur.fetchall()

    c.commit()
    c.close()

    return rows


def execute(sql, params=()):
    c = conn()
    cur = c.cursor()

    cur.execute(sql, params)

    c.commit()
    c.close()


def get_level():
    return int(st.session_state.get("admin_level", 0))


def require_admin(min_level=1):
    if get_level() < min_level:
        st.error("Kein Zugriff.")
        st.stop()


def render_overview():
    users = query("SELECT COUNT(*) as c FROM users")[0]["c"]
    tickets = query("SELECT COUNT(*) as c FROM support_tickets")[0]["c"]
    codes = query("SELECT COUNT(*) as c FROM redeem_codes")[0]["c"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="admin-stat-card">
                <div class="admin-stat-title">Users</div>
                <div class="admin-stat-value">{users}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="admin-stat-card">
                <div class="admin-stat-title">Tickets</div>
                <div class="admin-stat-value">{tickets}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="admin-stat-card">
                <div class="admin-stat-title">Redeem Codes</div>
                <div class="admin-stat-value">{codes}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_users():
    require_admin(1)

    st.markdown(
        '<div class="admin-section-title">👥 User Database</div>',
        unsafe_allow_html=True,
    )

    rows = query("""
        SELECT
            id,
            username,
            email,
            plan,
            tokens,
            role,
            admin_level,
            is_banned,
            created_at,
            last_login
        FROM users
        ORDER BY id DESC
    """)

    data = []

    for r in rows:
        item = dict(r)

        item["status"] = (
            "🟢 Active"
            if int(item.get("is_banned") or 0) == 0
            else "🔴 Banned"
        )

        item["admin_name"] = ROLE_NAMES.get(
            int(item.get("admin_level") or 0),
            "User",
        )

        item.pop("is_banned", None)

        data.append(item)

    if data:
        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Noch keine User in dieser Datenbank gefunden.")


def render_tickets():
    require_admin(1)

    rows = query("""
        SELECT *
        FROM support_tickets
        ORDER BY id DESC
    """)

    st.markdown(
        '<div class="admin-section-title">🎫 Support Tickets</div>',
        unsafe_allow_html=True,
    )

    if not rows:
        st.info("Keine Tickets vorhanden.")
        return

    for row in rows:
        with st.expander(
            f"#{row['id']} • {row['subject']} • {row['status']}"
        ):
            st.write(f"User: {row['username']}")
            st.write(f"Email: {row['email']}")
            st.write(f"Message: {row['message']}")

            if st.button(
                f"Close Ticket {row['id']}",
                key=f"close_{row['id']}"
            ):
                execute(
                    """
                    UPDATE support_tickets
                    SET status='closed'
                    WHERE id=?
                    """,
                    (row["id"],),
                )

                st.success("Ticket geschlossen.")
                st.rerun()


def render_codes():
    require_admin(2)

    st.markdown(
        '<div class="admin-section-title">🎁 Redeem Codes</div>',
        unsafe_allow_html=True,
    )

    code_type = st.selectbox(
        "Typ",
        ["tokens", "plan"],
    )

    tokens = st.number_input(
        "Tokens",
        0,
        999999,
        1000,
    )

    plan = st.selectbox(
        "Plan",
        ["free", "basic", "pro", "elite"],
    )

    uses = st.number_input(
        "Max Uses",
        1,
        999,
        1,
    )

    if st.button("Code erstellen"):
        code = secrets.token_hex(4).upper()

        execute("""
            INSERT INTO redeem_codes (
                code,
                code_type,
                plan,
                tokens,
                max_uses,
                used_count,
                created_by,
                expires_at,
                is_active,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, 0, ?, '', 1, ?)
        """, (
            code,
            code_type,
            plan,
            tokens,
            uses,
            st.session_state.get("user"),
            datetime.utcnow().isoformat(),
        ))

        st.success(f"Code erstellt: {code}")

    rows = query("""
        SELECT *
        FROM redeem_codes
        ORDER BY id DESC
    """)

    if rows:
        st.dataframe(
            pd.DataFrame([dict(r) for r in rows]),
            use_container_width=True,
            hide_index=True,
        )


def render_logs():
    require_admin(2)

    rows = query("""
        SELECT *
        FROM usage_logs
        ORDER BY id DESC
        LIMIT 100
    """)

    st.markdown(
        '<div class="admin-section-title">📜 Logs</div>',
        unsafe_allow_html=True,
    )

    if rows:
        st.dataframe(
            pd.DataFrame([dict(r) for r in rows]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Keine Logs gefunden.")


def render_payments():
    require_admin(2)

    st.markdown(
        '<div class="admin-section-title">💳 Payments</div>',
        unsafe_allow_html=True,
    )

    rows = query("""
        SELECT *
        FROM payments
        ORDER BY id DESC
    """)

    if rows:
        st.dataframe(
            pd.DataFrame([dict(r) for r in rows]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Keine Zahlungen gefunden.")


def render_admin_actions():
    require_admin(3)

    st.markdown(
        '<div class="admin-section-title">🛡️ Admin Actions</div>',
        unsafe_allow_html=True,
    )

    users = query("""
        SELECT username
        FROM users
        ORDER BY username ASC
    """)

    usernames = [u["username"] for u in users]

    selected = st.selectbox(
        "User auswählen",
        usernames,
    )

    role = st.selectbox(
        "Neuer Rang",
        [
            "Supporter - Level 1",
            "Moderator - Level 2",
            "Admin - Level 3",
            "Owner - Level 1337",
        ],
    )

    if st.button("Rang setzen"):

        if "Supporter" in role:
            lvl = 1
            role_name = "supporter"

        elif "Moderator" in role:
            lvl = 2
            role_name = "moderator"

        elif "Admin" in role:
            lvl = 3
            role_name = "admin"

        else:
            lvl = 1337
            role_name = "owner"

        execute("""
            UPDATE users
            SET role=?, admin_level=?
            WHERE username=?
        """, (
            role_name,
            lvl,
            selected,
        ))

        st.success("Rang aktualisiert.")
        st.rerun()


def render_admin_panel():
    require_admin(1)

    st.markdown(
        """
        <div class="admin-hero">
            🛡️ Admin Panel
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="admin-sub">
            MaByte Control Center — Users, Tickets, Tokens, Logs und Payments.
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs([
        "Overview",
        "Users",
        "Tickets",
        "Redeem Codes",
        "Logs",
        "Payments",
        "Admin Actions",
    ])

    with tabs[0]:
        render_overview()

    with tabs[1]:
        render_users()

    with tabs[2]:
        render_tickets()

    with tabs[3]:
        render_codes()

    with tabs[4]:
        render_logs()

    with tabs[5]:
        render_payments()

    if get_level() >= 3:
        with tabs[6]:
            render_admin_actions()

def render_admin():
    admin_page()