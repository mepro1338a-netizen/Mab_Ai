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


def get_level():
    return int(st.session_state.get("admin_level", 0))


def require_admin(min_level=1):
    if get_level() < min_level:
        st.error("Kein Zugriff.")
        st.stop()


def db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def query(sql, params=()):
    conn = db()
    conn.row_factory = sqlite3.Row
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


def ensure_admin_columns():
    cols = query("PRAGMA table_info(users)")
    names = [c["name"] for c in cols]

    add_cols = {
        "last_login": "TEXT",
        "last_ip": "TEXT",
        "country": "TEXT",
        "city": "TEXT",
        "instagram_name": "TEXT",
        "tiktok_name": "TEXT",
        "status": "TEXT DEFAULT 'active'",
    }

    for col, typ in add_cols.items():
        if col not in names:
            execute(f"ALTER TABLE users ADD COLUMN {col} {typ}")


def make_code(length=12):
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def render_stat(label, value):
    st.markdown(
        f"""
        <div class="admin-stat">
            <div class="admin-stat-label">{label}</div>
            <div class="admin-stat-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_admin_css():
    st.markdown(
        """
        <style>
        .admin-title {
            font-size: 52px;
            font-weight: 1000;
            color: white;
            margin-bottom: 10px;
        }

        .admin-sub {
            color: #bfdbfe;
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 30px;
        }

        .admin-card {
            background: linear-gradient(145deg, rgba(7,18,42,.98), rgba(12,38,78,.92));
            border: 1px solid rgba(96,165,250,.28);
            border-radius: 28px;
            padding: 28px;
            margin-bottom: 24px;
            box-shadow: 0 0 38px rgba(56,189,248,.16);
        }

        .admin-stat {
            background: linear-gradient(145deg, rgba(8,20,45,.98), rgba(13,45,90,.9));
            border: 1px solid rgba(125,211,252,.28);
            border-radius: 24px;
            padding: 22px;
            box-shadow: 0 0 26px rgba(56,189,248,.14);
        }

        .admin-stat-label {
            color: #93c5fd;
            font-size: 14px;
            font-weight: 800;
        }

        .admin-stat-value {
            color: white;
            font-size: 32px;
            font-weight: 1000;
            margin-top: 6px;
        }

        .perm-box {
            background: rgba(15,23,42,.85);
            border: 1px solid rgba(96,165,250,.25);
            border-radius: 20px;
            padding: 18px;
            color: #dbeafe;
            font-weight: 700;
            line-height: 1.8;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_overview():
    users = query("SELECT COUNT(*) as c FROM users")[0]["c"]

    try:
        tickets = query("SELECT COUNT(*) as c FROM support_tickets")[0]["c"]
    except Exception:
        tickets = 0

    try:
        codes = query("SELECT COUNT(*) as c FROM redeem_codes")[0]["c"]
    except Exception:
        codes = 0

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
        <div class="perm-box">
            Dein Rang: <b>{ROLE_NAMES.get(get_level(), "User")}</b><br>
            Admin Level: <b>{get_level()}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_users():
    require_admin(1)
    ensure_admin_columns()

    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.subheader("👥 User Database")

    rows = query(
        """
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
        """
    )

    data = [dict(r) for r in rows]

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


def render_tickets():
    require_admin(1)

    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.subheader("🎫 Support Tickets")

    try:
        tickets = query(
            """
            SELECT *
            FROM support_tickets
            ORDER BY id DESC
            """
        )
    except Exception:
        st.warning("Support-Ticket Tabelle nicht gefunden.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    for t in tickets:
        with st.expander(f"#{t['id']} — {t.get('subject', 'Ticket')} — {t.get('status', 'open')}"):
            st.write(dict(t))

            answer = st.text_area(
                "Antwort",
                key=f"ticket_answer_{t['id']}",
                placeholder="Antwort an User schreiben...",
            )

            c1, c2 = st.columns(2)

            with c1:
                if st.button("Antwort speichern", key=f"answer_{t['id']}"):
                    try:
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
                    except Exception as e:
                        st.error(e)

            with c2:
                if st.button("Ticket schließen", key=f"close_{t['id']}"):
                    try:
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
                    except Exception as e:
                        st.error(e)

    st.markdown("</div>", unsafe_allow_html=True)


def render_redeem_codes():
    require_admin(2)

    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.subheader("🎁 Redeem Codes erstellen")

    col1, col2, col3 = st.columns(3)

    with col1:
        tokens = st.number_input("Tokens", min_value=1, value=100, step=50)

    with col2:
        plan = st.selectbox("Plan", ["free", "pro", "elite", "admin"])

    with col3:
        amount = st.number_input("Anzahl Codes", min_value=1, max_value=100, value=1)

    note = st.text_input("Notiz", placeholder="z.B. Promo, Giveaway, Admin Grant")

    if st.button("Codes erstellen"):
        created = []

        for _ in range(amount):
            code = make_code()

            try:
                execute(
                    """
                    INSERT INTO redeem_codes
                    (code, tokens, plan, used, note, created_at)
                    VALUES (?, ?, ?, 0, ?, ?)
                    """,
                    (code, tokens, plan, note, datetime.now().isoformat()),
                )
                created.append(code)
            except Exception as e:
                st.error(e)

        if created:
            st.success("Codes erstellt:")
            st.code("\n".join(created))

    st.markdown("---")
    st.subheader("Bestehende Codes")

    try:
        codes = query("SELECT * FROM redeem_codes ORDER BY id DESC")
        st.dataframe([dict(c) for c in codes], use_container_width=True, hide_index=True)
    except Exception:
        st.warning("Redeem-Code Tabelle nicht gefunden.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_logs():
    require_admin(2)

    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.subheader("📜 Logs")

    try:
        rows = query("SELECT * FROM logs ORDER BY id DESC LIMIT 300")
        st.dataframe([dict(r) for r in rows], use_container_width=True, hide_index=True)
    except Exception:
        st.warning("Logs Tabelle nicht gefunden.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_payments():
    require_admin(2)

    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.subheader("💳 Payments")

    try:
        rows = query("SELECT * FROM payments ORDER BY id DESC LIMIT 300")
        st.dataframe([dict(r) for r in rows], use_container_width=True, hide_index=True)
    except Exception:
        st.warning("Payments Tabelle nicht gefunden.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_admin_actions():
    require_admin(3)

    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.subheader("🛡️ Admin Actions")

    users = query("SELECT id, username, email, role, admin_level FROM users ORDER BY username ASC")

    options = {
        f"{u['username']} | {u['email']} | Level {u['admin_level']}": u["id"]
        for u in users
    }

    selected = st.selectbox("User auswählen", list(options.keys()))

    new_level = st.selectbox(
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

    new_role = new_level[0].lower()

    if st.button("Rang setzen"):
        execute(
            """
            UPDATE users
            SET admin_level = ?, role = ?
            WHERE id = ?
            """,
            (new_level[1], new_role, options[selected]),
        )
        st.success("Rang aktualisiert.")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_admin():
    require_admin(1)
    render_admin_css()

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

    if level >= 3:
        tabs += ["Admin Actions"]

    selected_tabs = st.tabs(tabs)

    idx = 0

    with selected_tabs[idx]:
        render_overview()
    idx += 1

    with selected_tabs[idx]:
        render_users()
    idx += 1

    with selected_tabs[idx]:
        render_tickets()
    idx += 1

    if level >= 2:
        with selected_tabs[idx]:
            render_redeem_codes()
        idx += 1

        with selected_tabs[idx]:
            render_logs()
        idx += 1

        with selected_tabs[idx]:
            render_payments()
        idx += 1

    if level >= 3:
        with selected_tabs[idx]:
            render_admin_actions()