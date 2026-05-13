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
    list_audit_logs,
    set_role,
    set_plan,
    update_tokens,
    ban_user,
    add_audit_log,
    get_user,
)

try:
    from database import list_login_logs
except Exception:
    list_login_logs = None


ROLE_NAMES = {
    0: "User",
    1: "Supporter",
    2: "Moderator",
    3: "Admin",
    1337: "Owner",
}


def get_level():
    return int(st.session_state.get("admin_level", 0) or 0)


def current_user():
    return st.session_state.get("user", "system")


def require_admin(level=1):
    if get_level() < level:
        st.error("Kein Zugriff.")
        st.stop()


def is_owner():
    return get_level() == 1337 or st.session_state.get("role") == "owner"


def role_label(level):
    return ROLE_NAMES.get(int(level or 0), "User")


def metric_card(label, value):
    with st.container(border=True):
        st.metric(label, value)


def safe_df(rows):
    if not rows:
        st.info("Keine Daten vorhanden.")
        return

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )


def render_overview():
    users = list_users()
    tickets = list_support_messages()
    codes = list_codes()
    logs = list_usage()
    payments = list_purchases()

    total_tokens = sum(int(u.get("tokens") or 0) for u in users)
    banned = len([u for u in users if int(u.get("is_banned") or 0) == 1])
    open_tickets = len([t for t in tickets if t.get("status") == "open"])

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Users", len(users))

    with c2:
        metric_card("Total Tokens", total_tokens)

    with c3:
        metric_card("Open Tickets", open_tickets)

    with c4:
        metric_card("Banned", banned)

    c5, c6, c7, c8 = st.columns(4)

    with c5:
        metric_card("Usage Logs", len(logs))

    with c6:
        metric_card("Payments", len(payments))

    with c7:
        metric_card("Redeem Codes", len(codes))

    with c8:
        metric_card("Dein Rang", role_label(get_level()))


def render_users():
    require_admin(1)

    st.subheader("👥 User Intelligence")

    users = list_users()

    rows = []

    for u in users:
        rows.append({
            "ID": u.get("id"),
            "Username": u.get("username"),
            "Email": u.get("email"),
            "Plan": u.get("plan"),
            "Tokens": u.get("tokens"),
            "Role": u.get("role"),
            "Admin Level": u.get("admin_level"),
            "Rank": role_label(u.get("admin_level")),
            "Status": "Banned" if int(u.get("is_banned") or 0) == 1 else "Active",
            "Created": u.get("created_at"),
            "Last Login": u.get("last_login"),
        })

    safe_df(rows)


def render_user_control():
    require_admin(3)

    st.subheader("🛠️ User Control Center")

    users = list_users()
    usernames = [u.get("username") for u in users if u.get("username")]

    if not usernames:
        st.info("Keine User vorhanden.")
        return

    selected = st.selectbox("User auswählen", usernames)

    user = get_user(selected)

    if not user:
        st.error("User nicht gefunden.")
        return

    with st.container(border=True):
        st.markdown(f"### 👤 {user.get('username')}")
        st.write(f"Email: {user.get('email')}")
        st.write(f"Plan: {user.get('plan')}")
        st.write(f"Tokens: {user.get('tokens')}")
        st.write(f"Role: {user.get('role')} / Level {user.get('admin_level')}")
        st.write(f"Status: {'Banned' if int(user.get('is_banned') or 0) else 'Active'}")
        st.write(f"Created: {user.get('created_at')}")
        st.write(f"Last Login: {user.get('last_login')}")

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Plan ändern")
        new_plan = st.selectbox(
            "Neuer Plan",
            ["free", "pro", "grand", "elite"],
            index=["free", "pro", "grand", "elite"].index(user.get("plan", "free")),
        )

        if st.button("💎 Plan setzen", use_container_width=True):
            set_plan(selected, new_plan)
            add_audit_log(current_user(), "plan_changed", selected, new_plan)
            st.success("Plan aktualisiert.")
            st.rerun()

    with c2:
        st.subheader("Tokens setzen")
        new_tokens = st.number_input(
            "Tokens",
            min_value=0,
            max_value=999999999,
            value=int(user.get("tokens") or 0),
        )

        if st.button("🪙 Tokens setzen", use_container_width=True):
            update_tokens(selected, int(new_tokens))
            add_audit_log(current_user(), "tokens_updated", selected, str(new_tokens))
            st.success("Tokens aktualisiert.")
            st.rerun()

    st.divider()

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Rolle setzen")

        if is_owner():
            roles = [
                ("User", "user", 0),
                ("Supporter", "supporter", 1),
                ("Moderator", "moderator", 2),
                ("Admin", "admin", 3),
                ("Owner", "owner", 1337),
            ]
        else:
            roles = [
                ("User", "user", 0),
                ("Supporter", "supporter", 1),
                ("Moderator", "moderator", 2),
            ]

        role = st.selectbox(
            "Neue Rolle",
            roles,
            format_func=lambda x: f"{x[0]} — Level {x[2]}",
        )

        if st.button("🛡️ Rolle setzen", use_container_width=True):
            set_role(selected, role[1], role[2])
            add_audit_log(current_user(), "role_changed", selected, f"{role[1]} / {role[2]}")
            st.success("Rolle aktualisiert.")
            st.rerun()

    with c4:
        st.subheader("Ban Control")

        if st.button("🔴 User bannen", use_container_width=True):
            ban_user(selected, True)
            add_audit_log(current_user(), "user_banned", selected, "")
            st.success("User gebannt.")
            st.rerun()

        if st.button("🟢 User entbannen", use_container_width=True):
            ban_user(selected, False)
            add_audit_log(current_user(), "user_unbanned", selected, "")
            st.success("User entbannt.")
            st.rerun()


def render_login_logs():
    require_admin(3)

    st.subheader("🌐 Login & IP Intelligence")

    if list_login_logs is None:
        st.warning("Login-Logs sind noch nicht in database.py aktiviert.")
        return

    logs = list_login_logs(limit=300)

    safe_df(logs)


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

    st.subheader("🎁 Redeem Code Factory")

    c1, c2, c3 = st.columns(3)

    with c1:
        code_type = st.selectbox("Code Typ", ["tokens", "plan", "combo"])

    with c2:
        tokens = st.number_input("Tokens", min_value=0, max_value=9999999, value=1000)

    with c3:
        max_uses = st.number_input("Max Uses", min_value=1, max_value=9999, value=1)

    c4, c5 = st.columns(2)

    with c4:
        plan = st.selectbox("Plan", ["", "free", "pro", "grand", "elite"])

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

    st.divider()

    safe_df(list_codes())


def render_usage():
    require_admin(2)

    st.subheader("📜 Usage Intelligence")
    safe_df(list_usage())


def render_payments():
    require_admin(2)

    st.subheader("💳 Payments")
    safe_df(list_purchases())


def render_audit():
    require_admin(3)

    st.subheader("🧾 Audit Logs")
    safe_df(list_audit_logs())


def render_owner_console():
    require_admin(1337)

    st.subheader("👑 Owner Console")

    with st.container(border=True):
        st.write("Owner Mode aktiv.")
        st.write("Voller Zugriff auf User, Logs, Payments, IPs, Rollen, Bans und Codes.")
        st.warning("Alle Aktionen werden im Audit Log gespeichert.")


def render_admin_panel():
    require_admin(1)

    st.title("🛡️ Owner Command Center")
    st.caption("Users, IPs, Logins, Tokens, Plans, Payments, Tickets und System Logs.")

    tabs = [
        "Overview",
        "Users",
        "User Control",
        "Tickets",
    ]

    if get_level() >= 2:
        tabs += ["Redeem Codes", "Usage", "Payments"]

    if get_level() >= 3:
        tabs += ["Login Logs", "Audit"]

    if is_owner():
        tabs += ["Owner Console"]

    tab_objects = st.tabs(tabs)

    i = 0

    with tab_objects[i]:
        render_overview()
    i += 1

    with tab_objects[i]:
        render_users()
    i += 1

    with tab_objects[i]:
        render_user_control()
    i += 1

    with tab_objects[i]:
        render_tickets()
    i += 1

    if get_level() >= 2:
        with tab_objects[i]:
            render_codes()
        i += 1

        with tab_objects[i]:
            render_usage()
        i += 1

        with tab_objects[i]:
            render_payments()
        i += 1

    if get_level() >= 3:
        with tab_objects[i]:
            render_login_logs()
        i += 1

        with tab_objects[i]:
            render_audit()
        i += 1

    if is_owner():
        with tab_objects[i]:
            render_owner_console()


def render_admin():
    render_admin_panel()