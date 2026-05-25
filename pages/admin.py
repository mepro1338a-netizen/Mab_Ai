import sqlite3
import pandas as pd
import streamlit as st

from config import DB_PATH, PLANS
from ui.styles import inject_css, page_layout_css, gradient_title_css
from database import (
    OWNER_USERNAME,
    ROLE_LEVELS,
    get_user,
    list_users,
    secure_update_tokens,
    secure_set_plan,
    secure_set_role,
    secure_ban_user,
    secure_delete_user,
    set_role,
    create_redeem_code,
    list_codes,
    list_usage,
    list_purchases,
    list_support_messages,
    set_support_status,
    delete_support_message,
    clear_login_logs,
)

try:
    from database import list_login_logs
except Exception:
    list_login_logs = None


def refresh_actor_from_db():
    user = get_user(current_username())
    if not user:
        return
    st.session_state.role = str(user.get("role") or "user")
    st.session_state.admin_level = int(user.get("admin_level") or 0)


def current_username():
    return str(st.session_state.get("user") or "").strip().lower()


def current_role():
    return str(st.session_state.get("role") or "user").strip().lower()


def current_level():
    return int(st.session_state.get("admin_level", 0) or 0)


def is_owner():
    return (
        current_username() == OWNER_USERNAME
        or current_role() == "owner"
        or current_level() >= 1337
    )


def is_admin():
    return is_owner() or current_role() == "admin" or current_level() >= 3


def is_moderator():
    return is_admin() or current_role() == "moderator" or current_level() >= 2


def is_supporter():
    return is_moderator() or current_role() == "supporter" or current_level() >= 1


def can_manage_roles():
    return is_admin()


def can_manage_owner():
    return is_owner()


def force_owner():
    if current_username() != OWNER_USERNAME:
        return

    user = get_user(OWNER_USERNAME)

    if not user:
        return

    if user.get("role") != "owner" or int(user.get("admin_level") or 0) != 1337:
        set_role(OWNER_USERNAME, "owner", 1337)
        st.session_state.role = "owner"
        st.session_state.admin_level = 1337


def safe_int(value):
    try:
        return int(value or 0)
    except Exception:
        return 0


def safe_float(value):
    try:
        return float(value or 0)
    except Exception:
        return 0.0


def money(value):
    return f"{safe_float(value):,.2f}€".replace(",", "X").replace(".", ",").replace("X", ".")


def safe_df(rows, height=430):
    if not rows:
        st.info("Keine Daten vorhanden.")
        return

    st.dataframe(
        pd.DataFrame(rows),
        width="stretch",
        hide_index=True,
        height=height,
    )


def require_panel_access():
    force_owner()

    if not is_supporter():
        st.error("Kein Zugriff.")
        st.stop()


def admin_css():
    inject_css(page_layout_css(1380, 90, 90) + """
.admin-title {
    font-size: 56px;
    line-height: .95;
    font-weight: 1000;
    letter-spacing: -3px;
    background: linear-gradient(135deg, #ffe7a3, #c084fc, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.admin-sub {
    color: #cbd5e1 !important;
    font-size: 16px;
    font-weight: 800;
    margin-top: 10px;
    margin-bottom: 26px;
}

.admin-pill {
    display: inline-flex;
    padding: 7px 13px;
    border-radius: 999px;
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: white !important;
    font-size: 12px;
    font-weight: 1000;
    margin-right: 8px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.12), transparent 32%),
        linear-gradient(145deg, rgba(12,13,32,.92), rgba(6,7,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.16) !important;
    border-radius: 24px !important;
    box-shadow: 0 16px 40px rgba(0,0,0,.22) !important;
}

.stButton > button {
    min-height: 46px !important;
    border-radius: 16px !important;
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.22), transparent 34%),
        linear-gradient(145deg, rgba(36,8,56,.98), rgba(12,3,25,.98)) !important;
    border: 1px solid rgba(168,85,247,.34) !important;
    color: #ffe7a3 !important;
    font-size: 15px !important;
    font-weight: 1000 !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 24px rgba(168,85,247,.25) !important;
}

.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] > div,
.stTextArea textarea {
    background: rgba(14,10,28,.96) !important;
    border: 1px solid rgba(168,85,247,.26) !important;
    border-radius: 16px !important;
    color: #ffe7a3 !important;
}

[data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(18,14,34,.88), rgba(8,7,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.18) !important;
    border-radius: 22px !important;
    padding: 18px !important;
}

[data-testid="metric-container"] label {
    color: #c084fc !important;
    font-size: 11px !important;
    font-weight: 1000 !important;
    text-transform: uppercase !important;
}

[data-testid="metric-container"] div {
    color: #ffe7a3 !important;
    font-weight: 1000 !important;
}
"""
    )


def render_header():
    st.markdown(
        f"""
<div class="admin-title">Admin Control</div>
<div class="admin-sub">
    MaByte Internal Panel
    <span class="admin-pill">{current_role().upper()}</span>
    <span class="admin-pill">Level {current_level()}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def render_overview():
    users = list_users()
    tickets = list_support_messages()
    usage = list_usage()
    payments = list_purchases()

    open_tickets = len([t for t in tickets if t.get("status") == "open"])
    banned = len([u for u in users if safe_int(u.get("is_banned")) == 1])
    revenue = sum(safe_float(p.get("amount")) for p in payments)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("User", len(users))

    with c2:
        st.metric("Tickets", open_tickets)

    with c3:
        st.metric("Usage", len(usage))

    with c4:
        st.metric("Revenue", money(revenue))

    with c5:
        st.metric("Banned", banned)

    st.write("")

    with st.container(border=True):
        st.subheader("Role System")
        st.write("Owner: alles. Admin: fast alles. Moderator: alles außer Rollen/Rechte. Supporter: nur Tickets.")


def render_tickets():
    st.subheader("Support Tickets")

    tickets = list_support_messages()

    if not tickets:
        st.info("Keine Tickets vorhanden.")
        return

    status_filter = st.selectbox("Status", ["all", "open", "closed"])

    for item in tickets:
        if status_filter != "all" and item.get("status") != status_filter:
            continue

        with st.container(border=True):
            st.markdown(f"### #{item.get('id')} · {item.get('subject', 'Ticket')}")
            st.caption(f"{item.get('username', '')} · {item.get('email', '')} · {item.get('created_at', '')}")
            st.write(item.get("message", ""))

            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("Open", key=f"ticket_open_{item.get('id')}"):
                    set_support_status(item.get("id"), "open")
                    st.rerun()

            with c2:
                if st.button("Close", key=f"ticket_close_{item.get('id')}"):
                    set_support_status(item.get("id"), "closed")
                    st.rerun()

            with c3:
                if is_moderator():
                    if st.button("Delete", key=f"ticket_delete_{item.get('id')}"):
                        delete_support_message(item.get("id"))
                        st.rerun()


def render_users():
    if not is_moderator():
        st.warning("Supporter können nur Tickets bearbeiten.")
        return

    refresh_actor_from_db()
    actor = current_username()

    st.subheader("User Management")

    users = list_users()

    search = st.text_input("User suchen", placeholder="Username oder Email")

    for item in users:
        uname = str(item.get("username") or "")
        email = str(item.get("email") or "")

        if search and search.lower() not in f"{uname} {email}".lower():
            continue

        current_plan = str(item.get("plan") or "free")
        current_role = str(item.get("role") or "user")
        current_level = safe_int(item.get("admin_level"))
        current_tokens = safe_int(item.get("tokens"))
        banned = safe_int(item.get("is_banned")) == 1

        with st.container(border=True):
            st.markdown(f"### {uname}")
            st.caption(f"{email} · {current_role} · Level {current_level}")

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                new_tokens = st.number_input(
                    "Tokens",
                    min_value=0,
                    value=current_tokens,
                    key=f"tokens_{uname}",
                )

                if st.button("Tokens speichern", key=f"save_tokens_{uname}"):
                    ok, msg = secure_update_tokens(actor, uname, int(new_tokens))
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                    st.rerun()

            with c2:
                plans = list(PLANS.keys())
                new_plan = st.selectbox(
                    "Plan",
                    plans,
                    index=plans.index(current_plan) if current_plan in plans else 0,
                    key=f"plan_{uname}",
                )

                if st.button("Plan speichern", key=f"save_plan_{uname}"):
                    ok, msg = secure_set_plan(actor, uname, new_plan)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                    st.rerun()

            with c3:
                if can_manage_roles():
                    role_options = ["user", "supporter", "moderator", "admin"]

                    if is_owner():
                        role_options.append("owner")

                    if current_role not in role_options:
                        current_role = "user"

                    new_role = st.selectbox(
                        "Rolle",
                        role_options,
                        index=role_options.index(current_role),
                        key=f"role_{uname}",
                    )

                    if st.button("Rolle speichern", key=f"save_role_{uname}"):
                        ok, msg = secure_set_role(actor, uname, new_role)
                        if ok:
                            st.success(msg)
                            refresh_actor_from_db()
                        else:
                            st.error(msg)
                        st.rerun()
                else:
                    st.info("Rollenverwaltung für Moderatoren gesperrt.")

            with c4:
                if uname == OWNER_USERNAME and not is_owner():
                    st.info("Owner geschützt.")
                else:
                    if st.button("Ban" if not banned else "Unban", key=f"ban_{uname}"):
                        ok, msg = secure_ban_user(actor, uname, not banned)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
                        st.rerun()

                    if is_admin() and uname != OWNER_USERNAME:
                        if st.button("User löschen", key=f"delete_{uname}"):
                            ok, msg = secure_delete_user(actor, uname)
                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)
                            st.rerun()


def render_redeem():
    if not is_moderator():
        st.warning("Kein Zugriff.")
        return

    st.subheader("Redeem Codes")

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)

        with c1:
            code_type = st.selectbox("Typ", ["tokens", "plan", "combo"])
            tokens = st.number_input("Tokens", min_value=0, value=100)

        with c2:
            plan = st.selectbox("Plan", ["", *PLANS.keys()])
            max_uses = st.number_input("Max Uses", min_value=1, value=1)

        with c3:
            days = st.number_input("Gültig Tage", min_value=1, value=30)

        if st.button("Code erstellen", width="stretch"):
            code = create_redeem_code(
                code_type=code_type,
                tokens=int(tokens),
                plan=plan,
                max_uses=int(max_uses),
                created_by=current_username(),
                days_valid=int(days),
            )
            st.success("Code erstellt:")
            st.code(code)

    st.write("")
    safe_df(list_codes(), height=360)


def render_usage():
    if not is_moderator():
        st.warning("Kein Zugriff.")
        return

    st.subheader("Usage Logs")
    safe_df(list_usage(), height=520)


def render_payments():
    if not is_moderator():
        st.warning("Kein Zugriff.")
        return

    st.subheader("Payments")
    safe_df(list_purchases(), height=520)


def render_login_logs():
    if not is_admin():
        st.warning("Nur Admins und Owner.")
        return

    st.subheader("Login Logs")

    if st.button("Login Logs clearen", width="stretch"):
        clear_login_logs()
        st.success("Login Logs gelöscht.")
        st.rerun()

    if list_login_logs is None:
        st.info("Login Logs sind nicht aktiviert.")
        return

    safe_df(list_login_logs(limit=300), height=520)


def render_owner_console():
    if not is_owner():
        st.warning("Nur Owner.")
        return

    st.subheader("Owner Console")

    with st.container(border=True):
        st.write("Owner Mode aktiv.")
        st.write("mepro1337 ist dauerhaft als Owner geschützt.")

        if st.button("mepro1337 als Owner setzen", width="stretch"):
            set_role(OWNER_USERNAME, "owner", 1337)
            st.success("Owner gesetzt.")
            st.rerun()


def render_admin():
    require_panel_access()
    refresh_actor_from_db()
    admin_css()
    render_header()

    if current_role() == "supporter" and not is_moderator():
        tabs = st.tabs(["Tickets"])
        with tabs[0]:
            render_tickets()
        return

    tabs = ["Overview", "Tickets", "Users", "Redeem", "Usage", "Payments"]

    if is_admin():
        tabs.append("Login Logs")

    if is_owner():
        tabs.append("Owner")

    tab_objects = st.tabs(tabs)

    index = 0

    with tab_objects[index]:
        render_overview()
    index += 1

    with tab_objects[index]:
        render_tickets()
    index += 1

    with tab_objects[index]:
        render_users()
    index += 1

    with tab_objects[index]:
        render_redeem()
    index += 1

    with tab_objects[index]:
        render_usage()
    index += 1

    with tab_objects[index]:
        render_payments()
    index += 1

    if is_admin():
        with tab_objects[index]:
            render_login_logs()
        index += 1

    if is_owner():
        with tab_objects[index]:
            render_owner_console()