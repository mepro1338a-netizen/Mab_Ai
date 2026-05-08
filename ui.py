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

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).parent

HEADER_PATH = BASE_DIR / "neuerheader.png"
LOGO_PATH = BASE_DIR / "logo1.png"
FAVICON_PATH = BASE_DIR / "Logo24mp.png"


# =========================================================
# CACHED HELPERS
# =========================================================

@st.cache_data(show_spinner=False)
def img_b64(path_str: str) -> str:
    path = Path(path_str)
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode("utf-8")
    return ""


@st.cache_resource(show_spinner=False)
def boot_database():
    init_db()


HEADER_B64 = img_b64(str(HEADER_PATH))
LOGO_B64 = img_b64(str(LOGO_PATH))


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MAB.AI",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

boot_database()


# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "page": "home",
    "plan": "free",
    "tokens": 0,
    "user": None,
    "email": "",
    "role": "user",
    "admin_level": 0,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

if "captcha_a" not in st.session_state:
    st.session_state.captcha_a = random.randint(1, 5)

if "captcha_b" not in st.session_state:
    st.session_state.captcha_b = random.randint(1, 5)


# =========================================================
# LOGIC
# =========================================================

def refresh_captcha():
    st.session_state.captcha_a = random.randint(1, 5)
    st.session_state.captcha_b = random.randint(1, 5)


def sync_user(username: str):
    if not username:
        return

    user = get_user(username)
    if not user:
        return

    st.session_state.user = user["username"]
    st.session_state.email = user["email"]
    st.session_state.plan = user["plan"]
    st.session_state.tokens = user["tokens"]
    st.session_state.role = user["role"]
    st.session_state.admin_level = user["admin_level"]


def logout():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
    st.rerun()


def is_admin():
    return (
        st.session_state.role in ["supporter", "admin", "owner"]
        or int(st.session_state.admin_level or 0) > 0
    )


def is_owner():
    return st.session_state.role == "owner" or int(st.session_state.admin_level or 0) >= 3


def plan_rank(plan):
    return {
        "free": 1,
        "pro": 2,
        "grand": 3,
        "elite": 4,
    }.get(plan, 1)


def can_use(required_plan):
    return plan_rank(st.session_state.plan) >= plan_rank(required_plan) or is_admin()


def go(page):
    st.session_state.page = page
    st.rerun()


# =========================================================
# CSS
# =========================================================

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
    box-shadow: 0 0 18px rgba(255,215,0,.14) !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div {
    background: #000 !important;
    color: white !important;
    border-radius: 14px !important;
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

.card-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 22px;
    margin-top: 34px;
    margin-bottom: 44px;
}

.app-card {
    background: #101018;
    border-radius: 26px;
    padding: 32px;
    min-height: 210px;
    border: 1px solid rgba(255,255,255,.10);
    box-shadow: 0 24px 70px rgba(0,0,0,.30);
}

.app-card h3 {
    font-size: 32px;
    margin: 0 0 18px 0;
    color: white !important;
}

.app-card p {
    font-size: 18px;
    line-height: 1.6;
    color: #d4d4d8 !important;
}

.locked {
    opacity: .82;
}

.page-card {
    background: #101018;
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 28px;
    padding: 34px;
    box-shadow: 0 24px 70px rgba(0,0,0,.30);
    margin-bottom: 24px;
}

.badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(255,215,0,.12);
    border: 1px solid rgba(255,215,0,.35);
    color: #ffd700;
    font-weight: 800;
    margin-bottom: 16px;
}

.price-card {
    background: linear-gradient(180deg, #111127, #090914);
    border: 1px solid rgba(255,215,0,.25);
    border-radius: 30px;
    padding: 34px;
    min-height: 360px;
    box-shadow: 0 24px 70px rgba(0,0,0,.35);
}

.price-card h2 {
    color: white !important;
    font-size: 38px;
}

.price {
    font-size: 34px;
    font-weight: 950;
    color: #ffd700;
    margin: 16px 0;
}

.feature-list {
    color: #d4d4d8;
    line-height: 1.9;
    font-size: 18px;
}

.sidebar-box {
    background: #0f0f18;
    border: 1px solid rgba(255,215,0,.18);
    border-radius: 18px;
    padding: 16px;
    margin: 14px 0;
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

    .card-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# HEADER LOGO
# =========================================================

if HEADER_B64:
    st.markdown(
        f'<div class="top-logo-wrap"><img src="data:image/png;base64,{HEADER_B64}"></div>',
        unsafe_allow_html=True,
    )


# =========================================================
# NAVIGATION
# =========================================================

def nav_button(label, page, required_plan="free"):
    locked = not can_use(required_plan)
    text = f"🔒 {label}" if locked else label
    key = f"nav_{page}_{required_plan}_{label}".replace(" ", "_").replace("/", "_")

    if st.button(text, use_container_width=True, key=key):
        go("premium" if locked else page)


with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)

    st.markdown("## MAB.AI")

    if st.session_state.user:
        st.markdown(
            f"""
            <div class="sidebar-box">
                <b>👤 {st.session_state.user}</b><br>
                ⭐ Plan: {st.session_state.plan}<br>
                🪙 Tokens: {st.session_state.tokens}<br>
                🛡️ Role: {st.session_state.role}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Logout", key="logout_btn"):
            logout()
    else:
        if st.button("Login / Register", key="login_register_btn"):
            go("login")

    st.markdown("---")
    st.markdown("### Free")
    nav_button("💬 Memory Chat", "chat", "free")

    st.markdown("### Pro")
    nav_button("💻 Coding Area", "coding", "pro")
    nav_button("🎨 Image Generator", "image", "pro")
    nav_button("🎵 Music Generator", "music", "pro")
    nav_button("🎞️ Short Reels Creator", "reels", "pro")

    st.markdown("### Grand")
    nav_button("🎬 AI Video Generator", "video", "grand")

    st.markdown("### Account")
    nav_button("📊 User Dashboard", "dashboard")
    nav_button("🆘 Support", "support")
    nav_button("💳 Buy Premium", "premium")

    if is_admin():
        st.markdown("### Admin")
        nav_button("🛡️ Admin Panel", "admin")


# =========================================================
# HOME
# =========================================================

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

<div class="card-grid">
  <div class="app-card">
    <h3>Free</h3>
    <p>Memory Chat inklusive. Perfekt zum Starten, Planen und Schreiben.</p>
  </div>
  <div class="app-card locked">
    <h3>🔒 Pro</h3>
    <p>1200 Tokens<br>Coding, Images, Musik & Reels.</p>
  </div>
  <div class="app-card locked">
    <h3>🔒 Grand</h3>
    <p>4000 Tokens<br>AI Video Generator und stärkere Workflows.</p>
  </div>
  <div class="app-card locked">
    <h3>🔒 Elite</h3>
    <p>Alles freigeschaltet.<br>Höchste API-Leistung.</p>
  </div>
</div>
"""
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)


# =========================================================
# LOGIN / REGISTER
# =========================================================

elif st.session_state.page == "login":
    st.title("🔐 Login / Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.markdown('<div class="page-card">', unsafe_allow_html=True)

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

        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="page-card">', unsafe_allow_html=True)

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

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# FEATURES
# =========================================================

elif st.session_state.page in ["chat", "coding", "image", "music", "reels", "video"]:
    feature_map = {
        "chat": (
            "💬 Memory Chat",
            "free",
            "Schreibe, plane, sammle Ideen und arbeite mit deinem AI-Assistenten.",
        ),
        "coding": (
            "💻 Coding Area",
            "pro",
            "Lass dir Code schreiben, debuggen, refactoren oder erklären.",
        ),
        "image": (
            "🎨 Image Generator",
            "pro",
            "Erstelle Bilder für Social Media, Branding, Produkte und Kampagnen.",
        ),
        "music": (
            "🎵 Music Generator",
            "pro",
            "Erstelle Musikideen, Lyrics, Prompts und später komplette Audio-Workflows.",
        ),
        "reels": (
            "🎞️ Short Reels Creator",
            "pro",
            "Erstelle virale Reel-Ideen, Skripte, Hooks und Video-Prompts.",
        ),
        "video": (
            "🎬 AI Video Generator",
            "grand",
            "Generiere Video-Prompts und später komplette Video-Workflows.",
        ),
    }

    title, required, desc = feature_map[st.session_state.page]

    st.markdown(
        f"""
        <div class="page-card">
            <span class="badge">{required.upper()} Feature</span>
            <h1>{title}</h1>
            <p style="font-size:20px;color:#d4d4d8;line-height:1.7;">{desc}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not can_use(required):
        st.warning(f"Dieses Feature benötigt mindestens {required.upper()}.")
        st.session_state.page = "premium"
        st.stop()

    prompt = st.text_area("Dein Prompt", key=f"{st.session_state.page}_prompt", height=180)

    if st.button("Starten", key=f"{st.session_state.page}_start"):
        st.success("API kommt im nächsten Schritt rein.")


# =========================================================
# DASHBOARD
# =========================================================

elif st.session_state.page == "dashboard":
    st.title("📊 User Dashboard")

    if st.session_state.user:
        sync_user(st.session_state.user)

    a, b, c = st.columns(3)
    a.metric("User", st.session_state.user or "Nicht eingeloggt")
    b.metric("Plan", st.session_state.plan)
    c.metric("Tokens", st.session_state.tokens)

    st.markdown('<div class="page-card">', unsafe_allow_html=True)
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

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# SUPPORT
# =========================================================

elif st.session_state.page == "support":
    st.title("🆘 Support")

    st.markdown('<div class="page-card">', unsafe_allow_html=True)

    subject = st.text_input("Betreff", key="support_subject")
    msg = st.text_area("Nachricht", key="support_msg", height=180)
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

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# PREMIUM
# =========================================================

elif st.session_state.page == "premium":
    st.title("💳 Buy Premium")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="price-card">
                <h2>Pro</h2>
                <div class="price">9.99€ / Monat</div>
                <div class="feature-list">
                    • 1200 Tokens<br>
                    • Coding Area<br>
                    • Image Generator<br>
                    • Music Generator<br>
                    • Short Reels Creator
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Buy Pro", key="buy_pro")

    with c2:
        st.markdown(
            """
            <div class="price-card">
                <h2>Grand</h2>
                <div class="price">49.99€ / Monat</div>
                <div class="feature-list">
                    • 4000 Tokens<br>
                    • Alles aus Pro<br>
                    • AI Video Generator<br>
                    • Stärkere Workflows
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Buy Grand", key="buy_grand")

    with c3:
        st.markdown(
            """
            <div class="price-card">
                <h2>Elite</h2>
                <div class="price">199€ / Monat</div>
                <div class="feature-list">
                    • Alles freigeschaltet<br>
                    • Höchste API-Leistung<br>
                    • Beste Qualität<br>
                    • Maximaler Zugriff
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Buy Elite", key="buy_elite")


# =========================================================
# ADMIN PANEL
# =========================================================

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
        status_filter = st.selectbox(
            "Status Filter",
            ["all", "open", "closed"],
            key="admin_ticket_filter",
        )

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
        if st.button("Users laden", key="load_users_btn"):
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

        if st.button("Codes laden", key="load_codes_btn"):
            codes = list_codes()
            st.dataframe([dict(c) for c in codes], use_container_width=True)

    with tab_logs:
        if st.button("Logs laden", key="load_logs_btn"):
            usage = list_usage()
            audits = list_audit_logs()

            st.subheader("Usage Logs")
            st.dataframe([dict(u) for u in usage], use_container_width=True)

            st.subheader("Audit Logs")
            st.dataframe([dict(a) for a in audits], use_container_width=True)

    with tab_payments:
        if st.button("Payments laden", key="load_payments_btn"):
            payments = list_purchases()
            st.dataframe([dict(p) for p in payments], use_container_width=True)