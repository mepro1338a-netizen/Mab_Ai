import streamlit as st

from ai_service import ai_health_check

from db_manager import execute, fetch_all
from database import (
    list_users,
    set_plan,
    update_tokens,
    set_role,
    ban_user,
    delete_user,
    support_counts,
    create_redeem_code,
    list_codes,
    list_usage,
    list_audit_logs,
    list_purchases,
    add_audit_log,
)

from redeem_tracking import list_redeem_redemptions

from ui_helpers import (
    require_login,
    is_admin,
    is_owner,
)


def init_admin_support_tables():
    execute("""
    CREATE TABLE IF NOT EXISTS support_replies (
        id SERIAL PRIMARY KEY,
        ticket_id INTEGER,
        sender TEXT,
        sender_role TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)


def safe_users():
    try:
        users = list_users()

        clean = []

        for user in users:
            user = dict(user)

            user.pop("password", None)
            user.pop("password_hash", None)

            clean.append(user)

        return clean

    except Exception:
        return fetch_all("""
        SELECT
            id,
            username,
            email,
            plan,
            tokens,
            role,
            admin_level,
            created_at
        FROM users
        ORDER BY id DESC
        """)


def render_admin():
    require_login()

    if not is_admin():
        st.error("Kein Zugriff.")
        st.stop()

    init_admin_support_tables()

    st.markdown("""
    <div class="page-card">
        <span class="badge">ADMIN</span>
        <h1>🛡️ Admin Panel</h1>
        <p>
            Verwalte User, Tickets, Redeem Codes,
            Logs und Systemstatus.
        </p>
    </div>
    """, unsafe_allow_html=True)

    try:
        counts = support_counts()
    except Exception:
        counts = {
            "total": 0,
            "open": 0,
            "closed": 0,
        }

    try:
        health = ai_health_check()
    except Exception as e:
        health = {"error": str(e)}

    users = safe_users()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("User", len(users))
    c2.metric("Tickets Gesamt", counts.get("total", 0))
    c3.metric("Offen", counts.get("open", 0))
    c4.metric("Admin Level", st.session_state.admin_level)

    (
        tab_tickets,
        tab_users,
        tab_codes,
        tab_redeem_logs,
        tab_logs,
        tab_payments,
        tab_system,
    ) = st.tabs([
        "🎫 Tickets",
        "👥 Users",
        "🎁 Redeem Codes",
        "🧾 Redeem Logs",
        "📜 Logs",
        "💳 Payments",
        "⚙️ System",
    ])

    with tab_tickets:
        render_admin_tickets()

    with tab_users:
        render_admin_users()

    with tab_codes:
        render_admin_codes()

    with tab_redeem_logs:
        render_admin_redeem_logs()

    with tab_logs:
        render_admin_logs()

    with tab_payments:
        render_admin_payments()

    with tab_system:
        render_admin_system(health)


def render_admin_tickets():
    st.markdown("## 🎫 Support Tickets")

    status_filter = st.selectbox(
        "Status Filter",
        ["all", "open", "closed"],
        key="admin_ticket_filter",
    )

    if status_filter == "all":
        tickets = fetch_all("""
        SELECT *
        FROM support_tickets
        ORDER BY created_at DESC
        """)
    else:
        tickets = fetch_all("""
        SELECT *
        FROM support_tickets
        WHERE status = %s
        ORDER BY created_at DESC
        """, (status_filter,))

    if not tickets:
        st.info("Keine Tickets vorhanden.")
        return

    for ticket in tickets:
        status = ticket.get("status", "open")
        title = ticket.get("subject", "Ohne Betreff")

        with st.expander(
            f"#{ticket['id']} · {title} · {status}"
        ):
            st.markdown(
                f"""
                <div class="page-card">
                    <b>User:</b> {ticket.get("username")}<br>
                    <b>Email:</b> {ticket.get("email")}<br>
                    <b>Kategorie:</b> {ticket.get("category")}<br>
                    <b>Status:</b> {ticket.get("status")}<br>
                    <b>Erstellt:</b> {ticket.get("created_at")}

                    <hr>

                    <h4>Nachricht</h4>
                    <p>{ticket.get("message")}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            replies = fetch_all("""
            SELECT *
            FROM support_replies
            WHERE ticket_id = %s
            ORDER BY created_at ASC
            """, (ticket["id"],))

            st.markdown("### Verlauf")

            if replies:
                for reply in replies:
                    st.markdown(
                        f"""
                        <div class="page-card">
                            <b>{reply.get("sender")}</b>

                            <span style="color:#ffd700;">
                                ({reply.get("sender_role")})
                            </span><br>

                            <small>
                                {reply.get("created_at")}
                            </small>

                            <p style="margin-top:12px;">
                                {reply.get("message")}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("Noch keine Antworten.")

            reply_text = st.text_area(
                "Antwort schreiben",
                key=f"reply_text_{ticket['id']}",
                height=120,
            )

            col1, col2, col3 = st.columns(3)

            if col1.button(
                "Antwort senden",
                key=f"send_reply_{ticket['id']}"
            ):
                if not reply_text.strip():
                    st.error("Bitte Antwort eingeben.")
                else:
                    execute("""
                    INSERT INTO support_replies (
                        ticket_id,
                        sender,
                        sender_role,
                        message
                    )
                    VALUES (%s, %s, %s, %s)
                    """, (
                        ticket["id"],
                        st.session_state.user,
                        st.session_state.role,
                        reply_text,
                    ))

                    execute("""
                    UPDATE support_tickets
                    SET status = 'open'
                    WHERE id = %s
                    """, (ticket["id"],))

                    add_audit_log(
                        st.session_state.user,
                        "support_reply",
                        str(ticket["id"]),
                        reply_text[:250],
                    )

                    st.success("Antwort gesendet.")
                    st.rerun()

            if col2.button(
                "Ticket schließen",
                key=f"close_ticket_{ticket['id']}"
            ):
                execute("""
                UPDATE support_tickets
                SET status = 'closed'
                WHERE id = %s
                """, (ticket["id"],))

                st.success("Ticket geschlossen.")
                st.rerun()

            if col3.button(
                "Ticket löschen",
                key=f"delete_ticket_{ticket['id']}"
            ):
                execute("""
                DELETE FROM support_replies
                WHERE ticket_id = %s
                """, (ticket["id"],))

                execute("""
                DELETE FROM support_tickets
                WHERE id = %s
                """, (ticket["id"],))

                st.success("Ticket gelöscht.")
                st.rerun()


def render_admin_users():
    st.markdown("## 👥 Users")

    users = safe_users()

    if users:
        st.dataframe(
            users,
            use_container_width=True,
        )
    else:
        st.info("Keine User vorhanden.")

    st.markdown("---")
    st.markdown("### User bearbeiten")

    target_user = st.text_input(
        "Username",
        key="admin_target_user",
    )

    col_a, col_b = st.columns(2)

    with col_a:
        new_plan = st.selectbox(
            "Plan",
            ["free", "pro", "grand", "elite"],
            key="admin_new_plan",
        )

        new_tokens = st.number_input(
            "Tokens setzen",
            min_value=0,
            value=0,
            step=100,
            key="admin_new_tokens",
        )

    with col_b:
        if is_owner():
            new_role = st.selectbox(
                "Role",
                [
                    "user",
                    "supporter",
                    "moderator",
                    "admin",
                    "owner",
                ],
                key="admin_new_role",
            )

            new_level = st.selectbox(
                "Admin Level",
                [0, 1, 2, 3, 999],
                key="admin_new_level",
            )
        else:
            new_role = "user"
            new_level = 0

    c1, c2, c3, c4 = st.columns(4)

    if c1.button("Plan setzen"):
        set_plan(target_user, new_plan)
        st.success("Plan geändert.")
        st.rerun()

    if c2.button("Tokens setzen"):
        update_tokens(target_user, new_tokens)
        st.success("Tokens geändert.")
        st.rerun()

    if c3.button("User bannen"):
        ban_user(target_user, True)
        st.success("User gebannt.")
        st.rerun()

    if c4.button("User löschen"):
        delete_user(target_user)
        st.success("User gelöscht.")
        st.rerun()

    if is_owner():
        if st.button("Role setzen"):
            set_role(
                target_user,
                new_role,
                new_level,
            )

            st.success("Role geändert.")
            st.rerun()


def render_admin_codes():
    st.markdown("## 🎁 Redeem Codes")

    if not is_owner():
        st.info("Nur Owner kann Codes erstellen.")
        return

    with st.form("create_code_form"):
        code_type = st.selectbox(
            "Typ",
            ["tokens", "plan", "mixed"]
        )

        plan = st.selectbox(
            "Plan",
            ["", "free", "pro", "grand", "elite"]
        )

        tokens = st.number_input(
            "Tokens",
            min_value=0,
            value=100,
            step=100,
        )

        max_uses = st.number_input(
            "Max Uses",
            min_value=1,
            value=1,
        )

        days_valid = st.number_input(
            "Gültig Tage",
            min_value=1,
            value=30,
        )

        submit = st.form_submit_button(
            "Code erstellen"
        )

    if submit:
        code = create_redeem_code(
            code_type=code_type,
            value="",
            tokens=tokens,
            plan=plan,
            max_uses=max_uses,
            created_by=st.session_state.user,
            days_valid=days_valid,
        )

        st.success(f"Code erstellt: {code}")

    codes = list_codes()

    if codes:
        st.dataframe(
            codes,
            use_container_width=True,
        )
    else:
        st.info("Keine Codes vorhanden.")


def render_admin_redeem_logs():
    st.markdown("## 🧾 Redeem Logs")

    logs = list_redeem_redemptions()

    if logs:
        st.dataframe(
            logs,
            use_container_width=True,
        )
    else:
        st.info(
            "Noch keine Redeem Einlösungen vorhanden."
        )


def render_admin_logs():
    st.markdown("## 📜 Logs")

    usage = list_usage()

    if usage:
        st.dataframe(
            usage,
            use_container_width=True,
        )
    else:
        st.info("Keine Logs vorhanden.")

    audit_logs = list_audit_logs()

    if audit_logs:
        st.dataframe(
            audit_logs,
            use_container_width=True,
        )
    else:
        st.info("Keine Audit Logs vorhanden.")


def render_admin_payments():
    st.markdown("## 💳 Payments")

    purchases = list_purchases()

    if purchases:
        st.dataframe(
            purchases,
            use_container_width=True,
        )
    else:
        st.info("Keine Payments vorhanden.")


def render_admin_system(health):
    st.markdown("## ⚙️ System")

    st.markdown("### AI Health Check")
    st.json(health)

    st.markdown("### Session")
    st.json({
        "user": st.session_state.get("user"),
        "plan": st.session_state.get("plan"),
        "role": st.session_state.get("role"),
        "admin_level": st.session_state.get("admin_level"),
    })
