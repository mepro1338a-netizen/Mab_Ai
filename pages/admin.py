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


# =========================================================
# CORE HELPERS
# =========================================================

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
    return f"{safe_float(value):,.2f}â‚¬".replace(",", "X").replace(".", ",").replace("X", ".")


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


# =========================================================
# CSS
# =========================================================

def admin_css():
    st.markdown(
        """
<style>

.stApp,
[data-testid="stAppViewContainer"]{
    background:
        radial-gradient(circle at 15% 0%, rgba(56,189,248,.20), transparent 30%),
        radial-gradient(circle at 90% 0%, rgba(124,58,237,.16), transparent 28%),
        linear-gradient(180deg,#06111f 0%,#0a1d38 45%,#08162b 100%) !important;
}

[data-testid="stHeader"]{
    background:transparent!important;
}

.main .block-container{
    max-width:1380px!important;
    padding-top:5.4rem!important;
    padding-bottom:3rem!important;
}

section[data-testid="stSidebar"]{
    background:#06111f!important;
}

.admin-shell{
    border-radius:34px;
    padding:28px;
    background:
        linear-gradient(180deg,rgba(15,23,42,.72),rgba(15,23,42,.38));
    border:1px solid rgba(148,163,184,.14);
    box-shadow:0 30px 80px rgba(0,0,0,.35);
}

.admin-hero{
    border-radius:30px;
    padding:28px 32px;
    margin-bottom:24px;
    background:
        radial-gradient(circle at 90% 15%,rgba(56,189,248,.24),transparent 30%),
        linear-gradient(135deg,rgba(2,6,23,.96),rgba(30,64,175,.82));
    border:1px solid rgba(255,215,128,.18);
    box-shadow:0 24px 60px rgba(0,0,0,.32);
}

.admin-kicker{
    color:#ffd36a;
    font-size:12px;
    font-weight:950;
    letter-spacing:.16em;
    text-transform:uppercase;
}

.admin-title{
    color:#fff1c2;
    font-size:44px;
    font-weight:1000;
    letter-spacing:-1.5px;
    line-height:1.05;
    margin-top:8px;
}

.admin-sub{
    color:#f8e7b0;
    font-size:15px;
    line-height:1.6;
    max-width:900px;
    margin-top:12px;
}

.admin-pill-row{
    display:flex;
    flex-wrap:wrap;
    gap:10px;
    margin-top:18px;
}

.admin-pill{
    display:inline-flex;
    align-items:center;
    gap:8px;
    padding:9px 13px;
    border-radius:999px;
    background:rgba(255,255,255,.10);
    border:1px solid rgba(255,255,255,.12);
    color:#dbeafe;
    font-size:12px;
    font-weight:850;
}

.kpi-card{
    border-radius:24px;
    padding:18px 20px;
    min-height:128px;
    background:
        radial-gradient(circle at 85% 15%, rgba(125,211,252,.30), transparent 34%),
        linear-gradient(135deg,#008cff 0%,#0057d9 55%,#082f91 100%);
    border:1px solid rgba(255,255,255,.22);
    box-shadow:
        0 18px 42px rgba(0,0,0,.26),
        inset 0 1px 0 rgba(255,255,255,.20);
}

.kpi-label{
    color:#dff7ff;
    font-size:11px;
    font-weight:950;
    letter-spacing:.10em;
    text-transform:uppercase;
}

.kpi-value{
    color:white;
    font-size:30px;
    font-weight:1000;
    line-height:1.05;
    margin-top:8px;
}

.kpi-sub{
    color:#dbeafe;
    font-size:12px;
    font-weight:750;
    margin-top:6px;
}

.panel-card{
    border-radius:26px;
    padding:22px;
    background:
        linear-gradient(180deg,rgba(15,23,42,.88),rgba(15,23,42,.62));
    border:1px solid rgba(255,255,255,.10);
    box-shadow:0 18px 48px rgba(0,0,0,.26);
}

.panel-title{
    color:#fff1c2;
    font-size:22px;
    font-weight:1000;
    letter-spacing:-.4px;
    margin-bottom:10px;
}

.panel-sub{
    color:#cbd5e1;
    font-size:13px;
    line-height:1.5;
    margin-bottom:14px;
}

.status-row{
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:11px 0;
    border-bottom:1px solid rgba(255,255,255,.08);
}

.status-name{
    color:#e0f2fe;
    font-size:14px;
    font-weight:800;
}

.status-badge{
    padding:5px 10px;
    border-radius:999px;
    background:rgba(34,197,94,.16);
    color:#86efac;
    font-size:12px;
    font-weight:900;
}

.warn-badge{
    background:rgba(245,158,11,.18);
    color:#fde68a;
}

.danger-badge{
    background:rgba(239,68,68,.18);
    color:#fecaca;
}

.admin-note{
    border-radius:22px;
    padding:18px;
    background:linear-gradient(135deg,rgba(255,211,106,.96),rgba(255,243,196,.96));
    border:1px solid rgba(245,158,11,.35);
    color:#111827;
    font-weight:800;
}

.section-title{
    color:#fff1c2;
    font-size:24px;
    font-weight:1000;
    margin:8px 0 14px 0;
}

div[data-testid="stTabs"] button{
    color:#dbeafe!important;
    font-weight:850!important;
}

div[data-testid="stTabs"] button[aria-selected="true"]{
    color:#ffd36a!important;
}

div[data-testid="stVerticalBlockBorderWrapper"]{
    background:
        linear-gradient(180deg,rgba(15,107,255,.62),rgba(12,52,150,.72))!important;
    border:1px solid rgba(255,215,128,.16)!important;
    border-radius:24px!important;
    box-shadow:0 18px 44px rgba(0,0,0,.25)!important;
}

div[data-testid="stMetric"]{
    background:
        radial-gradient(circle at 85% 15%, rgba(125,211,252,.35), transparent 35%),
        linear-gradient(135deg,#00b7ff 0%,#006dff 52%,#083b9c 100%)!important;
    border:1px solid rgba(255,255,255,.30)!important;
    border-radius:22px!important;
    padding:16px!important;
    box-shadow:0 14px 30px rgba(0,102,255,.25)!important;
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
    font-weight:950!important;
    background:linear-gradient(135deg,#ffd36a,#f59e0b)!important;
    color:#111827!important;
    box-shadow:0 12px 24px rgba(245,158,11,.18)!important;
}

.stButton > button:hover{
    transform:translateY(-1px);
    filter:brightness(1.04);
}

.stDataFrame{
    border-radius:20px!important;
    overflow:hidden!important;
}

hr{
    border-color:rgba(255,255,255,.10)!important;
}

</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# UI HELPERS
# =========================================================

def kpi(label, value, sub=""):
    st.markdown(
        f"""
<div class="kpi-card">
    <div class="kpi-label">{label}</div>
    <div class="kpi-value">{value}</div>
    <div class="kpi-sub">{sub}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def panel_start(title, sub=""):
    st.markdown(
        f"""
<div class="panel-card">
    <div class="panel-title">{title}</div>
    <div class="panel-sub">{sub}</div>
        """,
        unsafe_allow_html=True,
    )


def panel_end():
    st.markdown("</div>", unsafe_allow_html=True)


def status_line(name, status="Online", kind="ok"):
    badge = "status-badge"

    if kind == "warn":
        badge += " warn-badge"

    if kind == "danger":
        badge += " danger-badge"

    st.markdown(
        f"""
<div class="status-row">
    <div class="status-name">{name}</div>
    <div class="{badge}">{status}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# DATA HELPERS
# =========================================================

def get_admin_data():
    users = list_users()
    tickets = list_support_messages()
    codes = list_codes()
    logs = list_usage()
    payments = list_purchases()

    return users, tickets, codes, logs, payments


def estimate_revenue(payments):
    total = 0

    for p in payments:
        total += safe_float(
            p.get("amount")
            or p.get("price")
            or p.get("total")
            or 0
        )

    return total


def plan_distribution(users):
    counts = {}

    for u in users:
        plan = str(u.get("plan") or "free")
        counts[plan] = counts.get(plan, 0) + 1

    return counts


# =========================================================
# OVERVIEW
# =========================================================

def render_overview():
    users, tickets, codes, logs, payments = get_admin_data()

    total_tokens = sum(safe_int(u.get("tokens")) for u in users)
    banned = len([u for u in users if safe_int(u.get("is_banned")) == 1])
    active = len(users) - banned
    open_tickets = len([t for t in tickets if t.get("status") == "open"])
    revenue = estimate_revenue(payments)

    a, b, c, d, e = st.columns(5)

    with a:
        kpi("Users", len(users), f"{active} active")

    with b:
        kpi("Revenue", money(revenue), "tracked payments")

    with c:
        kpi("Tokens", f"{total_tokens:,}".replace(",", "."), "in circulation")

    with d:
        kpi("Tickets", open_tickets, "open support")

    with e:
        kpi("Risk", banned, "banned accounts")

    st.write("")

    left, mid, right = st.columns([1.15, 1, 1], gap="large")

    with left:
        panel_start("System Health", "Core services and platform status")
        status_line("OpenAI Core", "Online")
        status_line("Database", "Healthy")
        status_line("Railway Runtime", "Running")
        status_line("Stripe", "Ready", "warn")
        status_line("Football Engine", "Prepared", "warn")
        panel_end()

    with mid:
        panel_start("Plan Mix", "Current user distribution")

        counts = plan_distribution(users)

        rows = [{"Plan": k, "Users": v} for k, v in counts.items()]

        if rows:
            chart_df = pd.DataFrame(rows).set_index("Plan")
            st.bar_chart(chart_df)
        else:
            st.info("Keine Daten.")

        panel_end()

    with right:
        panel_start("Command Actions", "Fast internal operations")

        if st.button("Refresh Dashboard", width="stretch"):
            st.rerun()

        if st.button("Clear Session Cache", width="stretch"):
            st.session_state.clear()
            st.success("Session Cache geleert.")

        if st.button("Prepare Broadcast", width="stretch"):
            st.session_state.page = "admin"
            st.info("Broadcast System vorbereitet.")

        panel_end()

    st.divider()

    panel_start("Recent Platform Activity", "Latest AI usage and system logs")

    safe_df(logs[:12] if logs else [], height=330)

    panel_end()


# =========================================================
# ANALYTICS
# =========================================================

def render_analytics():
    require_admin(2)

    logs = list_usage()
    payments = list_purchases()
    users = list_users()

    revenue = estimate_revenue(payments)

    a, b, c, d = st.columns(4)

    with a:
        kpi("Usage Events", len(logs), "AI actions")

    with b:
        kpi("Payments", len(payments), "transactions")

    with c:
        kpi("Revenue", money(revenue), "estimated")

    with d:
        kpi("Users", len(users), "registered")

    st.write("")

    if not logs:
        st.info("Noch keine Analytics-Daten vorhanden.")
        return

    df = pd.DataFrame(logs)

    left, right = st.columns(2, gap="large")

    with left:
        panel_start("Usage by Tool", "Most used internal tools")

        if "tool" in df.columns:
            tool_counts = df["tool"].fillna("unknown").value_counts()
            st.bar_chart(tool_counts)
        else:
            st.info("Keine Tool-Spalte gefunden.")

        panel_end()

    with right:
        panel_start("Token Burn", "Estimated token consumption")

        if "cost_tokens" in df.columns and "tool" in df.columns:
            df["cost_tokens"] = pd.to_numeric(df["cost_tokens"], errors="coerce").fillna(0)
            burn = df.groupby("tool")["cost_tokens"].sum().sort_values(ascending=False)
            st.bar_chart(burn)
        else:
            st.info("Keine Token-Spalten gefunden.")

        panel_end()

    st.divider()

    panel_start("Raw Usage Feed", "Searchable usage intelligence")
    safe_df(logs, height=440)
    panel_end()


# =========================================================
# USERS
# =========================================================

def render_users():
    require_admin(1)

    panel_start("User Intelligence", "Search, filter and inspect accounts")

    users = list_users()

    c1, c2, c3 = st.columns(3)

    with c1:
        search = st.text_input("Search", placeholder="Username or Email")

    with c2:
        plan_filter = st.selectbox("Plan", ["all", "free", "pro", "grand", "elite"])

    with c3:
        status_filter = st.selectbox("Status", ["all", "active", "banned"])

    rows = []

    for u in users:
        username = str(u.get("username") or "")
        email = str(u.get("email") or "")
        plan = str(u.get("plan") or "free")
        banned = safe_int(u.get("is_banned")) == 1

        if search:
            q = search.lower()
            if q not in username.lower() and q not in email.lower():
                continue

        if plan_filter != "all" and plan != plan_filter:
            continue

        if status_filter == "active" and banned:
            continue

        if status_filter == "banned" and not banned:
            continue

        rows.append({
            "ID": u.get("id"),
            "Username": username,
            "Email": email,
            "Plan": plan,
            "Tokens": u.get("tokens"),
            "Role": u.get("role"),
            "Admin Level": u.get("admin_level"),
            "Rank": role_label(u.get("admin_level")),
            "Status": "Banned" if banned else "Active",
            "Created": u.get("created_at"),
            "Last Login": u.get("last_login"),
        })

    safe_df(rows, height=520)

    panel_end()


# =========================================================
# USER CONTROL
# =========================================================

def render_user_control():
    require_admin(3)

    users = list_users()
    usernames = [u.get("username") for u in users if u.get("username")]

    if not usernames:
        st.info("Keine User vorhanden.")
        return

    selected = st.selectbox("Select User", usernames)
    user = get_user(selected)

    if not user:
        st.error("User nicht gefunden.")
        return

    a, b, c, d = st.columns(4)

    with a:
        kpi("User", user.get("username"), user.get("email"))

    with b:
        kpi("Plan", user.get("plan"), "subscription")

    with c:
        kpi("Tokens", f"{safe_int(user.get('tokens')):,}".replace(",", "."), "balance")

    with d:
        status = "Banned" if safe_int(user.get("is_banned")) else "Active"
        kpi("Status", status, role_label(user.get("admin_level")))

    st.write("")

    left, right = st.columns(2, gap="large")

    with left:
        panel_start("Subscription Control", "Adjust plan and tokens")

        plans = ["free", "pro", "grand", "elite"]
        current_plan = user.get("plan", "free")

        if current_plan not in plans:
            current_plan = "free"

        new_plan = st.selectbox(
            "Plan",
            plans,
            index=plans.index(current_plan),
        )

        if st.button("Set Plan", width="stretch"):
            set_plan(selected, new_plan)
            add_audit_log(current_user(), "plan_changed", selected, new_plan)
            st.success("Plan aktualisiert.")
            st.rerun()

        new_tokens = st.number_input(
            "Tokens",
            min_value=0,
            max_value=999999999,
            value=safe_int(user.get("tokens")),
        )

        if st.button("Set Tokens", width="stretch"):
            update_tokens(selected, int(new_tokens))
            add_audit_log(current_user(), "tokens_updated", selected, str(new_tokens))
            st.success("Tokens aktualisiert.")
            st.rerun()

        panel_end()

    with right:
        panel_start("Security Control", "Roles, permissions and bans")

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
            "Role",
            roles,
            format_func=lambda x: f"{x[0]} â€” Level {x[2]}",
        )

        if st.button("Set Role", width="stretch"):
            set_role(selected, role[1], role[2])
            add_audit_log(current_user(), "role_changed", selected, f"{role[1]} / {role[2]}")
            st.success("Rolle aktualisiert.")
            st.rerun()

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Ban User", width="stretch"):
                ban_user(selected, True)
                add_audit_log(current_user(), "user_banned", selected, "")
                st.success("User gebannt.")
                st.rerun()

        with c2:
            if st.button("Unban User", width="stretch"):
                ban_user(selected, False)
                add_audit_log(current_user(), "user_unbanned", selected, "")
                st.success("User entbannt.")
                st.rerun()

        panel_end()


# =========================================================
# SUPPORT
# =========================================================

def render_tickets():
    require_admin(1)

    panel_start("Support Queue", "Manage user support requests")

    tickets = list_support_messages()

    if not tickets:
        st.info("Keine Tickets vorhanden.")
        panel_end()
        return

    status_filter = st.selectbox("Status", ["all", "open", "closed"])

    for t in tickets:
        if status_filter != "all" and t.get("status") != status_filter:
            continue

        with st.expander(f"#{t.get('id')} â€¢ {t.get('subject')} â€¢ {t.get('status')}"):
            st.write("User:", t.get("username"))
            st.write("Email:", t.get("email"))
            st.write("Kategorie:", t.get("category"))
            st.write("PrioritÃ¤t:", t.get("priority"))
            st.write("Nachricht:", t.get("message"))
            st.write("Erstellt:", t.get("created_at"))

            c1, c2 = st.columns(2)

            with c1:
                if st.button("Close", key=f"close_ticket_{t.get('id')}"):
                    set_support_status(t.get("id"), "closed")
                    add_audit_log(current_user(), "ticket_closed", str(t.get("id")), "")
                    st.success("Ticket geschlossen.")
                    st.rerun()

            with c2:
                if get_level() >= 3:
                    if st.button("Delete", key=f"delete_ticket_{t.get('id')}"):
                        delete_support_message(t.get("id"))
                        add_audit_log(current_user(), "ticket_deleted", str(t.get("id")), "")
                        st.success("Ticket gelÃ¶scht.")
                        st.rerun()

    panel_end()


# =========================================================
# REDEEM CODES
# =========================================================

def render_codes():
    require_admin(2)

    panel_start("Redeem Code Factory", "Create plan, token and combo codes")

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
        days_valid = st.number_input("GÃ¼ltig Tage", min_value=1, max_value=365, value=30)

    if st.button("Create Redeem Code", width="stretch"):
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

    safe_df(list_codes(), height=360)

    panel_end()


# =========================================================
# USAGE / PAYMENTS / LOGS
# =========================================================

def render_usage():
    require_admin(2)

    panel_start("Usage Intelligence", "AI usage events and token burn")

    logs = list_usage()

    search = st.text_input("Search Usage", placeholder="User, Tool, Provider, Status")

    if search:
        filtered = []

        for row in logs:
            text = " ".join([str(v) for v in row.values()])

            if search.lower() in text.lower():
                filtered.append(row)

        logs = filtered

    safe_df(logs, height=520)

    panel_end()


def render_payments():
    require_admin(2)

    payments = list_purchases()
    revenue = estimate_revenue(payments)

    a, b, c = st.columns(3)

    with a:
        kpi("Payments", len(payments), "transactions")

    with b:
        kpi("Revenue", money(revenue), "tracked")

    with c:
        avg = revenue / len(payments) if payments else 0
        kpi("Avg Payment", money(avg), "estimated")

    st.write("")

    panel_start("Payment Ledger", "Purchases and billing records")
    safe_df(payments, height=520)
    panel_end()


def render_audit():
    require_admin(3)

    panel_start("Audit Logs", "Security-sensitive admin actions")
    safe_df(list_audit_logs(), height=560)
    panel_end()


def render_login_logs():
    require_admin(3)

    panel_start("Login Intelligence", "IP, devices and session security")

    if list_login_logs is None:
        st.warning("Login-Logs sind noch nicht in database.py aktiviert.")
        panel_end()
        return

    safe_df(list_login_logs(limit=300), height=560)

    panel_end()


# =========================================================
# FOOTBALL
# =========================================================

def render_football_admin():
    require_admin(2)

    usage = list_usage()

    football_rows = []

    for row in usage:
        text = " ".join([str(v).lower() for v in row.values()])

        if "football" in text or "match" in text or "soccer" in text:
            football_rows.append(row)

    users = set([r.get("username") for r in football_rows if r.get("username")])
    tokens = sum(safe_int(r.get("cost_tokens")) for r in football_rows)

    a, b, c, d = st.columns(4)

    with a:
        kpi("Football Logs", len(football_rows), "events")

    with b:
        kpi("Football Users", len(users), "unique")

    with c:
        kpi("Tokens", f"{tokens:,}".replace(",", "."), "burned")

    with d:
        kpi("API Status", "Prepared", "gateway")

    st.write("")

    panel_start("Football Usage Feed", "Creator, API and match intelligence")
    safe_df(football_rows, height=520)
    panel_end()


# =========================================================
# SYSTEM TOOLS
# =========================================================

def render_system_tools():
    require_admin(3)

    if "maintenance_mode" not in st.session_state:
        st.session_state.maintenance_mode = False

    if "feature_flags" not in st.session_state:
        st.session_state.feature_flags = {
            "football_api": False,
            "stripe_live": False,
            "beta_dashboard": True,
            "automation_lab": False,
            "video_generation": False,
        }

    left, right = st.columns(2, gap="large")

    with left:
        panel_start("Release Control", "Maintenance and feature rollout")

        st.session_state.maintenance_mode = st.toggle(
            "Maintenance Mode",
            value=bool(st.session_state.maintenance_mode),
        )

        if st.session_state.maintenance_mode:
            st.warning("Maintenance Mode aktiv.")
        else:
            st.success("System normal.")

        panel_end()

    with right:
        panel_start("Feature Flags", "Internal rollout controls")

        flags = st.session_state.feature_flags

        for key in list(flags.keys()):
            flags[key] = st.toggle(
                key,
                value=bool(flags[key]),
                key=f"flag_{key}",
            )

        st.session_state.feature_flags = flags

        panel_end()

    st.write("")

    panel_start("Broadcast Center", "Prepare internal user announcements")

    message = st.text_area(
        "Broadcast Message",
        placeholder="Neue Features, Wartung, Football API Launch...",
    )

    if st.button("Save Broadcast", width="stretch"):
        st.session_state.broadcast_message = message
        add_audit_log(current_user(), "broadcast_saved", "system", message[:200])
        st.success("Broadcast gespeichert.")

    panel_end()


# =========================================================
# OWNER
# =========================================================

def render_owner_console():
    require_admin(1337)

    panel_start("Owner Console", "Highest privilege command layer")

    st.write("Owner Mode aktiv.")
    st.warning("Alle kritischen Aktionen sollten Ã¼ber Audit Logs nachvollziehbar bleiben.")

    st.markdown(
        """
<div class="admin-note">
Next build: Stripe Webhooks, real maintenance gate, persistent feature flags, API key management and AI cost tracking.
</div>
        """,
        unsafe_allow_html=True,
    )

    panel_end()


# =========================================================
# MAIN
# =========================================================

def render_admin_panel():
    require_admin(1)
    admin_css()

    st.markdown('<div class="admin-shell">', unsafe_allow_html=True)

    st.markdown(
        """
<div class="admin-hero">
    <div class="admin-kicker">MABYTE INTERNAL</div>
    <div class="admin-title">Owner Command Center</div>
    <div class="admin-sub">
        Premium control layer for users, tokens, plans, payments, football usage,
        feature flags, support and system intelligence.
    </div>
    <div class="admin-pill-row">
        <div class="admin-pill">System Online</div>
        <div class="admin-pill">Admin Secured</div>
        <div class="admin-pill">Football Ready</div>
        <div class="admin-pill">Stripe Prepared</div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )

    tabs = [
        "Command",
        "Analytics",
        "Users",
        "Control",
        "Support",
    ]

    if get_level() >= 2:
        tabs += [
            "Redeem",
            "Usage",
            "Payments",
            "Football",
        ]

    if get_level() >= 3:
        tabs += [
            "Logins",
            "Audit",
            "System",
        ]

    if is_owner():
        tabs += ["Owner"]

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

    st.markdown("</div>", unsafe_allow_html=True)


def render_admin():
    render_admin_panel()
