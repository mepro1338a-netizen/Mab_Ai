from dotenv import load_dotenv
load_dotenv()

import base64
import json
import os
from pathlib import Path
import streamlit as st

from config import APP_NAME, APP_TAGLINE, PLANS, ROLE_LABELS, HEADER_PATH, SIDEBAR_LOGO_PATH, FAVICON_PATH
from database import (
    init_db, list_users, list_purchases, set_plan, update_tokens,
    set_role, delete_user, create_user, add_memory, load_memory,
    create_redeem_code, list_codes, redeem_code, create_support_message,
    list_support_messages, support_counts, set_support_read, set_support_status,
    update_support_note, delete_support_message, list_admin_chat, add_admin_chat
)
from auth import login_user, register_user
from backend import refresh_user, process_chat, process_coding, process_image, process_video, process_music
from payments import create_checkout_session, confirm_checkout_session

def img_b64(path: Path):
    if path and path.exists():
        return base64.b64encode(path.read_bytes()).decode("utf-8")
    return ""

FAVICON = str(FAVICON_PATH) if FAVICON_PATH.exists() else "🧠"

st.set_page_config(
    page_title=APP_NAME,
    page_icon=FAVICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

HEADER_B64 = img_b64(HEADER_PATH)
SIDEBAR_B64 = img_b64(SIDEBAR_LOGO_PATH) or HEADER_B64

SESSION_FILE = "session.json"


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


for k, v in defaults().items():
    if k not in st.session_state:
        st.session_state[k] = v


def normalize_user(user):
    if not user:
        return None
    if isinstance(user, dict):
        return user
    if isinstance(user, (tuple, list)):
        return {
            "username": user[0] if len(user) > 0 else "",
            "email": user[1] if len(user) > 1 else "",
            "plan": user[3] if len(user) > 3 else "free",
            "tokens": user[4] if len(user) > 4 else 0,
            "role": user[5] if len(user) > 5 else "user",
        }
    return None


def save_session(username):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump({"username": username}, f)


def load_session():
    try:
        if os.path.exists(SESSION_FILE):
            return json.load(open(SESSION_FILE, "r", encoding="utf-8")).get("username")
    except Exception:
        return None
    return None


def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def plan_label(plan):
    return PLANS.get(plan, PLANS["free"])["label"]


def role_label(role):
    return ROLE_LABELS.get(role, role.title())


def sync_user():
    if not st.session_state.user:
        return
    user = normalize_user(refresh_user(st.session_state.user))
    if user:
        st.session_state.email = user.get("email", "")
        st.session_state.plan = user.get("plan", "free")
        st.session_state.tokens = user.get("tokens", 0)
        st.session_state.role = user.get("role", "user")


def login_success(user):
    user = normalize_user(user)
    if not user:
        st.error("Login fehlgeschlagen.")
        return
    st.session_state.user = user.get("username", "")
    st.session_state.email = user.get("email", "")
    st.session_state.plan = user.get("plan", "free")
    st.session_state.tokens = user.get("tokens", 0)
    st.session_state.role = user.get("role", "user")
    st.session_state.show_login = False
    st.session_state.page = "chat"
    save_session(st.session_state.user)


saved = load_session()
if saved and not st.session_state.user:
    u = normalize_user(refresh_user(saved))
    if u:
        login_success(u)
sync_user()


def logout():
    clear_session()
    for k, v in defaults().items():
        st.session_state[k] = v
    st.rerun()


def require_login():
    if not st.session_state.user:
        st.session_state.show_login = True
        st.warning("Bitte zuerst einloggen.")
        return False
    return True


def plan_rank(plan):
    return {"free": 1, "pro": 2, "grand": 3, "elite": 4}.get(plan, 1)


def can_use(required_plan):
    if st.session_state.role in ["admin", "owner"]:
        return True
    return plan_rank(st.session_state.plan) >= plan_rank(required_plan)


def can_access_admin():
    return st.session_state.role in ["supporter", "moderator", "admin", "owner"]


def can_manage_roles():
    return st.session_state.role == "owner"


def set_page(page):
    st.session_state.page = page
    st.rerun()


def nav_button(label, page, required_plan="free", admin_only=False):
    if admin_only and not can_access_admin():
        return
    locked = (not admin_only) and (not can_use(required_plan))
    text = f"🔒 {label}" if locked else label
    key = f"nav_{page}_{required_plan}_{label}".replace(" ", "_").replace("/", "_").replace(".", "_")
   button_key = f"nav_{page}_{required_plan}_{label}".replace(" ", "_").replace("/", "_").replace("🔒", "")
	if st.button(text, use_container_width=True, key=button_key):
        if locked:
            st.session_state.upgrade_message = f"{label} benötigt mindestens {plan_label(required_plan)}."
            set_page("premium")
        else:
            set_page(page)


st.markdown("""
<style>
html, body, .stApp {
    background:#000 !important;
    color:#fff !important;
}

[data-testid="stHeader"] {
    background:#ffffff !important;
    height:84px !important;
    border-bottom:1px solid rgba(0,0,0,.08) !important;
}

.header-logo-fixed {
    position:fixed;
    top:10px;
    left:50%;
    transform:translateX(-50%);
    z-index:999999;
    pointer-events:none;
}

.header-logo-fixed img {
    height:62px;
    width:auto;
    max-width:320px;
    object-fit:contain;
    border-radius:12px;
}

.block-container {
    max-width:1220px !important;
    padding-top:7rem !important;
    padding-bottom:6rem !important;
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

.stButton button,
[data-testid="stFormSubmitButton"] button {
    width:100%;
    background:#000 !important;
    color:#ffd700 !important;
    border:1px solid rgba(255,215,0,.55) !important;
    border-radius:14px !important;
    min-height:46px;
    font-weight:800;
}

.stButton button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    border-color:#ffd700 !important;
    box-shadow:0 0 18px rgba(255,215,0,.22);
}

input, textarea,
.stTextInput input,
.stTextArea textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background:#000 !important;
    color:#fff !important;
    caret-color:#fff !important;
    border:1px solid rgba(255,215,0,.45) !important;
    border-radius:14px !important;
}

input::placeholder, textarea::placeholder {
    color:#999 !important;
}

[data-testid="stForm"] {
    background:#050509 !important;
    border:1px solid rgba(255,255,255,.08) !important;
    border-radius:22px !important;
    padding:24px !important;
}

.hero {
    background:linear-gradient(135deg,#06364d,#3b0b55);
    border:1px solid rgba(255,255,255,.14);
    border-radius:34px;
    padding:58px;
    margin-top:24px;
    text-align:center;
}

.hero h1 {
    font-size:clamp(2.3rem,6vw,4.9rem);
    line-height:1;
    font-weight:950;
    color:white !important;
    margin-bottom:20px;
}

.hero p {
    font-size:1.18rem;
    line-height:1.7;
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
    opacity:.68;
    border-color:rgba(255,215,0,.35);
}

.plan-card {
    background:#11111a;
    border:1px solid rgba(255,215,0,.25);
    border-radius:24px;
    padding:24px;
    min-height:280px;
}

@media(max-width:900px) {
    .grid { grid-template-columns:1fr; }
    .header-logo-fixed img { height:48px; }
}
</style>
""", unsafe_allow_html=True)

if HEADER_B64:
    st.markdown(
        f'<div class="header-logo-fixed"><img src="data:image/png;base64,{HEADER_B64}"></div>',
        unsafe_allow_html=True,
    )


# Payment success handler
query = st.query_params
if query.get("payment_success") and query.get("session_id"):
    ok, msg = confirm_checkout_session(query.get("session_id"))
    if ok:
        st.success(msg)
        sync_user()
    else:
        st.warning(msg)


with st.sidebar:
    if SIDEBAR_B64:
        st.markdown(f'<div class="logo-card"><img src="data:image/png;base64,{SIDEBAR_B64}"></div>', unsafe_allow_html=True)
    else:
        st.title(APP_NAME)

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
        if st.button("Logout", use_container_width=True, key="logout_button"):
            logout()
    else:
        if st.button("Login / Register", use_container_width=True, key="open_login"):
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

    if can_access_admin():
        st.markdown("### Team")
        nav_button("Admin Panel", "admin", admin_only=True)


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
            username = st.text_input("Username", key="reg_username")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
            submit = st.form_submit_button("Register", use_container_width=True)
        if submit:
            ok, msg = register_user(username, email, password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
    st.stop()


page = st.session_state.page

if page == "chat":
    if not st.session_state.memory_chat:
        st.markdown("""
        <section class="hero">
            <h1>Hallo, willkommen auf MAB.AI</h1>
            <p>
                Was können wir für dich tun?<br>
                Starte mit Memory Chat, erstelle Texte, plane Projekte, sammle Ideen oder lass dir direkt helfen.
                Egal ob Programmierung, Monetarisierung oder künstliche Intelligenz — in jedem Bereich können wir dir helfen.
            </p>
        </section>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="grid">
            <div class="card"><h3>Free</h3><p>Memory Chat inklusive.</p></div>
            <div class="card locked"><h3>🔒 Pro</h3><p>Coding, Bilder, Musik und Reels.</p></div>
            <div class="card locked"><h3>🔒 Grand</h3><p>AI Video Generator.</p></div>
            <div class="card locked"><h3>🔒 Elite</h3><p>Alles freigeschaltet.</p></div>
        </div>
        """, unsafe_allow_html=True)

    if require_login():
        for role, msg in st.session_state.memory_chat:
            with st.chat_message(role):
                st.markdown(msg)
        prompt = st.chat_input("Schreib etwas...")
        if prompt:
            st.session_state.memory_chat.append(("user", prompt))
            answer, cost, ok = process_chat(st.session_state.user, prompt, st.session_state.language, st.session_state.memory_chat[:-1])
            st.session_state.memory_chat.append(("assistant", answer))
            sync_user()
            st.rerun()

elif page == "coding":
    st.title("💻 Coding Area")
    st.caption("Pro Feature · 5 Tokens")
    if require_login() and can_use("pro"):
        task = st.text_area("Was soll ich bauen oder fixen?", height=220)
        if st.button("Run Coding Assistant", key="coding_run"):
            answer, cost, ok = process_coding(st.session_state.user, task, st.session_state.language)
            st.markdown(answer)
            sync_user()
    else:
        st.warning("🔒 Dafür brauchst du Pro.")

elif page == "image":
    st.title("🎨 Image Generator")
    st.caption("Pro Feature · OpenAI Image API · 15 Tokens")
    if require_login() and can_use("pro"):
        prompt = st.text_area("Was soll ich als Bild erstellen?", height=160)
        if st.button("Generate Image", key="image_run"):
            result, error, cost, ok = process_image(st.session_state.user, prompt)
            if ok:
                st.image(result, use_container_width=True)
                sync_user()
            else:
                st.error(error)
    else:
        st.warning("🔒 Dafür brauchst du Pro.")

elif page == "music":
    st.title("🎵 Music Generator")
    st.caption("Pro Feature · Replicate API · 18 Tokens")
    if require_login() and can_use("pro"):
        prompt = st.text_area("Welche Musik soll ich erstellen?", height=160)
        if st.button("Generate Music", key="music_run"):
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

elif page == "reels":
    st.title("🎞️ Short Reels Creator")
    st.caption("Pro Feature · Replicate API")
    if require_login() and can_use("pro"):
        platform = st.selectbox("Platform", ["TikTok", "Instagram Reels", "YouTube Shorts"])
        prompt = st.text_area("Was für ein Reel soll erstellt werden?", height=160)
        if st.button("Generate Reel", key="reels_run"):
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

elif page == "video":
    st.title("🎬 AI Video Generator")
    st.caption("Grand Feature · Replicate API")
    if require_login() and can_use("grand"):
        prompt = st.text_area("Was für ein Video soll erstellt werden?", height=160)
        if st.button("Generate Video", key="video_run"):
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

elif page == "dashboard":
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

        st.markdown("## Billing History")
        st.table(list_purchases(st.session_state.user))

elif page == "support":
    st.title("🆘 Support")
    if require_login():
        with st.form("support_form", clear_on_submit=True):
            category = st.selectbox("Kategorie", ["Account", "Payment", "Tokens", "AI Generation", "Bug", "Other"])
            subject = st.text_input("Betreff")
            message = st.text_area("Nachricht", height=180)
            submit = st.form_submit_button("Support Nachricht senden")
        if submit:
            ok, msg = create_support_message(st.session_state.user, st.session_state.email, category, subject, message)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

elif page == "premium":
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
                    <div class="plan-card">
                        <h2>{p["label"]}</h2>
                        <h3>{p["price"]}</h3>
                        <p><b>{p["tokens"]} Tokens</b></p>
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

elif page == "admin":
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

    tab_tickets, tab_users, tab_codes, tab_payments, tab_chat = st.tabs(["Tickets", "Users", "Codes", "Payments", "Team Chat"])

    with tab_tickets:
        status_filter = st.selectbox("Filter", ["all", "open", "closed"])
        messages = list_support_messages(status_filter)
        if not messages:
            st.info("Keine Tickets vorhanden.")
        for msg in messages:
            with st.expander(f"#{msg['id']} · {msg['subject']} · {msg['username']} · {msg['status'].upper()}"):
                st.write(f"User: {msg['username']}")
                st.write(f"Email: {msg['email']}")
                st.write(f"Category: {msg['category']}")
                st.write(f"Created: {msg['created_at']}")
                st.write(msg["message"])
                note = st.text_area("Admin Note", value=msg.get("admin_note") or "", key=f"note_{msg['id']}")
                a, b, c, d = st.columns(4)
                if a.button("Save Note", key=f"save_note_{msg['id']}"):
                    update_support_note(msg["id"], note)
                    st.rerun()
                if b.button("Mark Read", key=f"read_{msg['id']}"):
                    set_support_read(msg["id"], 1)
                    st.rerun()
                if c.button("Open/Close", key=f"status_{msg['id']}"):
                    set_support_status(msg["id"], "closed" if msg["status"] == "open" else "open")
                    st.rerun()
                if d.button("Delete", key=f"delete_{msg['id']}"):
                    delete_support_message(msg["id"])
                    st.rerun()

    with tab_users:
        st.table(list_users())
        if can_manage_roles():
            st.subheader("User verwalten")
            target = st.text_input("Username")
            new_plan = st.selectbox("Plan", ["free", "pro", "grand", "elite"])
            token_amount = st.number_input("Tokens hinzufügen", min_value=0, value=100)
            new_role = st.selectbox("Role", ["user", "supporter", "moderator", "admin", "owner"])
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("Plan setzen"):
                set_plan(target, new_plan)
                st.success("Plan geändert.")
            if c2.button("Tokens hinzufügen"):
                update_tokens(target, int(token_amount))
                st.success("Tokens hinzugefügt.")
            if c3.button("Role setzen"):
                ok, msg = set_role(target, new_role, st.session_state.role)
                st.success(msg) if ok else st.error(msg)
            if c4.button("User löschen"):
                delete_user(target)
                st.success("User gelöscht.")
        else:
            st.info("Nur Owner kann Rollen ändern.")

    with tab_codes:
        if can_manage_roles():
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
        else:
            st.info("Nur Owner/Admin kann Codes erstellen.")

    with tab_payments:
        st.table(list_purchases())

    with tab_chat:
        for row in list_admin_chat():
            st.markdown(f"**{row['role']} · {row['username']}**")
            st.write(row["message"])
            st.caption(row["created_at"])
            st.markdown("---")
        with st.form("admin_chat_form", clear_on_submit=True):
            msg = st.text_area("Team Nachricht")
            submit = st.form_submit_button("Senden")
        if submit:
            ok, msg2 = add_admin_chat(st.session_state.user, st.session_state.role, msg)
            if ok:
                st.rerun()
            else:
                st.error(msg2)
