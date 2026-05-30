"""MaByte Admin Control Panel — Owner / Admin / Moderator / Supporter."""
from __future__ import annotations

import html
import io
from datetime import datetime

import pandas as pd
import streamlit as st

from config import DB_PATH, PLANS, FOOTBALL_PLANS
from db.admin_stats import (
    env_health_snapshot,
    football_usage_aggregate,
    platform_metrics,
    staff_directory,
)
from ui.admin_ui import (
    inject_admin_ui_css,
    render_activity_feed,
    render_distribution_bars,
    render_hero,
    render_kpi_grid,
    render_section,
    render_ticket_card,
    render_user_header,
)
from ui.premium_foundation import render_status_badge, render_empty_state
from ui.stripe_admin_diagnostics import render_stripe_admin_diagnostics
from ui.styles import inject_css, page_layout_css
from database import (
    OWNER_USERNAME,
    ROLE_LEVELS,
    get_user,
    list_users,
    secure_update_tokens,
    secure_set_plan,
    secure_set_football_plan,
    secure_set_role,
    secure_ban_user,
    secure_delete_user,
    set_role,
    create_redeem_code,
    list_codes,
    list_usage,
    list_purchases,
    list_support_messages,
    list_ticket_replies,
    add_ticket_reply,
    set_support_status,
    set_support_priority,
    delete_support_message,
    clear_login_logs,
    list_login_logs,
    list_audit_logs,
    usage_summary,
    list_leads,
    lead_count,
)

try:
    from database import recent_activity
except ImportError:
    recent_activity = None


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
    except (TypeError, ValueError):
        return 0


def safe_float(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def money(value):
    return f"{safe_float(value):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def safe_df(rows, height=400):
    if not rows:
        st.info("Keine Einträge.")
        return
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True, height=height)


def require_panel_access():
    from services.access_control import require_admin_panel
    require_admin_panel()
    force_owner()
    if not is_supporter():
        st.error("Kein Zugriff auf das Admin Control Panel.")
        st.stop()


def admin_css():
    inject_css(page_layout_css(1400, 88, 48))
    inject_admin_ui_css()
    inject_css("""
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div,
.stTextArea textarea {
    background: rgba(10,12,26,.95) !important;
    border: 1px solid rgba(168,85,247,.22) !important;
    border-radius: 14px !important;
    color: #f8fafc !important;
}
""")


def render_command_center():
    m = platform_metrics()
    render_kpi_grid([
        ("Nutzer", str(m["users_total"]), f"+{m['users_new_7d']} diese Woche", "default"),
        ("Aktiv 24h", str(m["users_active_24h"]), "Eingeloggt / aktiv", "good"),
        ("Offene Tickets", str(m["tickets_open"]), f"{m['tickets_total']} gesamt", "warn" if m["tickets_open"] else "good"),
        ("Umsatz", money(m["revenue_total"]), f"{money(m['revenue_7d'])} · 7T", "good"),
        ("Usage 24h", str(m["usage_24h"]), f"{m['usage_total']} gesamt", "default"),
        ("Tokens 7T", f"{m['tokens_7d']:,}".replace(",", "."), "Verbrauch", "default"),
        ("Football Premium", str(m["football_paid"]), "Aktive FB-Pläne", "default"),
        ("Premium", str(m.get("premium_users", 0)), f"+{m.get('premium_conversions_7d', 0)} Conv. 7T", "good"),
        ("Errors 24h", str(m.get("errors_24h", 0)), "App-Fehler", "warn" if m.get("errors_24h") else "good"),
        ("Security", str(m["failed_logins_24h"]), "Fehl-Logins 24h", "warn" if m["failed_logins_24h"] else "good"),
    ])

    c1, c2 = st.columns(2)
    with c1:
        render_distribution_bars("Pläne (MaByte)", m.get("plans") or {})
    with c2:
        render_distribution_bars("Football Pläne", m.get("football_plans") or {})

    st.markdown('<div class="adm-section" style="margin-top:12px">', unsafe_allow_html=True)
    st.markdown('<div class="adm-section-title">Live Activity</div>', unsafe_allow_html=True)
    feed = []
    for row in (list_usage() or [])[:6]:
        feed.append((
            str(row.get("tool", "system")).replace("_", " ").title(),
            f"{row.get('username', '')} · {str(row.get('created_at', ''))[:16]} · {row.get('cost_tokens', 0)} Tokens",
        ))
    for p in (list_purchases() or [])[:3]:
        feed.append((
            "Zahlung",
            f"{p.get('username', '')} · {money(p.get('amount'))} · {str(p.get('created_at', ''))[:16]}",
        ))
    render_activity_feed(feed[:10])
    st.markdown("</div>", unsafe_allow_html=True)


def render_analytics():
    if not is_moderator():
        st.warning("Kein Zugriff.")
        return

    m = platform_metrics()
    render_section("Analytics Dashboard", "Production Beta · Live Metriken")
    render_kpi_grid([
        ("Aktiv 24h", str(m["users_active_24h"]), "Unique Nutzer", "good"),
        ("Neu 7T", str(m["users_new_7d"]), "Registrierungen", "default"),
        ("Premium Nutzer", str(m.get("premium_users", 0)), "Plan ≠ Free", "good"),
        ("Conversions 7T", str(m.get("premium_conversions_7d", 0)), "Stripe paid", "good"),
        ("AI Usage 24h", str(m["usage_24h"]), f"{m['usage_total']} total", "default"),
        ("Tokens 7T", f"{m['tokens_7d']:,}".replace(",", "."), "Verbrauch", "default"),
        ("Stripe 7T", money(m["revenue_7d"]), money(m["revenue_total"]), "good"),
        ("Errors 24h", str(m.get("errors_24h", 0)), "App errors", "warn" if m.get("errors_24h") else "good"),
    ])

    c1, c2, c3 = st.columns(3)
    with c1:
        render_distribution_bars("MaByte Pläne", m.get("plans") or {})
    with c2:
        render_distribution_bars("Football Pläne", m.get("football_plans") or {})
    with c3:
        render_distribution_bars("Errors nach Kategorie", m.get("errors_by_category") or {})

    try:
        from db.errors import errors_last_24h
        err_rows = errors_last_24h(30)
        if err_rows:
            st.markdown('<div class="adm-section-title">Errors (24h)</div>', unsafe_allow_html=True)
            safe_df(err_rows, height=220)
    except Exception:
        pass

    render_section("Workspace Usage", "Nutzung nach Workspace · letzte 7 Tage")
    tool_rows = usage_summary(days=7)
    if tool_rows:
        tool_data = {str(r.get("tool") or "?"): int(r.get("runs") or 0) for r in tool_rows}
        render_distribution_bars("Top Workspaces", tool_data)
        safe_df(tool_rows, height=280)
    else:
        render_empty_state("Keine Usage-Daten", "Sobald Nutzer AI/Apps nutzen, erscheinen Stats hier.")

    if is_owner():
        fb_rows = football_usage_aggregate()
        if fb_rows:
            st.markdown('<div class="adm-section-title" style="margin-top:16px">Football API (7 Tage)</div>', unsafe_allow_html=True)
            safe_df(fb_rows, height=220)


def render_leads():
    if not is_moderator():
        st.warning("Kein Zugriff.")
        return

    total = lead_count()
    render_section("Lead CRM", f"{total} Leads · vollständige Registrierungsdaten")

    rows = list_leads(limit=500)
    if not rows:
        render_empty_state("Noch keine Leads", "Neue Registrierungen erscheinen hier automatisch.")
        return

    export_rows = []
    for r in rows:
        export_rows.append({
            "id": r.get("id"),
            "username": r.get("username"),
            "email": r.get("email"),
            "name": r.get("full_name"),
            "company": r.get("company"),
            "phone": r.get("phone"),
            "country": r.get("country"),
            "use_case": r.get("use_case"),
            "marketing": r.get("marketing_opt_in"),
            "status": r.get("status"),
            "ip": r.get("ip_address"),
            "created": str(r.get("created_at", ""))[:19],
        })

    st.metric("Leads gesamt", total)
    safe_df(export_rows, height=420)
    st.download_button(
        "CSV Export",
        data=pd.DataFrame(export_rows).to_csv(index=False).encode("utf-8"),
        file_name=f"mabyte_leads_{datetime.utcnow().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="adm_leads_csv",
    )


def render_tickets():
    render_section("Support Inbox", "Antworten, Priorität, Status-Timeline")
    tickets = list_support_messages()
    if not tickets:
        render_empty_state("Inbox leer", "Neue Support-Anfragen erscheinen hier.")
        return

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        status_filter = st.selectbox(
            "Status", ["all", "open", "in_progress", "closed"], key="adm_ticket_status"
        )
    with f2:
        categories = sorted({str(t.get("category") or "Sonstiges") for t in tickets})
        cat_filter = st.selectbox("Kategorie", ["all", *categories], key="adm_ticket_cat")
    with f3:
        prio_filter = st.selectbox(
            "Priorität", ["all", "urgent", "high", "normal", "low"], key="adm_ticket_prio"
        )
    with f4:
        st.metric(
            "Offen",
            sum(1 for t in tickets if str(t.get("status") or "") in ("open", "in_progress")),
        )

    shown = 0
    actor = current_username()
    for item in tickets:
        if status_filter != "all" and item.get("status") != status_filter:
            continue
        if cat_filter != "all" and str(item.get("category") or "") != cat_filter:
            continue
        if prio_filter != "all" and str(item.get("priority") or "normal") != prio_filter:
            continue
        shown += 1
        tid = int(item.get("id") or 0)
        st.markdown(render_ticket_card(item), unsafe_allow_html=True)
        st.caption(
            f"Priorität: **{item.get('priority', 'normal')}** · "
            f"Aktualisiert: {str(item.get('updated_at', ''))[:16]}"
        )

        for rep in list_ticket_replies(tid):
            who = "Team" if int(rep.get("is_staff") or 0) else rep.get("author", "User")
            st.markdown(
                f'<div class="adm-activity"><strong>{html.escape(str(who))}</strong> · '
                f'{html.escape(str(rep.get("created_at", ""))[:16])}<br>'
                f'{html.escape(str(rep.get("body") or "")[:500])}</div>',
                unsafe_allow_html=True,
            )

        with st.form(f"adm_reply_{tid}"):
            reply_body = st.text_area("Admin-Antwort", height=90, key=f"adm_reply_txt_{tid}")
            if st.form_submit_button("Antwort senden", width="stretch"):
                if reply_body.strip():
                    ok, msg = add_ticket_reply(tid, actor, reply_body.strip(), is_staff=True)
                    if ok:
                        set_support_status(tid, "in_progress")
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            if st.button("Öffnen", key=f"t_open_{tid}"):
                set_support_status(tid, "open")
                st.rerun()
        with c2:
            if st.button("In Arbeit", key=f"t_prog_{tid}"):
                set_support_status(tid, "in_progress")
                st.rerun()
        with c3:
            if st.button("Schließen", key=f"t_close_{tid}"):
                set_support_status(tid, "closed")
                st.rerun()
        with c4:
            prio_opts = ["low", "normal", "high", "urgent"]
            cur_prio = str(item.get("priority") or "normal")
            prio_idx = prio_opts.index(cur_prio) if cur_prio in prio_opts else 1
            new_prio = st.selectbox(
                "Prio",
                prio_opts,
                index=prio_idx,
                key=f"t_prio_{tid}",
                label_visibility="collapsed",
            )
            if st.button("Prio setzen", key=f"t_prio_set_{tid}"):
                set_support_priority(tid, new_prio)
                st.rerun()
        with c5:
            render_status_badge(str(item.get("status") or "open"))
            if is_moderator() and st.button("Löschen", key=f"t_del_{tid}"):
                delete_support_message(tid)
                st.rerun()
    if shown == 0:
        st.info("Keine Tickets für diesen Filter.")


def _filter_users(users, search, role_f, plan_f, banned_f, fb_f):
    for item in users:
        uname = str(item.get("username") or "")
        email = str(item.get("email") or "")
        if search and search.lower() not in f"{uname} {email}".lower():
            continue
        if role_f != "all" and str(item.get("role") or "user") != role_f:
            continue
        if plan_f != "all" and str(item.get("plan") or "free") != plan_f:
            continue
        if fb_f != "all" and str(item.get("football_plan") or "none") != fb_f:
            continue
        if banned_f == "banned" and safe_int(item.get("is_banned")) != 1:
            continue
        if banned_f == "active" and safe_int(item.get("is_banned")) == 1:
            continue
        yield item


def render_users():
    if not is_moderator():
        st.warning("Supporter: nur Tickets.")
        return

    refresh_actor_from_db()
    actor = current_username()
    users = list_users()

    render_section("User Operations", f"{len(users)} Accounts · sichere Verwaltung ohne Auto-Linking")

    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            search = st.text_input("Suche", placeholder="User / Email", key="adm_user_search")
        with c2:
            role_f = st.selectbox("Rolle", ["all", "user", "supporter", "moderator", "admin", "owner"], key="adm_f_role")
        with c3:
            plan_f = st.selectbox("Plan", ["all", *PLANS.keys()], key="adm_f_plan")
        with c4:
            fb_f = st.selectbox("Football", ["all", "none", *FOOTBALL_PLANS.keys()], key="adm_f_fb")
        with c5:
            banned_f = st.selectbox("Status", ["all", "active", "banned"], key="adm_f_ban")

    filtered = list(_filter_users(users, search, role_f, plan_f, banned_f, fb_f))
    st.caption(f"{len(filtered)} Treffer")

    for item in filtered[:40]:
        uname = str(item.get("username") or "")
        st.markdown(render_user_header(item), unsafe_allow_html=True)

        with st.expander(f"Verwalten · {uname}", expanded=False):
            current_plan = str(item.get("plan") or "free")
            current_fb = str(item.get("football_plan") or "none")
            current_role_val = str(item.get("role") or "user")
            current_tokens = safe_int(item.get("tokens"))
            banned = safe_int(item.get("is_banned")) == 1

            g1, g2, g3 = st.columns(3)
            with g1:
                new_tokens = st.number_input("Tokens", 0, 1_000_000, current_tokens, key=f"tok_{uname}")
                if st.button("Tokens speichern", key=f"save_tok_{uname}"):
                    ok, msg = secure_update_tokens(actor, uname, int(new_tokens))
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()
            with g2:
                plans = list(PLANS.keys())
                new_plan = st.selectbox("Plan", plans, index=plans.index(current_plan) if current_plan in plans else 0, key=f"pl_{uname}")
                if st.button("Plan speichern", key=f"save_pl_{uname}"):
                    ok, msg = secure_set_plan(actor, uname, new_plan)
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()
            with g3:
                fb_plans = ["none", *FOOTBALL_PLANS.keys()]
                fb_i = fb_plans.index(current_fb) if current_fb in fb_plans else 0
                new_fb = st.selectbox("Football", fb_plans, index=fb_i, key=f"fb_{uname}",
                    format_func=lambda x: "Keiner" if x == "none" else FOOTBALL_PLANS.get(x, {}).get("label", x))
                if st.button("FB speichern", key=f"save_fb_{uname}"):
                    ok, msg = secure_set_football_plan(actor, uname, new_fb)
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()

            g4, g5 = st.columns(2)
            with g4:
                if can_manage_roles():
                    role_opts = ["user", "supporter", "moderator", "admin"] + (["owner"] if is_owner() else [])
                    if current_role_val not in role_opts:
                        current_role_val = "user"
                    new_role = st.selectbox("Rolle", role_opts, index=role_opts.index(current_role_val), key=f"role_{uname}")
                    if st.button("Rolle speichern", key=f"save_role_{uname}"):
                        ok, msg = secure_set_role(actor, uname, new_role)
                        if ok:
                            st.success(msg)
                            refresh_actor_from_db()
                        else:
                            st.error(msg)
                        st.rerun()
                else:
                    st.info("Rollen: nur Admin/Owner")
            with g5:
                if uname == OWNER_USERNAME and not is_owner():
                    st.warning("Owner geschützt.")
                else:
                    if st.button("Sperren" if not banned else "Entsperren", key=f"ban_{uname}"):
                        ok, msg = secure_ban_user(actor, uname, not banned)
                        st.success(msg) if ok else st.error(msg)
                        st.rerun()
                    if is_admin() and uname != OWNER_USERNAME:
                        if st.button("Account löschen", key=f"del_{uname}", type="primary"):
                            ok, msg = secure_delete_user(actor, uname)
                            st.success(msg) if ok else st.error(msg)
                            st.rerun()

    if len(filtered) > 40:
        st.caption("Zeige max. 40 User — Filter verfeinern.")


def render_revenue():
    if not is_moderator():
        return
    payments = list_purchases()
    paid = [p for p in payments if str(p.get("payment_status") or "") == "paid"]
    render_section("Revenue Center", f"{len(paid)} erfolgreiche Zahlungen")
    render_kpi_grid([
        ("Umsatz gesamt", money(sum(safe_float(p.get("amount")) for p in paid)), f"{len(paid)} Payments", "good"),
        ("Durchschnitt", money(sum(safe_float(p.get("amount")) for p in paid) / max(len(paid), 1)), "pro Zahlung", "default"),
        ("Stripe Sessions", str(len(payments)), "inkl. offen", "default"),
        ("Letzte", str(payments[0].get("username", "—")) if payments else "—", str(payments[0].get("created_at", ""))[:16] if payments else "", "default"),
    ])
    safe_df(payments[:100], height=420)


def render_codes():
    if not is_moderator():
        return
    render_section("Redeem Codes", "Tokens, Pläne & Combos ausgeben")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            code_type = st.selectbox("Typ", ["tokens", "plan", "combo"], key="adm_code_type")
            tokens = st.number_input("Tokens", 0, 100000, 100, key="adm_code_tok")
        with c2:
            plan = st.selectbox("Plan", ["", *PLANS.keys()], key="adm_code_plan")
            max_uses = st.number_input("Max Uses", 1, 10000, 1, key="adm_code_uses")
        with c3:
            days = st.number_input("Gültig (Tage)", 1, 365, 30, key="adm_code_days")
        if st.button("Code generieren", type="primary", width="stretch"):
            code = create_redeem_code(
                code_type=code_type,
                tokens=int(tokens),
                plan=plan,
                max_uses=int(max_uses),
                created_by=current_username(),
                days_valid=int(days),
            )
            st.success("Code erstellt")
            st.code(code)
    safe_df(list_codes(), height=360)


def render_security():
    if not is_admin():
        st.warning("Nur Admin & Owner.")
        return
    render_section("Security & Audit", "Login-Versuche und Admin-Aktionen")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Login-Logs leeren", width="stretch"):
            clear_login_logs()
            st.success("Login-Logs gelöscht.")
            st.rerun()
    with c2:
        failed = sum(1 for l in list_login_logs(limit=100) if not safe_int(l.get("success")))
        st.metric("Fehlversuche (letzte 100)", failed)

    tab_login, tab_audit = st.tabs(["Login Logs", "Audit Trail"])
    with tab_login:
        safe_df(list_login_logs(limit=250), height=400)
    with tab_audit:
        if list_audit_logs:
            safe_df(list_audit_logs(limit=250), height=400)
        else:
            st.info("Audit-Logs leer.")


def render_team():
    if not is_admin():
        st.warning("Nur Admin & Owner.")
        return
    render_section("Team Directory", "Interne Rollen & Berechtigungen")
    staff = staff_directory()
    if not staff:
        render_empty_state("Kein Team", "Weise Rollen unter Users zu.")
        return
    for member in staff:
        st.markdown(render_user_header(member), unsafe_allow_html=True)
    st.markdown(
        """
| Rolle | Level | Rechte |
|--------|-------|--------|
| Supporter | 1 | Tickets |
| Moderator | 2 | + Users, Codes, Usage, Revenue |
| Admin | 3 | + Rollen, Security, Audit |
| Owner | 1337 | Vollzugriff + System |
        """
    )


def render_owner_os():
    if not is_owner():
        st.warning("Nur Owner (mepro1337).")
        return

    render_section("Owner Operations", "System, Export, Bulk-Aktionen")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Owner-Rechte für mepro1337 erzwingen", width="stretch"):
            set_role(OWNER_USERNAME, "owner", 1337)
            st.success("Owner gesetzt.")
            st.rerun()
    with c2:
        users = list_users()
        csv_buf = io.StringIO()
        if users:
            pd.DataFrame(users).to_csv(csv_buf, index=False)
            st.download_button(
                "User-Export (CSV)",
                csv_buf.getvalue(),
                file_name=f"mabyte_users_{datetime.utcnow().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                width="stretch",
            )

    with st.container(border=True):
        st.markdown("**Bulk Token Grant**")
        bc1, bc2 = st.columns(2)
        with bc1:
            bulk_user = st.text_input("Username", key="owner_bulk_user")
        with bc2:
            bulk_tokens = st.number_input("Tokens", 0, 10_000_000, 1000, key="owner_bulk_tok")
        if st.button("Tokens vergeben", key="owner_bulk_grant"):
            ok, msg = secure_update_tokens(current_username(), bulk_user.strip().lower(), int(bulk_tokens))
            st.success(msg) if ok else st.error(msg)

    st.markdown('<div class="adm-section-title" style="margin-top:16px">System Health (ENV)</div>', unsafe_allow_html=True)
    env_rows = env_health_snapshot()
    env_html = "".join(
        f'<div class="adm-activity"><div class="t">{html.escape(label)}</div>'
        f'<div class="d"><span class="{"adm-env-ok" if ok else "adm-env-miss"}">'
        f'{"Konfiguriert" if ok else "Fehlt"}</span></div></div>'
        for label, ok in env_rows
    )
    st.markdown(env_html, unsafe_allow_html=True)
    st.caption(f"Datenbank: {DB_PATH}")


def render_admin():
    require_panel_access()
    refresh_actor_from_db()
    admin_css()
    render_hero(current_role(), current_level(), is_owner=is_owner())

    if current_role() == "supporter" and not is_moderator():
        render_tickets()
        return

    tabs = ["Command Center", "Users", "Leads", "Tickets", "Revenue", "Codes", "Analytics"]
    if is_admin():
        tabs.extend(["Security", "Team"])
    if is_owner():
        tabs.append("Owner OS")

    tab_objs = st.tabs(tabs)
    idx = 0

    with tab_objs[idx]:
        render_command_center()
    idx += 1
    with tab_objs[idx]:
        render_users()
    idx += 1
    with tab_objs[idx]:
        render_leads()
    idx += 1
    with tab_objs[idx]:
        render_tickets()
    idx += 1
    with tab_objs[idx]:
        render_revenue()
    idx += 1
    with tab_objs[idx]:
        render_codes()
    idx += 1
    with tab_objs[idx]:
        render_analytics()
    idx += 1

    if is_admin():
        with tab_objs[idx]:
            render_stripe_admin_diagnostics()
        idx += 1
        with tab_objs[idx]:
            render_security()
        idx += 1
        with tab_objs[idx]:
            render_team()
        idx += 1

    if is_owner():
        with tab_objs[idx]:
            render_owner_os()
