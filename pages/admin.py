import secrets
from datetime import datetime

import pandas as pd
import streamlit as st

from database import (
    list_users,
    list_support_messages,
    set_support_status,
    delete_support_message,
    create_redeem_code,
    list_codes,
    list_usage,
    list_purchases,
    set_role,
    ban_user,
    add_audit_log,
)


ROLE_NAMES = {
    0: "User",
    1: "Supporter",
    2: "Moderator",
    3: "Admin",
    1337: "Owner",
}


def get_level():
    return int(st.session_state.get("admin_level", 0))


def current_user():
    return st.session_state.get("user", "system")


def require_admin(level=1):
    if get_level() < level:
        st.error("Kein Zugriff.")
        st.stop()


def can_manage_admins():
    return get_level() == 1337


def can_manage_staff():
    return get_level() in [3, 1337]


def role_label(level):
    return ROLE_NAMES.get(int(level or 0), "User")


def render_stat(title, value):
    st.markdown(
        f"""
        <div class="admin-stat-card">
            <div class="admin-stat-title">{title}</div>
            <div class="admin-stat-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview():
    users = list_users()
    tickets = list_support_messages()
    codes = list_codes()
    logs = list_usage()
    payments = list_purchases()

    c1, c2, c3 = st.columns(3)
    with c1:
        render_stat("Users", len(users))
    with c2:
        render_stat("Tickets", len(tickets))
    with c3:
        render_stat("Redeem Codes", len(codes))

    c4, c5, c6 = st.columns(3)
    with c4:
        render_stat("Logs", len(logs))
    with c5:
        render_stat("Payments", len(payments))
    with c6:
        render_stat("Dein Rang", role_label(get_level()))


def render_users():
    require_admin(1)

    st.subheader("👥 User Database")

    users = list_users()

    if not users:
        st.info("Noch keine User gefunden.")
        return

    data = []

    for u in users:
        data.append({
            "ID": u.get("id"),
            "Username": u.get("username"),
            "Email": u.get("email"),
            "Plan": u.get("plan"),
            "Tokens": u.get("tokens"),
            "Role": u.get("role"),
            "Admin Level": u.get("admin_level"),
            "Rang": role_label(u.get("admin_level")),
            "Status": "🔴 Banned" if int(u.get("is_banned") or 0) == 1 else "🟢 Active",
            "Created": u.get("created_at"),
            "Last Login": u.get("last_login"),
        })

    st.dataframe(
        pd.DataFrame(data),
        use_container_width=True,
        hide_index=True,
    )


def render_tickets():
    require_admin(1)

    st.subheader("🎫 Support Tickets")

    tickets = list_support_messages()

    if not tickets:
        st.info("Keine Tickets vorhanden.")
        return

    for t in tickets:
        with st.expander(f"#{t.get('id')} • {t.get('subject')} • {t.get('status')}"):
            st.write("User:", t.get("username"))
            st.write("Email:", t.get("email"))
            st.write("Kategorie:", t.get("category"))
            st.write("Priorität:", t.get("priority"))
            st.write("Nachricht:", t.get("message"))
            st.write("Erstellt:", t.get("created_at"))

            c1, c2 = st.columns(2)

            with c1:
                if st.button("✅ Schließen", key=f"close_ticket_{t.get('id')}"):
                    set_support_status(t.get("id"), "closed")
                    add_audit_log(current_user(), "ticket_closed", str(t.get("id")), "")
                    st.success("Ticket geschlossen.")
                    st.rerun()

            with c2:
                if get_level() >= 3:
                    if st.button("🗑️ Löschen", key=f"delete_ticket_{t.get('id')}"):
                        delete_support_message(t.get("id"))
                        add_audit_log(current_user(), "ticket_deleted", str(t.get("id")), "")
                        st.success("Ticket gelöscht.")
                        st.rerun()


def render_codes():
    require_admin(2)

    st.subheader("🎁 Redeem Codes")

    with st.container():
        c1, c2, c3 = st.columns(3)

        with c1:
            code_type = st.selectbox("Code Typ", ["tokens", "plan", "combo"])

        with c2:
            tokens = st.number_input("Tokens", min_value=0, max_value=9999999, value=1000)

        with c3:
            max_uses = st.number_input("Max Uses", min_value=1, max_value=9999, value=1)

        c4, c5 = st.columns(2)

        with c4:
            plan = st.selectbox("Plan", ["", "free", "pro", "elite"])

        with c5:
            days_valid = st.number_input("Gültig Tage", min_value=1, max_value=365, value=30)

        if st.button("🚀 Redeem Code erstellen", use_container_width=True):
            code = create_redeem_code(
                code_type=code_type,
                tokens=int(tokens),
                plan=plan,
                max_uses=int(max_uses),
                created_by=current_user(),
                days_valid=int(days_valid),
            )

            add_audit_log(current_user(), "redeem_created", code, f"{tokens} tokens / {plan}")

            st.success("Code erstellt:")
            st.code(code)

    st.markdown("---")

    codes = list_codes()

    if codes:
        st.dataframe(
            pd.DataFrame(codes),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Noch keine Codes vorhanden.")


def render_logs():
    require_admin(2)

    st.subheader("📜 Usage Logs")

    logs = list_usage()

    if not logs:
        st.info("Keine Logs vorhanden.")
        return

    st.dataframe(
        pd.DataFrame(logs),
        use_container_width=True,
        hide_index=True,
    )


def render_payments():
    require_admin(2)

    st.subheader("💳 Payments")

    payments = list_purchases()

    if not payments:
        st.info("Keine Payments vorhanden.")
        return

    st.dataframe(
        pd.DataFrame(payments),
        use_container_width=True,
        hide_index=True,
    )


def render_admin_actions():
    require_admin(3)

    st.subheader("🛡️ Admin Actions")

    users = list_users()

    if not users:
        st.info("Keine User vorhanden.")
        return

    usernames = [u.get("username") for u in users if u.get("username")]

    selected_user = st.selectbox("User auswählen", usernames)

    selected_data = next((u for u in users if u.get("username") == selected_user), None)

    if selected_data:
        st.info(
            f"Aktuell: {selected_data.get('username')} • "
            f"Role: {selected_data.get('role')} • "
            f"Level: {selected_data.get('admin_level')}"
        )

    st.markdown("### Rang vergeben")

    if can_manage_admins():
        rank_options = [
            ("User", "user", 0),
            ("Supporter", "supporter", 1),
            ("Moderator", "moderator", 2),
            ("Admin", "admin", 3),
            ("Owner", "owner", 1337),
        ]
    else:
        rank_options = [
            ("User", "user", 0),
            ("Supporter", "supporter", 1),
            ("Moderator", "moderator", 2),
        ]

    rank = st.selectbox(
        "Neuer Rang",
        rank_options,
        format_func=lambda x: f"{x[0]} — Level {x[2]}",
    )

    if st.button("✅ Rang setzen", use_container_width=True):
        set_role(selected_user, rank[1], rank[2])
        add_audit_log(
            current_user(),
            "role_changed",
            selected_user,
            f"{rank[1]} / {rank[2]}",
        )
        st.success("Rang aktualisiert.")
        st.rerun()

    st.markdown("---")
    st.markdown("### User sperren / entsperren")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🔴 User bannen", use_container_width=True):
            ban_user(selected_user, True)
            add_audit_log(current_user(), "user_banned", selected_user, "")
            st.success("User gebannt.")
            st.rerun()

    with c2:
        if st.button("🟢 User entbannen", use_container_width=True):
            ban_user(selected_user, False)
            add_audit_log(current_user(), "user_unbanned", selected_user, "")
            st.success("User entbannt.")
            st.rerun()


def render_admin_panel():
    require_admin(1)

    st.markdown(
        """
        <div class="admin-title">🛡️ Admin Panel</div>
        <div class="admin-subtitle">
            MaByte Control Center — Users, Tickets, Tokens, Logs und Payments.
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = ["Overview", "Users", "Tickets"]

    if get_level() >= 2:
        tabs += ["Redeem Codes", "Logs", "Payments"]

    if get_level() in [3, 1337]:
        tabs += ["Admin Actions"]

    tab_objects = st.tabs(tabs)

    idx = 0

    with tab_objects[idx]:
        render_overview()
    idx += 1

    with tab_objects[idx]:
        render_users()
    idx += 1

    with tab_objects[idx]:
        render_tickets()
    idx += 1

    if get_level() >= 2:
        with tab_objects[idx]:
            render_codes()
        idx += 1

        with tab_objects[idx]:
            render_logs()
        idx += 1

        with tab_objects[idx]:
            render_payments()
        idx += 1

    if get_level() in [3, 1337]:
        with tab_objects[idx]:
            render_admin_actions()


def render_admin():
    render_admin_panel()