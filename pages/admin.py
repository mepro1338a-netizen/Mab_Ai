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


def safe_df(rows):
    if not rows:
        st.info("Keine Daten vorhanden.")
        return

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )


def metric_card(label, value):
    with st.container(border=True):
        st.metric(label, value)


def admin_css():
    st.markdown(
        """
<style>
.main .block-container{
    max-width:1380px;
    padding-top:5.5rem;
    padding-bottom:3rem;
}

.admin-hero{
    border-radius:30px;
    padding:30px;
    margin-bottom:26px;
    background:
        radial-gradient(circle at 85% 20%, rgba(56,189,248,.22), transparent 30%),
        linear-gradient(135deg, rgba(15,23,42,.95), rgba(30,64,175,.84));
    border:1px solid rgba(255,215,128,.18);
    box-shadow:0 24px 60px rgba(0,0,0,.30);
}

.admin-kicker{
    color:#ffd36a;
    font-size:12px;
    font-weight:950;
    letter-spacing:.14em;
    text-transform:uppercase;
}

.admin-title{
    color:#fff1c2;
    font-size:42px;
    font-weight:1000;
    letter-spacing:-1.4px;
    line-height:1.05;
    margin-top:8px;
}

.admin-sub{
    color:#f8e7b0;
    font-size:15px;
    line-height:1.6;
    margin-top:12px;
}

.section-title{
    color:#fff1c2;
    font-size:26px;
    font-weight:1000;
    margin-top:20px;
    margin-bottom:10px;
}

div[data-testid="stMetric"]{
    background:
        radial-gradient(circle at 85% 15%, rgba(125,211,252,.40), transparent 35%),
        linear-gradient(135deg,#00b7ff 0%,#006dff 52%,#083b9c 100%)!important;
    border:1px solid rgba(255,255,255,.30)!important;
    border-radius:22px!important;
    padding:16px!important;
    box-shadow:0 14px 30px rgba(0,102,255,.28)!important;
}

div[data-testid="stMetricLabel"]{
    color:#dff7ff!important;
    font-size:11px!important;
    font-weight:950!important;
    text-transform:uppercase!important;
}

div[data-testid="stMetricValue"]{
    color:white!important;
    font-size:28px!important;
    font-weight:1000!important;
}

.stButton > button{
    border:none!important;
    border-radius:15px!important;
    min-height:43px!important;
    font-weight:900!important;
    background:linear-gradient(135deg,#ffd36a,#f59e0b)!important;
    color:#111827!important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_overview():
    users = list_users()
    tickets = list_support_messages()
    codes = list_codes()
    logs = list_usage()
    payments = list_purchases()

    total_tokens = sum(safe_int(u.get("tokens")) for u in users)
    banned = len([u for u in users if safe_int(u.get("is_banned")) == 1])
    open_tickets = len([t for t in tickets if t.get("status") == "open"])

    revenue = sum(safe_float(p.get("amount") or p.get("price")) for p in payments)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        metric_card("Users", len(users))
    with c2:
        metric_card("Revenue", money(revenue))
    with c3:
        metric_card("Tokens", f"{total_tokens:,}".replace(",", "."))
    with c4:
        metric_card("Tickets", open_tickets)
    with c5:
        metric_card("Banned", banned)

    st.divider()

    left, right = st.columns([1.3, 1], gap="large")

    with left:
        st.markdown("### Plan Distribution")
        plan_counts = {}

        for u in users:
            plan = str(u.get("plan") or "free")
            plan_counts[plan] = plan_counts.get(plan, 0) + 1

        plan_df = pd.DataFrame(
            [{"Plan": k, "Users": v} for k, v in plan_counts.items()]
        )

        if not plan_df.empty:
            st.bar_chart(plan_df.set_index("Plan"))

    with right:
        st.markdown("### System Status")

        safe_df([
            {"Service": "OpenAI", "Status": "Online"},
            {"Service": "Stripe", "Status": "Ready"},
            {"Service": "Database", "Status": "Healthy"},
            {"Service": "Railway", "Status": "Running"},
            {"Service": "Football Engine", "Status": "Prepared"},
        ])

    st.divider()

    st.markdown("### Recent Activity")

    safe_df(logs[:12] if logs else [])


def render_analytics():
    require_admin(2)

    st.subheader("Analytics Center")

    logs = list_usage()
    payments = list_purchases()
    users = list_users()

    c1, c2, c3, c4 = st.columns(4)

    total_usage = len(logs)
    total_payments = len(payments)
    total_revenue = sum(safe_float(p.get("amount") or p.get("price")) for p in payments)
    total_users = len(users)

    with c1:
        metric_card("Usage Events", total_usage)
    with c2:
        metric_card("Payments", total_payments)
    with c3:
        metric_card("Revenue", money(total_revenue))
    with c4:
        metric_card("Users", total_users)

    st.divider()

    if logs:
        df = pd.DataFrame(logs)

        if "tool" in df.columns:
            st.markdown("### Usage by Tool")
            tool_counts = df["tool"].fillna("unknown").value_counts()
            st.bar_chart(tool_counts)

        if "status" in df.columns:
            st.markdown("### Status Distribution")
            status_counts = df["status"].fillna("unknown").value_counts()
            st.bar_chart(status_counts)

        if "cost_tokens" in df.columns and "tool" in df.columns:
            st.markdown("### Token Burn by Tool")
            df["cost_tokens"] = pd.to_numeric(df["cost_tokens"], errors="coerce").fillna(0)
            burn = df.groupby("tool")["cost_tokens"].sum().sort_values(ascending=False)
            st.bar_chart(burn)

    else:
        st.info("Noch keine Analytics-Daten vorhanden.")


def render_users():
    require_admin(1)

    st.subheader("User Intelligence")

    users = list_users()
    search = st.text_input("User suchen", placeholder="Username oder Email")

    rows = []

    for u in users:
        username = str(u.get("username") or "")
        email = str(u.get("email") or "")

        if search:
            q = search.lower()
            if q not in username.lower() and q not in email.lower():
                continue

        rows.append({
            "ID": u.get("id"),
            "Username": username,
            "Email": email,
            "Plan": u.get("plan"),
            "Tokens": u.get("tokens"),
            "Role": u.get("role"),
            "Admin Level": u.get("admin_level"),
            "Rank": role_label(u.get("admin_level")),
            "Status": "Banned" if safe_int(u.get("is_banned")) == 1 else "Active",
            "Created": u.get("created_at"),
            "Last Login": u.get("last_login"),
        })

    safe_df(rows)


def render_user_control():
    require_admin(3)

    st.subheader("User Control Center")

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

    c0, c1, c2, c3 = st.columns(4)

    with c0:
        metric_card("User", user.get("username"))
    with c1:
        metric_card("Plan", user.get("plan"))
    with c2:
        metric_card("Tokens", user.get("tokens"))
    with c3:
        status = "Banned" if safe_int(user.get("is_banned")) else "Active"
        metric_card("Status", status)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Plan ändern")

        plans = ["free", "pro", "grand", "elite"]
        current_plan = user.get("plan", "free")

        if current_plan not in plans:
            current_plan = "free"

        new_plan = st.selectbox(
            "Neuer Plan",
            plans,
            index=plans.index(current_plan),
        )

        if st.button("Plan setzen", use_container_width=True):
            set_plan(selected, new_plan)
            add_audit_log(current_user(), "plan_changed", selected, new_plan)
            st.success("Plan aktualisiert.")
            st.rerun()

    with col2:
        st.subheader("Tokens setzen")

        new_tokens = st.number_input(
            "Tokens",
            min_value=0,
            max_value=999999999,
            value=safe_int(user.get("tokens")),
        )

        if st.button("Tokens setzen", use_container_width=True):
            update_tokens(selected, int(new_tokens))
            add_audit_log(current_user(), "tokens_updated", selected, str(new_tokens))
            st.success("Tokens aktualisiert.")
            st.rerun()

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
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

        if st.button("Rolle setzen", use_container_width=True):
            set_role(selected, role[1], role[2])
            add_audit_log(current_user(), "role_changed", selected, f"{role[1]} / {role[2]}")
            st.success("Rolle aktualisiert.")
            st.rerun()

    with col4:
        st.subheader("Ban Control")

        if st.button("User bannen", use_container_width=True):
            ban_user(selected, True)
            add_audit_log(current_user(), "user_banned", selected, "")
            st.success("User gebannt.")
            st.rerun()

        if st.button("User entbannen", use_container_width=True):
            ban_user(selected, False)
            add_audit_log(current_user(), "user_unbanned", selected, "")
            st.success("User entbannt.")
            st.rerun()


def render_system_tools():
    require_admin(3)

    st.subheader("System Tools")

    if "maintenance_mode" not in st.session_state:
        st.session_state.maintenance_mode = False

    if "feature_flags" not in st.session_state:
        st.session_state.feature_flags = {
            "football_api": False,
            "stripe_live": False,
            "beta_dashboard": True,
            "automation_lab": False,
        }

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Maintenance")

        st.session_state.maintenance_mode = st.toggle(
            "Maintenance Mode",
            value=bool(st.session_state.maintenance_mode),
        )

        if st.session_state.maintenance_mode:
            st.warning("Maintenance Mode aktiv.")
        else:
            st.success("System normal.")

    with c2:
        st.markdown("### Feature Flags")

        flags = st.session_state.feature_flags

        for key in list(flags.keys()):
            flags[key] = st.toggle(
                key,
                value=bool(flags[key]),
                key=f"flag_{key}",
            )

        st.session_state.feature_flags = flags

    st.divider()

    st.markdown("### Broadcast")

    message = st.text_area(
        "Nachricht vorbereiten",
        placeholder="Neue Features, Wartung, Football API Launch...",
    )

    if st.button("Broadcast speichern", use_container_width=True):
        st.session_state.broadcast_message = message
        add_audit_log(current_user(), "broadcast_saved", "system", message[:200])
        st.success("Broadcast gespeichert.")


def render_football_admin():
    require_admin(2)

    st.subheader("Football Intelligence Admin")

    usage = list_usage()

    football_rows = []
    for row in usage:
        tool = str(row.get("tool", "")).lower()
        if "football" in tool or "match" in tool:
            football_rows.append(row)

    users = set([r.get("username") for r in football_rows if r.get("username")])
    tokens = sum(safe_int(r.get("cost_tokens")) for r in football_rows)

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Football Logs", len(football_rows))
    with c2:
        metric_card("Football Users", len(users))
    with c3:
        metric_card("Football Tokens", f"{tokens:,}".replace(",", "."))

    st.divider()

    safe_df(football_rows)


def render_login_logs():
    require_admin(3)

    st.subheader("Login & IP Intelligence")

    if list_login_logs is None:
        st.warning("Login-Logs sind noch nicht in database.py aktiviert.")
        return

    safe_df(list_login_logs(limit=300))


def render_tickets():
    require_admin(1)

    st.subheader("Support Tickets")

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
                if st.button("Schließen", key=f"close_ticket_{t.get('id')}"):
                    set_support_status(t.get("id"), "closed")
                    add_audit_log(current_user(), "ticket_closed", str(t.get("id")), "")
                    st.success("Ticket geschlossen.")
                    st.rerun()

            with c2:
                if get_level() >= 3:
                    if st.button("Löschen", key=f"delete_ticket_{t.get('id')}"):
                        delete_support_message(t.get("id"))
                        add_audit_log(current_user(), "ticket_deleted", str(t.get("id")), "")
                        st.success("Ticket gelöscht.")
                        st.rerun()


def render_codes():
    require_admin(2)

    st.subheader("Redeem Code Factory")

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

    if st.button("Redeem Code erstellen", use_container_width=True):
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
    st.subheader("Usage Intelligence")
    safe_df(list_usage())


def render_payments():
    require_admin(2)
    st.subheader("Payments")
    safe_df(list_purchases())


def render_audit():
    require_admin(3)
    st.subheader("Audit Logs")
    safe_df(list_audit_logs())


def render_owner_console():
    require_admin(1337)

    st.subheader("Owner Console")

    with st.container(border=True):
        st.write("Owner Mode aktiv.")
        st.warning("Alle Aktionen werden im Audit Log gespeichert.")


def render_admin_panel():
    require_admin(1)
    admin_css()

    st.markdown(
        """
<div class="admin-hero">
    <div class="admin-kicker">MABYTE INTERNAL</div>
    <div class="admin-title">Owner Command Center</div>
    <div class="admin-sub">
        Verwalte User, Tokens, Plans, Payments, Tickets, Football Usage,
        Feature Flags, Broadcasts und System Logs.
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    tabs = [
        "Overview",
        "Analytics",
        "Users",
        "User Control",
        "Tickets",
    ]

    if get_level() >= 2:
        tabs += ["Redeem Codes", "Usage", "Payments", "Football"]

    if get_level() >= 3:
        tabs += ["Login Logs", "Audit", "System Tools"]

    if is_owner():
        tabs += ["Owner Console"]

    tab_objects = st.tabs(tabs)

    i = 0

    with tab_objects[i]:
        render_overview()
    i += 1

    with tab_objects[i]:
        render_analytics()
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

        with tab_objects[i]:
            render_football_admin()
        i += 1

    if get_level() >= 3:
        with tab_objects[i]:
            render_login_logs()
        i += 1

        with tab_objects[i]:
            render_audit()
        i += 1

        with tab_objects[i]:
            render_system_tools()
        i += 1

    if is_owner():
        with tab_objects[i]:
            render_owner_console()


def render_admin():
    render_admin_panel()