import os
import sqlite3
import secrets
import string
from datetime import datetime

import streamlit as st


DB_PATH = "mabai.db"

ROLE_NAMES = {
    0: "User",
    1: "Supporter",
    2: "Moderator",
    3: "Admin",
    1337: "Owner",
}


# =========================
# DATABASE
# =========================

def db():
    conn = sqlite3.connect(os.path.abspath(DB_PATH), check_same_thread=False)
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


def table_exists(name):
    rows = query(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    )
    return len(rows) > 0


def ensure_tables():
    conn = db()
    cur = conn.cursor()

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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS redeem_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        tokens INTEGER DEFAULT 0,
        plan TEXT DEFAULT 'free',
        used INTEGER DEFAULT 0,
        used_by TEXT,
        note TEXT,
        created_at TEXT
    )
    """)

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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        message TEXT,
        created_at TEXT
    )
    """)

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


# =========================
# PERMISSIONS
# =========================

def get_level():
    return int(st.session_state.get("admin_level", 0))


def role_name(level=None):
    if level is None:
        level = get_level()
    return ROLE_NAMES.get(int(level), "User")


def require_admin(min_level=1):
    if get_level() < min_level:
        st.error("Kein Zugriff.")
        st.stop()


def can_admin_actions():
    return get_level() in [3, 1337]


# =========================
# HELPERS
# =========================

def make_code(length=12):
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def count_table(table):
    if not table_exists(table):
        return 0
    return query(f"SELECT COUNT(*) AS c FROM {table}")[0]["c"]


# =========================
# CSS
# =========================

def admin_css():
    st.markdown(
        """
<style>
.admin-title {
    font-size: 60px;
    font-weight: 1000;
    color: white;
    margin-bottom: 8px;
}

.admin-sub {
    color: #bfdbfe;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 32px;
}

.admin-card {
    background: linear-gradient(145deg, rgba(7,18,42,.98), rgba(12,38,78,.92));
    border: 1px solid rgba(96,165,250,.28);
    border-radius: 30px;
    padding: 28px;
    margin-bottom: 24px;
    box-shadow: 0 0 38px rgba(56,189,248,.16);
}

.admin-stat {
    background: linear-gradient(145deg, rgba(8,20,45,.98), rgba(13,45,90,.90));
    border: 1px solid rgba(125,211,252,.28);
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 0 26px rgba(56,189,248,.15);
}

.admin-stat-title {
    color: #93c5fd;
    font-size: 15px;
    font-weight: 900;
}

.admin-stat-value {
    color: white;
    font-size: 38px;
    font-weight: 1000;
    margin-top: 8px;
}

.role-box {
    background: rgba(15,23,42,.88);
    border: 1px solid rgba(96,165,250,.30);
    border-radius: 24px;
    padding: 22px;
    color: #dbeafe;
    font-size: 18px;
    font-weight: 750;
    line-height: 1.7;
}

.admin-pill {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(14,165,233,.16);
    border: 1px solid rgba(125,211,252,.35);
    color: #7dd3fc;
    font-weight: 900;
    margin-right: 8px;
}

.admin-section-title {
    font-size: 28px;
    font-weight: 950;
    color: white;
    margin-bottom: 18px;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_stat(title, value):
    st.markdown(
        f"""
        <div class="admin-stat">
            <div class="admin-stat-title">{title}</div>
            <div class="admin-stat-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# PAGES
# =========================

def render_overview():
    users = count_table("users")
    tickets = count_table("support_tickets")
    codes = count_table("redeem_codes")
    logs = count_table("logs")
    payments = count_table("payments")

    c1, c2, c3 = st.columns(3)

    with c1:
        render_stat("Users", users)
    with c2:
        render_stat("Tickets", tickets)
    with c3:
        render_stat("Redeem Codes", codes)

    c4, c5, c6 = st.columns(3)

    with c4:
        render_stat("Logs", logs)
    with c5:
        render_stat("Payments", payments)
    with c6:
        render_stat("Admin Level", get_level())

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="role-box">
            <span class="admin-pill">{role_name()}</span>
            <br><br>
            Supporter: Tickets beantworten und User ansehen.<br>
            Moderator: Tokens/Codes erstellen, Tickets, Logs und Payments ansehen.<br>
            Admin/Owner: alle Rechte inklusive Admin Actions.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_users():
    require_admin(1)

    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown('<div class="admin-section-title">👥 User Database</div>', unsafe_allow_html=True)

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

    if data:
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("Noch keine User in dieser Datenbank gefunden.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_tickets():
    require_admin(1)

    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown('<div class="admin-section-title">🎫 Support Tickets</div>', unsafe_allow_html=True)

    tickets = query("""
        SELECT *
        FROM support_tickets
        ORDER BY id DESC
    """)

    if not tickets:
        st.info("Keine Tickets vorhanden.")

    for t in tickets:
        title = f"#{t['id']} — {t['subject'] or 'Ticket'} — {t['status'] or 'open'}"

        with st.expander(title):
            st.write("User:", t["username"])
            st.write("Nachricht:", t["message"])
            st.write("Status:", t["status"])

            answer = st.text_area("Antwort", key=f"answer_{t['id']}")

            c1, c2 = st.columns(2)

            with c1:
                if st.button("Antwort speichern", key=f"save_ticket_{t['id']}"):
                    execute(
                        """
                        UPDATE support_tickets
                        SET admin_answer = ?, answered_at = ?
                        WHERE id = ?
                        """,
                        (answer, datetime.now().isoformat(), t["id"]),
                    )
                    st.success("Antwort gespeichert.")
                    st.rerun()

            with c2:
                if st.button("Ticket schließen", key=f"close_ticket_{t['id']}"):
                    execute(
                        """
                        UPDATE support_tickets
                        SET status = 'closed', closed_at = ?
                        WHERE id = ?
                        """,
                        (datetime.now().isoformat(), t["id"]),
                    )
                    st.success("Ticket geschlossen.")
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_redeem():
    require_admin(2)

    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown('<div class="admin-section-title">🎁 Redeem Codes</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        tokens = st.number_input("Tokens", min_value=1, value=100, step=50)

    with c2:
        plan = st.selectbox("Plan", ["free", "pro", "elite"])

    with c3:
        amount = st.number_input("Anzahl", min_value=1, max_value=100, value=1)

    note = st.text_input("Notiz", placeholder="Promo, Giveaway, Support-Gutschrift...")

    if st.button("Codes erstellen"):
        created = []

        for _ in range(int(amount)):
            code = make_code()

            execute(
                """
                INSERT INTO redeem_codes
                (code, tokens, plan, used, note, created_at)
                VALUES (?, ?, ?, 0, ?, ?)
                """,
                (code, int(tokens), plan, note, datetime.now().isoformat()),
            )

            created.append(code)

        st.success("Codes erstellt.")
        st.code("\n".join(created))

    st.markdown("---")

    rows = query("""
        SELECT *
        FROM redeem_codes
        ORDER BY id DESC
    """)

    data = [dict(r) for r in rows]

    if data:
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("Noch keine Redeem Codes vorhanden.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_logs():
    require_admin(2)

    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown('<div class="admin-section-title">📜 Logs</div>', unsafe_allow_html=True)

    rows = query("""
        SELECT *
        FROM logs
        ORDER BY id DESC
        LIMIT 300
    """)

    data = [dict(r) for r in rows]

    if data:
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("Noch keine Logs vorhanden.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_payments():
    require_admin(2)

    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown('<div class="admin-section-title">💳 Payments</div>', unsafe_allow_html=True)

    rows = query("""
        SELECT *
        FROM payments
        ORDER BY id DESC
        LIMIT 300
    """)

    data = [dict(r) for r in rows]

    if data:
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("Noch keine Payments vorhanden.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_admin_actions():
    require_admin(3)

    if not can_admin_actions():
        st.error("Nur Admin und Owner dürfen Admin Actions benutzen.")
        st.stop()

    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.markdown('<div class="admin-section-title">🛡️ Admin Actions</div>', unsafe_allow_html=True)

    users = query("""
        SELECT id, username, email, role, admin_level
        FROM users
        ORDER BY username ASC
    """)

    if not users:
        st.info("Keine User vorhanden.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    options = {
        f"{u['username']} | {u['email']} | Level {u['admin_level']}": u["id"]
        for u in users
    }

    selected = st.selectbox("User auswählen", list(options.keys()))

    rank = st.selectbox(
        "Neuer Rang",
        [
            ("User", 0),
            ("Supporter", 1),
            ("Moderator", 2),
            ("Admin", 3),
            ("Owner", 1337),
        ],
        format_func=lambda x: f"{x[0]} — Level {x[1]}",
    )

    if st.button("Rang setzen"):
        execute(
            """
            UPDATE users
            SET admin_level = ?, role = ?
            WHERE id = ?
            """,
            (rank[1], rank[0].lower(), options[selected]),
        )
        st.success("Rang aktualisiert.")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# MAIN
# =========================

def render_admin():
    ensure_tables()
    require_admin(1)
    admin_css()

    st.markdown(
        """
        <div class="admin-title">🛡️ Admin Panel</div>
        <div class="admin-sub">
            MaByte Control Center — Users, Tickets, Tokens, Logs und Payments.
        </div>
        """,
        unsafe_allow_html=True,
    )

    level = get_level()

    tabs = ["Overview", "Users", "Tickets"]

    if level >= 2:
        tabs += ["Redeem Codes", "Logs", "Payments"]

    if level in [3, 1337]:
        tabs += ["Admin Actions"]

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

    if level in [3, 1337]:
        with t[idx]:
            render_admin_actions()