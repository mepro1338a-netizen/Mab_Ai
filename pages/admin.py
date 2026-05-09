import streamlit as st

from ai_service import ai_health_check

from database import (
    list_users,
    set_plan,
    update_tokens,
    set_role,
    ban_user,
    delete_user,
    list_support_messages,
    support_counts,
    set_support_status,
    delete_support_message,
    create_redeem_code,
    list_codes,
    list_usage,
    list_audit_logs,
    list_purchases,
    add_audit_log,
)

from ui_helpers import require_login, is_admin, is_owner


def render_admin():
    require_login()

    if not is_admin():
        st.error("Kein Zugriff.")
        st.stop()

    st.title("🛡️ Admin Panel")

    counts = support_counts()
    health = ai_health_check()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Tickets Gesamt", counts.get("total", 0))
    col2.metric("Offen", counts.get("open", 0))
    col3.metric("Geschlossen", counts.get("closed", 0))
    col4.metric("Admin Level", st.session_state.admin_level)

    tab_tickets, tab_users, tab_codes, tab_logs, tab_payments, tab_system = st.tabs(
        ["Tickets", "Users", "Redeem Codes", "Logs", "Payments", "System"]
    )

    with tab_tickets:
        render_admin_tickets()

    with tab_users:
        render_admin_users()

    with tab_codes:
        render_admin_codes()

    with tab_logs:
        render_admin_logs()

    with tab_payments:
        render_admin_payments()

    with tab_system:
        render_admin_system(health)


def render_admin_tickets():
    status_filter = st.selectbox(
        "Status Filter",
        ["all", "open", "closed"],
        key="admin_ticket_filter",
    )

    tickets = list_support_messages(status_filter)

    if not tickets:
        st.info("Keine Tickets vorhanden.")
        return

    for ticket in tickets:
        with st.expander(f"#{ticket['id']} · {ticket.get('subject')} · {ticket.get('status')}"):
            st.write(f"User: {ticket.get('username')}")
            st.write(f"Email: {ticket.get('email')}")
            st.write(f"Kategorie: {ticket.get('category')}")
            st.write(f"Nachricht: {ticket.get('message')}")
            st.write(f"Erstellt: {ticket.get('created_at')}")

            col1, col2 = st.columns(2)

            if col1.button("Als geschlossen markieren", key=f"close_ticket_{ticket['id']}"):
                set_support_status(ticket["id"], "closed")
                add_audit_log(
                    st.session_state.user,
                    "close_ticket",
                    str(ticket["id"]),
                )
                st.rerun()

            if col2.button("Ticket löschen", key=f"delete_ticket_{ticket['id']}"):
                delete_support_message(ticket["id"])
                add_audit_log(
                    st.session_state.user,
                    "delete_ticket",
                    str(ticket["id"]),
                )
                st.rerun()


def render_admin_users():
    users = list_users()
    st.dataframe(users, use_container_width=True)

    st.markdown("### User bearbeiten")

    target_user = st.text_input("Username", key="admin_target_user")
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

    if is_owner():
        new_role = st.selectbox(
            "Role",
            ["user", "supporter", "moderator", "admin", "owner"],
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

    col1, col2, col3, col4 = st.columns(4)

    if col1.button("Plan setzen", key="admin_set_plan"):
        if not target_user:
            st.error("Bitte Username eingeben.")
        else:
            set_plan(target_user, new_plan)
            add_audit_log(
                st.session_state.user,
                "set_plan",
                target_user,
                new_plan,
            )
            st.success("Plan geändert.")

    if col2.button("Tokens setzen", key="admin_set_tokens"):
        if not target_user:
            st.error("Bitte Username eingeben.")
        else:
            update_tokens(target_user, new_tokens)
            add_audit_log(
                st.session_state.user,
                "set_tokens",
                target_user,
                str(new_tokens),
            )
            st.success("Tokens geändert.")

    if col3.button("User bannen", key="admin_ban_user"):
        if not target_user:
            st.error("Bitte Username eingeben.")
        else:
            ban_user(target_user, True)
            add_audit_log(
                st.session_state.user,
                "ban_user",
                target_user,
            )
            st.success("User gebannt.")

    if col4.button("User löschen", key="admin_delete_user"):
        if not target_user:
            st.error("Bitte Username eingeben.")
        else:
            delete_user(target_user)
            add_audit_log(
                st.session_state.user,
                "delete_user",
                target_user,
            )
            st.success("User gelöscht.")

    if is_owner():
        if st.button("Role / Admin Level setzen", key="admin_set_role"):
            if not target_user:
                st.error("Bitte Username eingeben.")
            else:
                set_role(target_user, new_role, new_level)
                add_audit_log(
                    st.session_state.user,
                    "set_role",
                    target_user,
                    f"{new_role}:{new_level}",
                )
                st.success("Role geändert.")


def render_admin_codes():
    if not is_owner():
        st.info("Nur Owner/Admin Level 999 kann Codes erstellen.")
    else:
        with st.form("create_code_form"):
            code_type = st.selectbox("Typ", ["tokens", "plan", "mixed"])
            plan = st.selectbox("Plan", ["free", "pro", "grand", "elite"])
            tokens = st.number_input("Tokens", min_value=0, value=100, step=100)
            max_uses = st.number_input("Max Uses", min_value=1, value=1)
            days_valid = st.number_input("Gültig Tage", min_value=1, value=30)

            submit = st.form_submit_button("Code erstellen")

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
            add_audit_log(
                st.session_state.user,
                "create_redeem_code",
                code,
            )
            st.success(f"Code erstellt: {code}")

    codes = list_codes()

    if codes:
        st.dataframe(codes, use_container_width=True)
    else:
        st.info("Keine Codes vorhanden.")


def render_admin_logs():
    st.markdown("### Usage Logs")
    usage = list_usage()

    if usage:
        st.dataframe(usage, use_container_width=True)
    else:
        st.info("Keine Usage Logs vorhanden.")

    st.markdown("### Audit Logs")
    audit_logs = list_audit_logs()

    if audit_logs:
        st.dataframe(audit_logs, use_container_width=True)
    else:
        st.info("Keine Audit Logs vorhanden.")


def render_admin_payments():
    purchases = list_purchases()

    if purchases:
        st.dataframe(purchases, use_container_width=True)
    else:
        st.info("Keine Payments vorhanden.")


def render_admin_system(health):
    st.markdown("### AI Health Check")
    st.json(health)

    st.markdown("### Session")
    st.json(
        {
            "user": st.session_state.get("user"),
            "plan": st.session_state.get("plan"),
            "role": st.session_state.get("role"),
            "admin_level": st.session_state.get("admin_level"),
        }
    )