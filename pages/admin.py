import os
import sqlite3
import secrets
import string

from datetime import datetime

import streamlit as st


DB_PATH = "mabai.db"


ROLE_NAMES = {
    1: "Supporter",
    2: "Moderator",
    3: "Admin",
    1337: "Owner",
}


# =========================================================
# DATABASE
# =========================================================

def db():
    db_path = os.path.abspath(DB_PATH)

    conn = sqlite3.connect(
        db_path,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


def query(sql, params=()):
    conn = db()
    cur = conn.cursor()

    cur.execute(sql, params)

    rows = cur.fetchall()

    conn.close()

    return rows


def execute(sql, params=()):
    conn = db()
    cur = conn.cursor()

    cur.execute(sql, params)

    conn.commit()
    conn.close()


# =========================================================
# TABLES
# =========================================================

def ensure_tables():
    conn = db()
    cur = conn.cursor()

    # USERS

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT,
        plan TEXT DEFAULT 'free',
        tokens INTEGER DEFAULT 0,
        role TEXT DEFAULT 'user',
        admin_level INTEGER DEFAULT 0,
        created_at TEXT,
        last_login TEXT,
        last_ip TEXT,
        country TEXT,
        city TEXT,
        instagram_name TEXT,
        tiktok_name TEXT,
        status TEXT DEFAULT 'active'
    )
    """)

    # REDEEM CODES

    cur.execute("""
    CREATE TABLE IF NOT EXISTS redeem_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        tokens INTEGER,
        plan TEXT,
        used INTEGER DEFAULT 0,
        note TEXT,
        created_at TEXT
    )
    """)

    # TICKETS

    cur.execute("""
    CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        subject TEXT,
        message TEXT,
        status TEXT DEFAULT 'open',
        admin_answer TEXT,
        answered_at TEXT,
        closed_at TEXT,
        created_at TEXT
    )
    """)

    # LOGS

    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        message TEXT,
        created_at TEXT
    )
    """)

    # PAYMENTS

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        amount TEXT,
        provider TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================================================
# HELPERS
# =========================================================

def get_level():
    return int(
        st.session_state.get("admin_level", 0)
    )


def require_admin(level=1):
    if get_level() < level:
        st.error("Kein Zugriff.")
        st.stop()


def role_name(level):
    return ROLE_NAMES.get(level, "User")


def make_code(length=12):
    chars = string.ascii_uppercase + string.digits

    return "".join(
        secrets.choice(chars)
        for _ in range(length)
    )


# =========================================================
# CSS
# =========================================================

def admin_css():
    st.markdown(
        """
        <style>

        .admin-title{
            font-size:64px;
            font-weight:1000;
            color:white;
            margin-bottom:10px;
        }

        .admin-sub{
            font-size:20px;
            color:#bfdbfe;
            font-weight:700;
            margin-bottom:35px;
        }

        .admin-card{
            background:linear-gradient(
                145deg,
                rgba(7,18,42,.98),
                rgba(12,38,78,.92)
            );

            border:1px solid rgba(96,165,250,.28);

            border-radius:30px;

            padding:28px;

            margin-bottom:25px;

            box-shadow:0 0 40px rgba(56,189,248,.18);
        }

        .admin-stat{
            background:linear-gradient(
                145deg,
                rgba(8,20,45,.98),
                rgba(13,45,90,.92)
            );

            border:1px solid rgba(125,211,252,.25);

            border-radius:24px;

            padding:24px;

            box-shadow:0 0 25px rgba(56,189,248,.15);
        }

        .admin-stat-title{
            color:#93c5fd;
            font-size:14px;
            font-weight:800;
        }

        .admin-stat-value{
            color:white;
            font-size:36px;
            font-weight:1000;
            margin-top:8px;
        }

        .role-box{
            background:rgba(15,23,42,.85);

            border:1px solid rgba(96,165,250,.28);

            border-radius:22px;

            padding:20px;

            color:#dbeafe;

            font-size:18px;

            font-weight:700;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# UI
# =========================================================

def render_stat(title, value):
    st.markdown(
        f"""
        <div class="admin-stat">
            <div class="admin-stat-title">
                {title}
            </div>

            <div class="admin-stat-value">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# OVERVIEW
# =========================================================

def render_overview():

    users = query(
        "SELECT COUNT(*) as c FROM users"
    )[0]["c"]

    tickets = query(
        "SELECT COUNT(*) as c FROM support_tickets"
    )[0]["c"]

    codes = query(
        "SELECT COUNT(*) as c FROM redeem_codes"
    )[0]["c"]

    c1, c2, c3 = st.columns(3)

    with c1:
        render_stat("Users", users)

    with c2:
        render_stat("Tickets", tickets)

    with c3:
        render_stat("Redeem Codes", codes)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="role-box">
            Eingeloggt als:
            <b>{role_name(get_level())}</b>

            <br><br>

            Admin Level:
            <b>{get_level()}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# USERS
# =========================================================

def render_users():
    require_admin(1)

    st.markdown(
        '<div class="admin-card">',
        unsafe_allow_html=True
    )

    st.subheader("👥 User Database")

    rows = query("""
    SELECT
        id,
        username,
        email,
        plan,
        tokens,
        role,
        admin_level,
        status,
        created_at,
        last_login,
        last_ip,
        country,
        city,
        instagram_name,
        tiktok_name
    FROM users
    ORDER BY id DESC
    """)

    data = [dict(r) for r in rows]

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# TICKETS
# =========================================================

def render_tickets():
    require_admin(1)

    st.markdown(
        '<div class="admin-card">',
        unsafe_allow_html=True
    )

    st.subheader("🎫 Support Tickets")

    tickets = query("""
    SELECT *
    FROM support_tickets
    ORDER BY id DESC
    """)

    if not tickets:
        st.info("Keine Tickets vorhanden.")

    for t in tickets:

        with st.expander(
            f"#{t['id']} - {t['subject']}"
        ):

            st.write("User:", t["username"])
            st.write("Message:", t["message"])
            st.write("Status:", t["status"])

            answer = st.text_area(
                "Antwort",
                key=f"answer_{t['id']}"
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "Antwort speichern",
                    key=f"save_{t['id']}"
                ):

                    execute("""
                    UPDATE support_tickets
                    SET admin_answer = ?,
                        answered_at = ?
                    WHERE id = ?
                    """, (
                        answer,
                        datetime.now().isoformat(),
                        t["id"]
                    ))

                    st.success("Antwort gespeichert.")
                    st.rerun()

            with c2:

                if st.button(
                    "Ticket schließen",
                    key=f"close_{t['id']}"
                ):

                    execute("""
                    UPDATE support_tickets
                    SET status = 'closed',
                        closed_at = ?
                    WHERE id = ?
                    """, (
                        datetime.now().isoformat(),
                        t["id"]
                    ))

                    st.success("Ticket geschlossen.")
                    st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# REDEEM
# =========================================================

def render_redeem():
    require_admin(2)

    st.markdown(
        '<div class="admin-card">',
        unsafe_allow_html=True
    )

    st.subheader("🎁 Redeem Codes")

    c1, c2, c3 = st.columns(3)

    with c1:
        tokens = st.number_input(
            "Tokens",
            min_value=1,
            value=100
        )

    with c2:
        plan = st.selectbox(
            "Plan",
            ["free", "pro", "elite"]
        )

    with c3:
        amount = st.number_input(
            "Anzahl",
            min_value=1,
            max_value=100,
            value=1
        )

    note = st.text_input(
        "Notiz"
    )

    if st.button("Codes erstellen"):

        created = []

        for _ in range(amount):

            code = make_code()

            execute("""
            INSERT INTO redeem_codes
            (
                code,
                tokens,
                plan,
                used,
                note,
                created_at
            )
            VALUES (?, ?, ?, 0, ?, ?)
            """, (
                code,
                tokens,
                plan,
                note,
                datetime.now().isoformat()
            ))

            created.append(code)

        st.success("Codes erstellt")

        st.code("\n".join(created))

    st.markdown("---")

    rows = query("""
    SELECT *
    FROM redeem_codes
    ORDER BY id DESC
    """)

    st.dataframe(
        [dict(r) for r in rows],
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# LOGS
# =========================================================

def render_logs():
    require_admin(2)

    st.markdown(
        '<div class="admin-card">',
        unsafe_allow_html=True
    )

    st.subheader("📜 Logs")

    rows = query("""
    SELECT *
    FROM logs
    ORDER BY id DESC
    LIMIT 300
    """)

    st.dataframe(
        [dict(r) for r in rows],
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# PAYMENTS
# =========================================================

def render_payments():
    require_admin(2)

    st.markdown(
        '<div class="admin-card">',
        unsafe_allow_html=True
    )

    st.subheader("💳 Payments")

    rows = query("""
    SELECT *
    FROM payments
    ORDER BY id DESC
    LIMIT 300
    """)

    st.dataframe(
        [dict(r) for r in rows],
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# ADMIN ACTIONS
# =========================================================

def render_admin_actions():
    require_admin(3)

    st.markdown(
        '<div class="admin-card">',
        unsafe_allow_html=True
    )

    st.subheader("🛡️ Admin Actions")

    users = query("""
    SELECT
        id,
        username,
        email,
        admin_level
    FROM users
    ORDER BY username ASC
    """)

    options = {
        f"{u['username']} | {u['email']}": u["id"]
        for u in users
    }

    selected = st.selectbox(
        "User auswählen",
        list(options.keys())
    )

    rank = st.selectbox(
        "Neuer Rang",
        [
            ("User", 0),
            ("Supporter", 1),
            ("Moderator", 2),
            ("Admin", 3),
            ("Owner", 1337),
        ],
        format_func=lambda x:
            f"{x[0]} - Level {x[1]}"
    )

    if st.button("Rang setzen"):

        execute("""
        UPDATE users
        SET
            admin_level = ?,
            role = ?
        WHERE id = ?
        """, (
            rank[1],
            rank[0].lower(),
            options[selected]
        ))

        st.success("Rang aktualisiert.")
        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# MAIN
# =========================================================

def render_admin():

    ensure_tables()

    require_admin(1)

    admin_css()

    st.markdown(
        """
        <div class="admin-title">
            🛡️ Admin Panel
        </div>

        <div class="admin-sub">
            MaByte Control Center —
            Users, Tickets, Tokens,
            Logs und Payments.
        </div>
        """,
        unsafe_allow_html=True,
    )

    level = get_level()

    tabs = [
        "Overview",
        "Users",
        "Tickets"
    ]

    if level >= 2:
        tabs += [
            "Redeem Codes",
            "Logs",
            "Payments"
        ]

    if level >= 3:
        tabs += [
            "Admin Actions"
        ]

    t = st.tabs(tabs)

    idx = 0

    with t[idx]:
        render_overview()
    idx += 1

    with t[idx]:
        render_users()
    idx += 1

    with t[idx]:
        render_tickets()
    idx += 1

    if level >= 2:

        with t[idx]:
            render_redeem()
        idx += 1

        with t[idx]:
            render_logs()
        idx += 1

        with t[idx]:
            render_payments()
        idx += 1

    if level >= 3:

        with t[idx]:
            render_admin_actions()