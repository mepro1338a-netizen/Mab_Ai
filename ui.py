from dotenv import load_dotenv
load_dotenv()

import base64
import os
import json
from pathlib import Path
import streamlit as st

from config import APP_NAME, PLANS, LOGO_PATH, ROLE_LABELS

from database import (
    init_db,
    list_users,
    list_purchases,
    set_plan,
    update_tokens,
    set_role,
    delete_user,
    create_user,
    add_memory,
    load_memory,
    create_redeem_code,
    list_codes,
    redeem_code,
    create_support_message,
    list_support_messages,
    support_counts,
    set_support_read,
    set_support_status,
    delete_support_message,
)

from auth import login_user, register_user

from backend import (
    refresh_user,
    process_chat,
    process_coding,
    process_image,
    process_video,
    process_music,
)

from payments import create_checkout_session


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

SESSION_FILE = "session.json"


# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def logo_base64():
    path = Path(LOGO_PATH)
    if path.exists():
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


LOGO_B64 = logo_base64()


def plan_label(plan):
    return PLANS.get(plan, PLANS["free"])["label"]


def role_label(role):
    return ROLE_LABELS.get(role, role.title())


def save_session(username):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({"username": username}, f)


def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("username")
    except Exception:
        return None


def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def defaults():
    return {
        "user": None,
        "email": "",
        "plan": "free",
        "tokens": 0,
        "role": "user",
        "page": "chat",
        "language": "German",
        "show_login": False,
        "memory_chat": [],
        "upgrade_message": "",
    }


for key, value in defaults().items():
    if key not in st.session_state:
        st.session_state[key] = value


def normalize_user(user):
    if not user:
        return None

    if isinstance(user, dict):
        return user

    # tuple/list aus database.py
    return {
        "username": user[0] if len(user) > 0 else "",
        "email": user[1] if len(user) > 1 else "",
        "plan": user[3] if len(user) > 3 else "free",
        "tokens": user[4] if len(user) > 4 else 0,
        "role": user[5] if len(user) > 5 else "user",
    }


def sync_user():
    if not st.session_state.user:
        return

    user = refresh_user(st.session_state.user)
    user = normalize_user(user)

    if user:
        st.session_state.email = user.get("email", "")
        st.session_state.plan = user.get("plan", "free")
        st.session_state.tokens = user.get("tokens", 0)
        st.session_state.role = user.get("role", "user")

def login_success(user):
    st.session_state.user = user["username"]
    st.session_state.email = user["email"]
    st.session_state.plan = user["plan"]
    st.session_state.tokens = user["tokens"]
    st.session_state.role = user["role"]
    st.session_state.show_login = False
    st.session_state.page = "chat"
    save_session(user["username"])


def logout():
    clear_session()
    for key, value in defaults().items():
        st.session_state[key] = value
    st.rerun()


saved = load_session()
if saved and not st.session_state.user:
    user = refresh_user(saved)
    if user:
        login_success(user)

sync_user()


def require_login():
    if not st.session_state.user:
        st.warning("Bitte zuerst einloggen.")
        st.session_state.show_login = True
        return False
    return True


def plan_rank(plan):
    ranks = {
        "free": 1,
        "pro": 2,
        "grand": 3,
        "elite": 4,
    }
    return ranks.get(plan, 1)


def can_use(required_plan):
    if st.session_state.role in ["admin", "owner"]:
        return True
    return plan_rank(st.session_state.plan) >= plan_rank(required_plan)


def can_access_admin():
    return st.session_state.role in ["supporter", "moderator", "admin", "owner"]


def can_manage_roles():
    return st.session_state.role in ["admin", "owner"]


def nav_button(label, page, required_plan="free", admin_only=False):
    locked = False

    if admin_only and not can_access_admin():
        return

    if not admin_only and not can_use(required_plan):
        locked = True

    text = label if not locked else f"🔒 {label}"

    if st.button(text, use_container_width=True, key=f"nav_{page}"):
        if locked:
            st.session_state.page = "premium"
            st.session_state.upgrade_message = f"{label} benötigt mindestens {plan_label(required_plan)}."
        else:
            st.session_state.page = page
        st.rerun()


# -------------------------------------------------
# CSS
# -------------------------------------------------
st.markdown("""
<style>
html, body, .stApp {
    background:#000 !important;
    color:#fff !important;
}

header {
    display:block !important;
    visibility:visible !important;
}

[data-testid="stSidebar"] {
    background:#07070b !important;
    border-right:1px solid rgba(255,215,0,.22) !important;
}

[data-testid="stSidebar"] * {
    color:#fff !important;
}

[data-testid="collapsedControl"] {
    display:flex !important;
    visibility:visible !important;
    opacity:1 !important;
    pointer-events:auto !important;
    z-index:999999 !important;
}

.block-container {
    max-width:1220px !important;
    padding-top:2rem !important;
}

.logo-card {
    background:#050509;
    border:1px solid rgba(255,255,255,.08);
    border-radius:22px;
    padding:16px;
    margin-bottom:22px;
}

.logo-card img {
    width:100%;
    border-radius:14px;
}

.account-box {
    background:#11111a;
    border:1px solid rgba(255,215,0,.25);
    border-radius:18px;
    padding:14px;
    margin-bottom:14px;
}

.stButton button {
    width:100%;
    background:#000 !important;
    color:#ffd700 !important;
    border:1px solid rgba(255,215,0,.55) !important;
    border-radius:14px !important;
    min-height:46px;
    font-weight:800;
}

.stButton button:hover {
    border-color:#ffd700 !important;
    box-shadow:0 0 18px rgba(255,215,0,.22);
}

.hero {
    background:linear-gradient(135deg,#06364d,#3b0b55);
    border:1px solid rgba(255,255,255,.14);
    border-radius:34px;
    padding:58px;
    margin-top:24px;
    text-align:center;
}

.hero-logo {
    width:260px;
    max-width:80%;
    margin:0 auto 28px auto;
    display:block;
    border-radius:16px;
}

.hero h1 {
    font-size:clamp(2.5rem,6vw,5rem);
    line-height:1;
    font-weight:950;
    color:white !important;
    margin-bottom:20px;
}

.hero p {
    font-size:1.2rem;
    color:#e5e7eb !important;
}

.grid {
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:18px;
    margin-top:28px;
}

.card {
    background:#11111a;
    border:1px solid rgba(255,255,255,.1);
    border-radius:24px;
    padding:24px;
    min-height:150px;
}

.card.locked {
    opacity:.65;
    border-color:rgba(255,215,0,.35);
}

.small-muted {
    color:#a1a1aa !important;
    font-size:.9rem;
}

@media(max-width:900px) {
    .grid {
        grid-template-columns:1fr;
    }
}
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    if LOGO_B64:
        st.markdown(
            f'<div class="logo-card"><img src="data:image/png;base64,{LOGO_B64}"></div>',
            unsafe_allow_html=True,
        )
    else:
        st.title("MAB.AI")

    if st.session_state.user:
        st.markdown(
            f"""
            <div class="account-box">
                <b>👤 {st.session_state.user}</b><br>
                🪙 {st.session_state.tokens} Tokens<br>
                ⭐ {plan_label(st.session_state.plan)}<br>
                🛡️ {role_label(st.session_state.role)}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Logout", use_container_width=True):
            logout()
    else:
        if st.button("Login / Register", use_container_width=True):
            st.session_state.show_login = True
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
    nav_button("User Dashboard", "dashboard", "free")
    nav_button("Support", "support", "free")
    nav_button("Buy Premium", "premium", "free")
    nav_button("Connect APIs", "connect", "free")

    if can_access_admin():
        st.markdown("### Team")
        nav_button("Admin Panel", "admin", admin_only=True)


# -------------------------------------------------
# LOGIN / REGISTER
# -------------------------------------------------
if st.session_state.show_login:
    st.title("🔐 Account")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)

        if submit:
            ok, msg, user = login_user(username, password)
            if ok:
                login_success(user)
                st.rerun()
            else:
                st.error(msg)

    with tab_register:
        with st.form("register_form"):
            username = st.text_input("Username", key="reg_user")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_pw")
            submit = st.form_submit_button("Register", use_container_width=True)

        if submit:
            ok, msg = register_user(username, email, password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.stop()


# -------------------------------------------------
# HOME / CHAT
# -------------------------------------------------
if st.session_state.page == "chat":
    if not st.session_state.memory_chat:
        logo_html = (
            f'<img class="hero-logo" src="data:image/png;base64,{LOGO_B64}">'
            if LOGO_B64 else ""
        )

        st.markdown(
            f"""
            <section class="hero">
                {logo_html}
                <h1>Was kann ich für dich tun?</h1>
                <p>Starte mit Memory Chat. Erstelle Texte, plane Projekte, sammle Ideen oder lass dir direkt helfen.</p>
            </section>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="grid">
                <div class="card"><h3>Free</h3><p>Memory Chat inklusive.</p></div>
                <div class="card locked"><h3>🔒 Pro</h3><p>Coding, Bilder, Musik und Reels.</p></div>
                <div class="card locked"><h3>🔒 Grand</h3><p>AI Video Generator.</p></div>
                <div class="card locked"><h3>🔒 Elite</h3><p>Alles freigeschaltet.</p></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if require_login():
        for role, msg in st.session_state.memory_chat:
            with st.chat_message(role):
                st.markdown(msg)

        prompt = st.chat_input("Schreib etwas...")
        if prompt:
            st.session_state.memory_chat.append(("user", prompt))
            answer, cost, ok = process_chat(
                st.session_state.user,
                prompt,
                st.session_state.language,
                st.session_state.memory_chat[:-1],
            )
            st.session_state.memory_chat.append(("assistant", answer))
            sync_user()
            st.rerun()


# -------------------------------------------------
# PRO FEATURES
# -------------------------------------------------
elif st.session_state.page == "coding":
    st.title("💻 Coding Area")
    st.caption("Pro Feature · 5 Tokens")

    if require_login() and can_use("pro"):
        task = st.text_area("Was soll ich bauen oder fixen?", height=220)
        if st.button("Run Coding Assistant"):
            answer, cost, ok = process_coding(st.session_state.user, task, st.session_state.language)
            st.markdown(answer)
            sync_user()
    else:
        st.warning("🔒 Dafür brauchst du Pro.")


elif st.session_state.page == "image":
    st.title("🎨 Image Generator")
    st.caption("Pro Feature · 15 Tokens")

    if require_login() and can_use("pro"):
        prompt = st.text_area("Was soll ich als Bild erstellen?", height=160)
        if st.button("Generate Image"):
            result, error, cost, ok = process_image(st.session_state.user, prompt)
            if ok:
                st.image(result, use_container_width=True)
                sync_user()
            else:
                st.error(error)
    else:
        st.warning("🔒 Dafür brauchst du Pro.")


elif st.session_state.page == "music":
    st.title("🎵 Music Generator")
    st.caption("Pro Feature · 18 Tokens")

    if require_login() and can_use("pro"):
        prompt = st.text_area("Welche Musik soll ich erstellen?", height=160)
        if st.button("Generate Music"):
            result, error, cost, ok = process_music(st.session_state.user, prompt)
            if ok:
                st.success(f"Cost: {cost} Tokens")
                if isinstance(result, str) and result.startswith("http"):
                    st.audio(result)
                else:
                    st.markdown(result)
                sync_user()
            else:
                st.error(error)
    else:
        st.warning("🔒 Dafür brauchst du Pro.")


elif st.session_state.page == "reels":
    st.title("🎞️ Short Reels Creator")
    st.caption("Pro Feature")

    if require_login() and can_use("pro"):
        platform = st.selectbox("Platform", ["TikTok", "Instagram Reels", "YouTube Shorts"])
        prompt = st.text_area("Was für ein Reel soll erstellt werden?", height=160)

        if st.button("Generate Reel"):
            full_prompt = f"Create a vertical 9:16 short reel for {platform}. {prompt}"
            result, error, cost, ok = process_video(st.session_state.user, full_prompt, "reels")
            if ok:
                st.success(f"Cost: {cost} Tokens")
                st.write(result)
                if isinstance(result, str) and result.startswith("http"):
                    st.video(result)
                sync_user()
            else:
                st.error(error)
    else:
        st.warning("🔒 Dafür brauchst du Pro.")


# -------------------------------------------------
# GRAND FEATURE
# -------------------------------------------------
elif st.session_state.page == "video":
    st.title("🎬 AI Video Generator")
    st.caption("Grand Feature")

    if require_login() and can_use("grand"):
        prompt = st.text_area("Was für ein Video soll erstellt werden?", height=160)
        if st.button("Generate Video"):
            result, error, cost, ok = process_video(st.session_state.user, prompt, "video")
            if ok:
                st.success(f"Cost: {cost} Tokens")
                st.write(result)
                if isinstance(result, str) and result.startswith("http"):
                    st.video(result)
                sync_user()
            else:
                st.error(error)
    else:
        st.warning("🔒 Dafür brauchst du Grand.")


# -------------------------------------------------
# ACCOUNT PAGES
# -------------------------------------------------
elif st.session_state.page == "dashboard":
    st.title("📊 User Dashboard")

    if require_login():
        sync_user()
        c1, c2, c3 = st.columns(3)
        c1.metric("Plan", plan_label(st.session_state.plan))
        c2.metric("Tokens", st.session_state.tokens)
        c3.metric("Role", role_label(st.session_state.role))

        st.markdown("## Redeem Code")
        with st.form("redeem_form"):
            code = st.text_input("Code")
            submit = st.form_submit_button("Redeem Code")

        if submit:
            ok, msg = redeem_code(st.session_state.user, code)
            if ok:
                st.success(msg)
                sync_user()
            else:
                st.error(msg)


elif st.session_state.page == "support":
    st.title("🆘 Support")
    st.caption("Schicke eine Nachricht an das MAB.AI Team.")

    if require_login():
        with st.form("support_form", clear_on_submit=True):
            category = st.selectbox("Kategorie", ["Account", "Payment", "Tokens", "AI Generation", "Bug", "Other"])
            subject = st.text_input("Betreff")
            message = st.text_area("Nachricht", height=180)
            submit = st.form_submit_button("Support Nachricht senden")

        if submit:
            ok, msg = create_support_message(
                st.session_state.user,
                st.session_state.email,
                category,
                subject,
                message,
            )
            if ok:
                st.success("Support Nachricht gesendet.")
            else:
                st.error(msg)


elif st.session_state.page == "premium":
    st.title("💳 Buy Premium")

    if st.session_state.upgrade_message:
        st.warning(st.session_state.upgrade_message)
        st.session_state.upgrade_message = ""

    if require_login():
        cols = st.columns(4)
        for col, key in zip(cols, ["free", "pro", "grand", "elite"]):
            p = PLANS[key]
            with col:
                st.markdown(
                    f"""
                    <div class="card">
                        <h3>{p["label"]}</h3>
                        <p><b>{p["price"]}</b></p>
                        <p>{p["tokens"]} Tokens</p>
                        <p>{p["description"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if key != "free":
                    if st.button(f"Buy {p['label']}", key=f"buy_{key}"):
                        url, error = create_checkout_session(st.session_state.user, key)
                        if error:
                            st.error(error)
                        else:
                            st.link_button("Open Checkout", url)


elif st.session_state.page == "connect":
    st.title("🔗 Connect APIs")
    st.info("Hier kommen später deine API-Verbindungen rein.")
    st.code("""
OPENAI_API_KEY=
STRIPE_SECRET_KEY=
REPLICATE_API_TOKEN=
RUNWAY_API_KEY=
SUNO_API_KEY=
""")


# -------------------------------------------------
# ADMIN PANEL
# -------------------------------------------------
elif st.session_state.page == "admin":
    if not can_access_admin():
        st.error("Kein Zugriff.")
        st.stop()

    st.title("🛡️ Admin Panel")

    counts = support_counts()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Support Total", counts.get("total", 0))
    c2.metric("Unread", counts.get("unread", 0))
    c3.metric("Open", counts.get("open", 0))
    c4.metric("Closed", counts.get("closed", 0))

    tabs = st.tabs(["Tickets", "Users", "Codes", "Payments"])

    with tabs[0]:
        st.subheader("🎫 Support Tickets")

        status_filter = st.selectbox("Filter", ["all", "open", "closed"])
        messages = list_support_messages(status_filter)

        if not messages:
            st.info("Keine Tickets vorhanden.")
        else:
            for msg in messages:
                mid, username, email, category, subject, body, status, is_read, created_at, updated_at = msg
                with st.expander(f"#{mid} · {subject} · {username} · {status.upper()}"):
                    st.write(f"User: {username}")
                    st.write(f"Email: {email}")
                    st.write(f"Category: {category}")
                    st.write(f"Created: {created_at}")
                    st.write(body)

                    a, b, c = st.columns(3)
                    if a.button("Mark Read", key=f"read_{mid}"):
                        set_support_read(mid, 1)
                        st.rerun()
                    if b.button("Open / Close", key=f"status_{mid}"):
                        set_support_status(mid, "closed" if status == "open" else "open")
                        st.rerun()
                    if c.button("Delete", key=f"delete_{mid}"):
                        delete_support_message(mid)
                        st.rerun()

    with tabs[1]:
        st.subheader("👥 Users")

        if not can_manage_roles():
            st.info("Nur Admin/Owner kann User verwalten.")
        else:
            rows = list_users()
            st.table(rows)

            st.markdown("### User bearbeiten")
            target = st.text_input("Username")
            new_plan = st.selectbox("Plan", ["free", "pro", "grand", "elite"])
            token_amount = st.number_input("Tokens hinzufügen", min_value=0, value=100)
            new_role = st.selectbox("Role", ["user", "supporter", "moderator", "admin"])

            c1, c2, c3 = st.columns(3)

            if c1.button("Plan setzen"):
                set_plan(target.strip().lower(), new_plan)
                st.success("Plan geändert.")

            if c2.button("Tokens hinzufügen"):
                update_tokens(target.strip().lower(), int(token_amount))
                st.success("Tokens hinzugefügt.")

            if c3.button("Role setzen"):
                set_role(target.strip().lower(), new_role)
                st.success("Role geändert.")

            if st.button("User löschen"):
                delete_user(target.strip().lower())
                st.success("User gelöscht.")

    with tabs[2]:
        st.subheader("🎟️ Redeem Codes")

        if not can_manage_roles():
            st.info("Nur Admin/Owner kann Codes erstellen.")
        else:
            with st.form("code_form"):
                code_type = st.selectbox("Code Type", ["tokens", "plan", "discount"])
                value = st.text_input("Value / Note", value="10%")
                tokens = st.number_input("Tokens", min_value=0, value=100)
                plan = st.selectbox("Plan", ["free", "pro", "grand", "elite"])
                max_uses = st.number_input("Max Uses", min_value=1, value=1)
                days = st.number_input("Valid Days", min_value=1, value=30)
                submit = st.form_submit_button("Create Code")

            if submit:
                code = create_redeem_code(code_type, value, tokens, plan, max_uses, st.session_state.user, days)
                st.success(f"Code erstellt: {code}")

            st.table(list_codes())

    with tabs[3]:
        st.subheader("💳 Payments")

        if not can_manage_roles():
            st.info("Nur Admin/Owner sieht Payments.")
        else:
            st.table(list_purchases())