import base64
import random
import textwrap
from pathlib import Path

import streamlit as st

from database import (
    init_db,
    create_user,
    verify_login,
    get_user,
    list_users,
    set_plan,
    update_tokens,
    set_role,
    ban_user,
    delete_user,
    create_support_message,
    list_support_messages,
    support_counts,
    set_support_status,
    delete_support_message,
    create_redeem_code,
    list_codes,
    redeem_code,
    list_usage,
    list_purchases,
    list_audit_logs,
    add_audit_log,
)

BASE_DIR = Path(__file__).parent

HEADER_PATH = BASE_DIR / "neuerheader.png"
LOGO_PATH = BASE_DIR / "logo1.png"
FAVICON_PATH = BASE_DIR / "Logo24mp.png"


def img_b64(path: Path) -> str:
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode("utf-8")
    return ""


HEADER_B64 = img_b64(HEADER_PATH)
LOGO_B64 = img_b64(LOGO_PATH)

st.set_page_config(
    page_title="MAB.AI",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()


# =========================
# SESSION
# =========================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "plan" not in st.session_state:
    st.session_state.plan = "free"

if "tokens" not in st.session_state:
    st.session_state.tokens = 0

if "user" not in st.session_state:
    st.session_state.user = None

if "email" not in st.session_state:
    st.session_state.email = ""

if "role" not in st.session_state:
    st.session_state.role = "user"

if "admin_level" not in st.session_state:
    st.session_state.admin_level = 0

if "captcha_a" not in st.session_state:
    st.session_state.captcha_a = random.randint(1, 5)

if "captcha_b" not in st.session_state:
    st.session_state.captcha_b = random.randint(1, 5)


def refresh_captcha():
    st.session_state.captcha_a = random.randint(1, 5)
    st.session_state.captcha_b = random.randint(1, 5)


def sync_user(username: str):
    user = get_user(username)
    if user:
        st.session_state.user = user["username"]
        st.session_state.email = user["email"]
        st.session_state.plan = user["plan"]
        st.session_state.tokens = user["tokens"]
        st.session_state.role = user["role"]
        st.session_state.admin_level = user["admin_level"]


def is_admin():
    return st.session_state.role in ["supporter", "admin", "owner"] or st.session_state.admin_level > 0


def is_owner():
    return st.session_state.role == "owner" or st.session_state.admin_level >= 3


# =========================
# CSS
# =========================

st.markdown(
    """
<style>
html, body, .stApp {
    background: #05050a !important;
    color: white !important;
}

[data-testid="stHeader"] {
    background: #000000 !important;
    height: 86px !important;
}

.block-container {
    max-width: 1400px !important;
    padding-top: 120px !important;
    padding-bottom: 120px !important;
}

.top-logo-wrap {
    position: fixed;
    top: 12px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 999999;
    pointer-events: none;
}

.top-logo-wrap img {
    height: 60px;
    width: auto;
    object-fit: contain;
}

section[data-testid="stSidebar"] {
    background: #050509 !important;
    border-right: 1px solid rgba(255,215,0,.20);
    min-width: 320px !important;
    max-width: 320px !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.stButton button {
    width: 100% !important;
    background: #000 !important;
    color: white !important;
    border: 1px solid rgba(255,215,0,.45) !important;
    border-radius: 16px !important;
    min-height: 48px !important;
    font-weight: 800 !important;
}

.stButton button:hover {
    border-color: #ffd700 !important;
    color: #ffd700 !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div {
    background: #000 !important;
    color: white !important;
}

.hero-box {
    background:
        radial-gradient(circle at top left, rgba(0,183,255,.25), transparent 35rem),
        radial-gradient(circle at top right, rgba(168,85,247,.25), transparent 35rem),
        linear-gradient(135deg, #10253c 0%, #171e36 55%, #42206a 100%);
    border-radius: 42px;
    padding: 80px 60px;
    text-align: center;
    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 30px 90px rgba(0,0,0,.45);
    margin-bottom: 34px;
}

.hero-title {
    font-size: clamp(46px, 5.5vw, 90px);
    line-height: 1.08;
    font-weight: 950;
    letter-spacing: -4px;
    color: white !important;
}

.hero-logo {
    margin: 28px auto 36px auto;
    display: flex;
    justify-content: center;
    align-items: center;
}

.hero-logo img {
    height: 95px;
    width: auto;
    object-fit: contain;
    border-radius: 18px;
    background: #000;
    padding: 8px 18px;
    box-shadow: 0 10px 35px rgba(0,0,0,.45);
}

.hero-subtitle {
    font-size: 34px;
    font-weight: 900;
    color: white !important;
    margin-top: 24px;
}

.hero-text {
    margin: 24px auto 0 auto;
    max-width: 1050px;
    font-size: 24px;
    line-height: 1.65;
    color: #e5e7eb !important;
    text-align: center;
}

.plan-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 22px;
    margin-top: 34px;
    margin-bottom: 120px;
}

.plan-card {
    background: #101018;
    border-radius: 26px;
    padding: 32px;
    min-height: 210px;
    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 24px 70px rgba(0,0,0,.30);
}

.plan-card h3 {
    font-size: 36px;
    margin: 0 0 20px 0;
    color: white !important;
}

.plan-card p {
    font-size: 19px;
    line-height: 1.6;
    color: #d4d4d8 !important;
}

.locked {
    opacity: .82;
}

@media(max-width: 900px) {
    .block-container {
        padding-top: 105px !important;
    }

    section[data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
    }

    .top-logo-wrap img {
        height: 52px;
    }

    .hero-box {
        padding: 42px 24px;
        border-radius: 30px;
    }

    .hero-title {
        font-size: 42px;
        letter-spacing: -2px;
    }

    .hero-logo img {
        height: 65px;
    }

    .hero-subtitle {
        font-size: 24px;
    }

    .hero-text {
        font-size: 18px;
    }

    .plan-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

if HEADER_B64:
    st.markdown(
        f'<div class="top-logo-wrap"><img src="data:image/png;base64,{HEADER_B64}"></div>',
        unsafe_allow_html=True,
    )


# =========================
# NAV
# =========================

def plan_rank(plan):
    return {"free": 1, "pro": 2, "grand": 3, "elite": 4}.get(plan, 1)


def nav_button(label, page, required_plan="free"):
    locked = plan_rank(st.session_state.plan) < plan_rank(required_plan)
    text = f"🔒 {label}" if locked else label
    key = f"nav_{page}_{required_plan}_{label}".replace(" ", "_").replace("/", "_")

    if st.button(text, use_container_width=True, key=key):
        st.session_state.page = "premium" if locked else page
        st.rerun()


with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)

    st.markdown("## MAB.AI")

    if st.session_state.user:
        st.success(f"👤 {st.session_state.user}")
        st.caption(f"Plan: {st.session_state.plan}")
        st.caption(f"Tokens: {st.session_state.tokens}")
        st.caption(f"Role: {st.session_state.role}")

        if st.button("Logout", key="logout_btn"):
            st.session_state.user = None
            st.session_state.email = ""
            st.session_state.plan = "free"
            st.session_state.tokens = 0
            st.session_state.role = "user"
            st.session_state.admin_level = 0
            st.session_state.page = "home"
            st.rerun()
    else:
        if st.button("Login / Register", key="login_register_btn"):
            st.session_state.page = "login"
            st.rerun()

    st.markdown("---")
    st.markdown("### Free")
    nav_button("Memory Chat", "chat", "free")

    st.markdown("### Pro")
    nav_button("Coding Area", "coding", "pro")
    nav_button("Image Generator", "image", "pro")
    nav_button("Music Generator", "music", "pro")
    nav_button("Short Reels Creator", "reels", "pro")

    st.markdown("### Grand")
    nav_button("AI Video Generator", "video", "grand")

    st.markdown("### Account")
    nav_button("User Dashboard", "dashboard")
    nav_button("Support", "support")
    nav_button("Buy Premium", "premium")

    if is_admin():
        st.markdown("### Admin")
        nav_button("Admin Panel", "admin")


# =========================
# HOME
# =========================

if st.session_state.page == "home":
    logo_html = "MAB.AI"
    if LOGO_B64:
        logo_html = f'<img src="data:image/png;base64,{LOGO_B64}">'

    html = f"""
<section class="hero-box">
  <div class="hero-title">Hallo willkommen auf</div>
  <div class="hero-logo">{logo_html}</div>
  <div class="hero-subtitle">
    Die neue AI für die Revolution von Social Media, Business Bereiche uvm.
  </div>
  <div class="hero-text">
    Starte mit Memory Chat, erstelle Texte, plane Projekte,
    sammle Ideen oder lass dir direkt helfen.
  </div>
  <div class="hero-text">
    Egal ob Programmierung, Monetarisierung oder künstliche Intelligenz —
    in jedem Bereich können wir dir helfen.
  </div>
</section>

<div class="plan-grid">
  <div class="plan-card">
    <h3>Free</h3>
    <p>Memory Chat inklusive.</p>
  </div>
  <div class="plan-card locked">
    <h3>🔒 Pro</h3>
    <p>1200 Tokens<br>Coding, Images, Musik & Reels.</p>
  </div>
  <div class="plan-card locked">
    <h3>🔒 Grand</h3>
    <p>4000 Tokens<br>AI Video Generator.</p>
  </div>
  <div class="plan-card locked">
    <h3>🔒 Elite</h3>
    <p>Alles freigeschaltet.<br>Höchste API-Leistung.</p>
  </div>
</div>
"""
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)


# =========================
# LOGIN
# =========================

elif st.session_state.page == "login":
    st.title("🔐 Login / Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_btn"):
            ok, msg, user = verify_login(username, password)

            if ok and user:
                st.session_state.user = user["username"]
                st.session_state.email = user["email"]
                st.session_state.plan = user["plan"]
                st.session_state.tokens = user["tokens"]
                st.session_state.role = user["role"]
                st.session_state.admin_level = user["admin_level"]
                st.session_state.page = "home"
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    with tab2:
        reg_user = st.text_input("Username", key="register_user")
        reg_mail = st.text_input("Email", key="register_mail")
        reg_pw = st.text_input("Password", type="password", key="register_pw")

        result = st.session_state.captcha_a + st.session_state.captcha_b

        captcha = st.number_input(
            f"Was ist {st.session_state.captcha_a} + {st.session_state.captcha_b}?",
            min_value=0,
            max_value=10,
            step=1,
            key="captcha_input",
        )

        if st.button("Register", key="register_btn"):
            if captcha != result:
                st.error("Captcha falsch.")
                refresh_captcha()
                st.rerun()

            if not reg_user or not reg_mail or not reg_pw:
                st.error("Bitte alles ausfüllen.")
            else:
                ok, msg = create_user(reg_user, reg_mail, reg_pw)

                if ok:
                    st.success(msg)
                    refresh_captcha()
                else:
                    st.error(msg)


# =========================
# FEATURES
# =========================

elif st.session_state.page == "chat":
    st.title("💬 Memory Chat")
    st.text_area("Nachricht", key="chat_prompt")
    st.button("Senden", key="chat_send")


elif st.session_state.page == "coding":
    st.title("💻 Coding Area")
    st.text_area("Was soll gebaut werden?", key="coding_prompt")
    st.button("Code generieren", key="code_generate")


elif st.session_state.page == "image":
    st.title("🎨 Image Generator")
    st.text_area("Bildbeschreibung", key="image_prompt")
    st.button("Bild generieren", key="img_generate")


elif st.session_state.page == "music":
    st.title("🎵 Music Generator")
    st.text_area("Musikbeschreibung", key="music_prompt")
    st.button("Musik generieren", key="music_generate")


elif st.session_state.page == "reels":
    st.title("🎞️ Short Reels Creator")
    st.text_area("Reel Beschreibung", key="reels_prompt")
    st.button("Reel erstellen", key="reel_generate")


elif st.session_state.page == "video":
    st.title("🎬 AI Video Generator")
    st.text_area("Videobeschreibung", key="video_prompt")
    st.button("Video generieren", key="video_generate")


# =========================
# DASHBOARD
# =========================

elif st.session_state.page == "dashboard":
    st.title("📊 User Dashboard")

    if st.session_state.user:
        sync_user(st.session_state.user)

    st.metric("User", st.session_state.user or "Nicht eingeloggt")
    st.metric("Plan", st.session_state.plan)
    st.metric("Tokens", st.session_state.tokens)

    st.markdown("### Redeem Code")
    code = st.text_input("Code eingeben", key="redeem_code_input")

    if st.button("Code einlösen", key="redeem_btn"):
        if not st.session_state.user:
            st.error("Bitte zuerst einloggen.")
        elif not code:
            st.error("Bitte Code eingeben.")
        else:
            ok, msg = redeem_code(st.session_state.user, code)
            if ok:
                sync_user(st.session_state.user)
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


# =========================
# SUPPORT
# =========================

elif st.session_state.page == "support":
    st.title("🆘 Support")

    subject = st.text_input("Betreff", key="support_subject")
    msg = st.text_area("Nachricht", key="support_msg")
    category = st.selectbox(
        "Kategorie",
        ["Allgemein", "Account", "Payment", "Technik", "Bug"],
        key="support_category",
    )

    if st.button("Ticket senden", key="ticket_send"):
        if not subject or not msg:
            st.error("Bitte alles ausfüllen.")
        else:
            username = st.session_state.user or "guest"
            email = st.session_state.email or ""
            ok, response = create_support_message(
                username=username,
                email=email,
                category=category,
                subject=subject,
                message=msg,
            )
            if ok:
                st.success(response)
            else:
                st.error(response)


# =========================
# PREMIUM
# =========================

elif st.session_state.page == "premium":
    st.title("💳 Buy Premium")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### Pro\n**9.99€ / Monat**\n\n1200 Tokens")
        st.button("Buy Pro", key="buy_pro")

    with c2:
        st.markdown("### Grand\n**49.99€ / Monat**\n\n4000 Tokens")
        st.button("Buy Grand", key="buy_grand")

    with c3:
        st.markdown("### Elite\n**199€ / Monat**\n\nAlles freigeschaltet. Höchste API-Leistung.")
        st.button("Buy Elite", key="buy_elite")


# =========================
# ADMIN PANEL
# =========================

elif st.session_state.page == "admin":
    if not is_admin():
        st.error("Kein Zugriff.")
        st.stop()

    st.title("🛡️ Admin Panel")

    counts = support_counts()

    a, b, c, d = st.columns(4)
    a.metric("Tickets Gesamt", counts.get("total", 0))
    b.metric("Offen", counts.get("open", 0))
    c.metric("Geschlossen", counts.get("closed", 0))
    d.metric("Admin Level", st.session_state.admin_level)

    tab_tickets, tab_users, tab_codes, tab_logs, tab_payments = st.tabs(
        ["Tickets", "Users", "Redeem Codes", "Logs", "Payments"]
    )

    with tab_tickets:
        st.subheader("🎫 Support Tickets")

        status_filter = st.selectbox("Status Filter", ["all", "open", "closed"], key="admin_ticket_filter")
        tickets = list_support_messages(status_filter)

        if not tickets:
            st.info("Keine Tickets vorhanden.")
        else:
            for ticket in tickets:
                with st.expander(f"#{ticket['id']} · {ticket['subject']} · {ticket['status']}"):
                    st.write(f"User: {ticket['username']}")
                    st.write(f"Email: {ticket['email']}")
                    st.write(f"Kategorie: {ticket['category']}")
                    st.write(f"Nachricht: {ticket['message']}")
                    st.write(f"Erstellt: {ticket['created_at']}")

                    c1, c2 = st.columns(2)

                    if c1.button("Als geschlossen markieren", key=f"close_ticket_{ticket['id']}"):
                        set_support_status(ticket["id"], "closed")
                        add_audit_log(st.session_state.user, "close_ticket", str(ticket["id"]))
                        st.rerun()

                    if c2.button("Ticket löschen", key=f"delete_ticket_{ticket['id']}"):
                        delete_support_message(ticket["id"])
                        add_audit_log(st.session_state.user, "delete_ticket", str(ticket["id"]))
                        st.rerun()

    with tab_users:
        st.subheader("👥 User Verwaltung")

        users = list_users()
        st.dataframe([dict(u) for u in users], use_container_width=True)

        st.markdown("### User bearbeiten")

        target_user = st.text_input("Username", key="admin_target_user")
        new_plan = st.selectbox("Plan", ["free", "pro", "grand", "elite"], key="admin_new_plan")
        new_tokens = st.number_input("Tokens setzen", min_value=0, value=0, step=100, key="admin_new_tokens")

        if is_owner():
            new_role = st.selectbox("Role", ["user", "supporter", "admin", "owner"], key="admin_new_role")
            new_level = st.selectbox("Admin Level", [0, 1, 2, 3], key="admin_new_level")
        else:
            new_role = "user"
            new_level = 0

        c1, c2, c3, c4 = st.columns(4)

        if c1.button("Plan setzen", key="admin_set_plan"):
            set_plan(target_user, new_plan)
            add_audit_log(st.session_state.user, "set_plan", target_user, new_plan)
            st.success("Plan geändert.")

        if c2.button("Tokens setzen", key="admin_set_tokens"):
            update_tokens(target_user, new_tokens)
            add_audit_log(st.session_state.user, "set_tokens", target_user, str(new_tokens))
            st.success("Tokens geändert.")

        if c3.button("User bannen", key="admin_ban_user"):
            ban_user(target_user, True)
            add_audit_log(st.session_state.user, "ban_user", target_user)
            st.success("User gebannt.")

        if c4.button("User löschen", key="admin_delete_user"):
            delete_user(target_user)
            add_audit_log(st.session_state.user, "delete_user", target_user)
            st.success("User gelöscht.")

        if is_owner():
            if st.button("Role / Admin Level setzen", key="admin_set_role"):
                set_role(target_user, new_role, new_level)
                add_audit_log(st.session_state.user, "set_role", target_user, f"{new_role}:{new_level}")
                st.success("Role geändert.")

    with tab_codes:
        st.subheader("🎟️ Redeem Codes")

        if not is_owner():
            st.info("Nur Owner/Admin Level 3 kann Codes erstellen.")
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
                add_audit_log(st.session_state.user, "create_redeem_code", code)
                st.success(f"Code erstellt: {code}")

        codes = list_codes()
        st.dataframe([dict(c) for c in codes], use_container_width=True)

    with tab_logs:
        st.subheader("📊 Usage Logs")
        usage = list_usage()
        st.dataframe([dict(u) for u in usage], use_container_width=True)

        st.subheader("🧾 Audit Logs")
        audits = list_audit_logs()
        st.dataframe([dict(a) for a in audits], use_container_width=True)

    with tab_payments:
        st.subheader("💳 Payments")
        payments = list_purchases()
        st.dataframe([dict(p) for p in payments], use_container_width=True)