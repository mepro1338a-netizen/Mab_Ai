# =========================
# pages/admin.py
# =========================

import streamlit as st

from database import (
    list_users,
    list_support_messages,
    list_codes,
    list_usage,
    list_purchases,
)

ROLE_NAMES = {
    1: "Supporter",
    2: "Moderator",
    3: "Admin",
    1337: "Owner",
}


def get_level():
    return int(st.session_state.get("admin_level", 0))


def require_admin(level=1):
    if get_level() < level:
        st.error("Kein Zugriff.")
        st.stop()


def render_overview():
    users = list_users()
    tickets = list_support_messages()
    codes = list_codes()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="admin-stat-card">
            <div class="admin-stat-title">Users</div>
            <div class="admin-stat-value">{len(users)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="admin-stat-card">
            <div class="admin-stat-title">Tickets</div>
            <div class="admin-stat-value">{len(tickets)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="admin-stat-card">
            <div class="admin-stat-title">Redeem Codes</div>
            <div class="admin-stat-value">{len(codes)}</div>
        </div>
        """, unsafe_allow_html=True)


def render_users():
    st.subheader("👥 User Database")

    users = list_users()

    if not users:
        st.info("Noch keine User gefunden.")
        return

    for user in users:
        st.markdown(f"""
        <div class="admin-user-card">
            <div class="admin-user-top">
                👤 {user.get("username")}
            </div>

            <div>📧 {user.get("email")}</div>
            <div>💎 Plan: {user.get("plan")}</div>
            <div>🪙 Tokens: {user.get("tokens")}</div>
            <div>🛡️ Role: {user.get("role")}</div>
            <div>📅 Created: {user.get("created_at")}</div>
            <div>🕓 Last Login: {user.get("last_login")}</div>
        </div>
        """, unsafe_allow_html=True)


def render_tickets():
    st.subheader("🎫 Support Tickets")

    tickets = list_support_messages()

    if not tickets:
        st.info("Keine Tickets vorhanden.")
        return

    for ticket in tickets:
        st.markdown(f"""
        <div class="admin-ticket-card">
            <div><b>#{ticket.get("id")} - {ticket.get("subject")}</b></div>
            <div>👤 {ticket.get("username")}</div>
            <div>📧 {ticket.get("email")}</div>
            <div>📌 Status: {ticket.get("status")}</div>
            <div>📝 {ticket.get("message")}</div>
        </div>
        """, unsafe_allow_html=True)


def render_codes():
    st.subheader("🎁 Redeem Codes")

    codes = list_codes()

    if not codes:
        st.info("Keine Redeem Codes vorhanden.")
        return

    for code in codes:
        st.markdown(f"""
        <div class="admin-code-card">
            <div><b>{code.get("code")}</b></div>
            <div>💎 Plan: {code.get("plan")}</div>
            <div>🪙 Tokens: {code.get("tokens")}</div>
            <div>📅 Expires: {code.get("expires_at")}</div>
        </div>
        """, unsafe_allow_html=True)


def render_logs():
    st.subheader("📜 Usage Logs")

    logs = list_usage()

    if not logs:
        st.info("Keine Logs vorhanden.")
        return

    for log in logs:
        st.markdown(f"""
        <div class="admin-log-card">
            <div><b>{log.get("tool")}</b></div>
            <div>👤 {log.get("username")}</div>
            <div>🪙 Tokens: {log.get("tokens_used")}</div>
            <div>📅 {log.get("created_at")}</div>
        </div>
        """, unsafe_allow_html=True)


def render_payments():
    st.subheader("💳 Payments")

    payments = list_purchases()

    if not payments:
        st.info("Keine Payments vorhanden.")
        return

    for pay in payments:
        st.markdown(f"""
        <div class="admin-payment-card">
            <div><b>{pay.get("username")}</b></div>
            <div>💎 {pay.get("plan")}</div>
            <div>💰 {pay.get("amount")}€</div>
            <div>📌 {pay.get("payment_status")}</div>
        </div>
        """, unsafe_allow_html=True)


def render_admin_actions():
    require_admin(3)

    st.subheader("🛡️ Admin Actions")
    st.success("Nur Admin & Owner haben Zugriff.")


def render_admin_panel():
    require_admin(1)

    st.markdown("""
    <div class="admin-title">
        🛡️ Admin Panel
    </div>

    <div class="admin-subtitle">
        MaByte Control Center — Users, Tickets, Tokens, Logs und Payments.
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        "Overview",
        "Users",
        "Tickets",
        "Redeem Codes",
        "Logs",
        "Payments",
        "Admin Actions",
    ])

    with tabs[0]:
        render_overview()

    with tabs[1]:
        render_users()

    with tabs[2]:
        render_tickets()

    with tabs[3]:
        render_codes()

    with tabs[4]:
        render_logs()

    with tabs[5]:
        render_payments()

    if get_level() >= 3:
        with tabs[6]:
            render_admin_actions()


def render_admin():
    render_admin_panel()