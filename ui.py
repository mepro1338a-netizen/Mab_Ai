from dotenv import load_dotenv
load_dotenv()

import base64
import json
import os
import streamlit as st

from config import APP_NAME, APP_TAGLINE, PLANS, LOGO_PATH, ROLE_LABELS
from database import (
    init_db, list_users, list_purchases, set_plan, update_tokens,
    set_role, delete_user, create_user, add_memory, load_memory,
    create_redeem_code, list_codes, redeem_code
)
from auth import login_user, register_user
from backend import (
    refresh_user, process_chat, process_coding, process_content,
    process_script, process_reels, process_image, process_video, process_music
)
from payments import create_checkout_session

st.set_page_config(page_title=APP_NAME, page_icon="🧠", layout="wide", initial_sidebar_state="expanded")



# Sidebar uses Streamlit default behavior: desktop expanded, mobile toggleable.

SESSION_FILE = "session.json"


def logo_base64():
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


LOGO_B64 = logo_base64()


def plan_label(plan):
    return PLANS.get(plan, PLANS["free"])["label"]


def role_label(role):
    return ROLE_LABELS.get(role, role.title())

st.markdown("""
<style>
:root {--bg:#000;--panel:#0b0b10;--panel2:#15151d;--border:#282833;--gold:#ffd700;--text:#fff;--muted:#a1a1aa;}
html, body, .stApp {background:#000!important;color:#fff!important;}
#MainMenu {visibility:hidden;} footer {visibility:hidden;}
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {display:none!important;}
[data-testid="stSidebar"] {background:#07070b!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] * {color:#fff!important;}
.block-container {max-width:1180px!important;padding-top:1rem!important;padding-bottom:8rem!important;}
h1,h2,h3,h4,h5,h6,p,label,span,div {color:#fff!important;}
button,.stButton button,[data-testid="stFormSubmitButton"] button {background:#000!important;color:var(--gold)!important;border:1px solid rgba(255,215,0,.5)!important;border-radius:14px!important;font-weight:850!important;min-height:44px;}
button:hover,.stButton button:hover {border-color:var(--gold)!important;box-shadow:0 0 18px rgba(255,215,0,.18);}
input,textarea,.stTextInput input,.stTextArea textarea,[data-baseweb="input"] input,[data-baseweb="textarea"] textarea {background:#000!important;color:#fff!important;caret-color:#fff!important;border:1px solid var(--border)!important;border-radius:14px!important;}
input::placeholder,textarea::placeholder {color:#777!important;}
[data-testid="stChatInput"],[data-testid="stChatInput"] > div,[data-testid="stChatInput"] section,[data-testid="stChatInput"] div {background-color:#000!important;}
[data-testid="stChatInput"] textarea {background:#000!important;color:#fff!important;caret-color:#fff!important;border:1px solid var(--border)!important;border-radius:18px!important;}
[data-baseweb="select"] > div,[data-baseweb="popover"],[data-baseweb="menu"],ul[role="listbox"],div[role="listbox"] {background:#000!important;color:#fff!important;border:1px solid rgba(255,215,0,.45)!important;}
[data-baseweb="select"] * {color:#fff!important;} li[role="option"],div[role="option"] {background:#000!important;color:#fff!important;}
[data-testid="stChatMessage"] {background:var(--panel)!important;border:1px solid var(--border)!important;border-radius:18px!important;padding:12px!important;}
.top-navbar {position:sticky;top:0;z-index:100;height:74px;margin-bottom:28px;padding:14px 20px;background:rgba(0,0,0,.92);backdrop-filter:blur(18px);border:1px solid rgba(255,255,255,.08);border-radius:22px;display:flex;align-items:center;justify-content:space-between;}
.top-brand {display:flex;align-items:center;gap:14px;}.top-logo {height:48px;width:auto;border-radius:12px;object-fit:contain;}.brand-name {font-size:24px;font-weight:900;letter-spacing:-.04em;}.top-user {display:flex;gap:12px;align-items:center;background:#111116;border:1px solid var(--border);border-radius:999px;padding:10px 14px;font-weight:800;}
.hero {background:radial-gradient(circle at top left,rgba(0,183,255,.22),transparent 30rem),radial-gradient(circle at top right,rgba(168,85,247,.28),transparent 28rem),linear-gradient(135deg,rgba(9,40,58,.94),rgba(49,17,68,.94));border:1px solid rgba(255,255,255,.1);border-radius:34px;padding:46px;margin:16px 0 28px;box-shadow:0 30px 90px rgba(0,0,0,.4);}
.hero-logo {width:320px;max-width:80%;margin-bottom:24px;border-radius:18px;display:block;}.hero h1 {font-size:clamp(2.8rem,6vw,5.7rem);line-height:.95;letter-spacing:-.075em;margin:0 0 20px;}
.hero-title {font-size:clamp(2.7rem,5.7vw,5.4rem);line-height:.98;letter-spacing:-.075em;font-weight:950;margin:0 0 20px;}
.inline-logo {height:.95em;vertical-align:-.16em;margin:0 .18em;border-radius:10px;}.hero p {color:#dbeafe!important;font-size:1.12rem;max-width:850px;}
.grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:24px;}.card {background:rgba(21,21,29,.86);border:1px solid var(--border);border-radius:22px;padding:18px;margin-bottom:16px;}.account-box {background:var(--panel2);border:1px solid var(--border);border-radius:18px;padding:14px 16px;margin-bottom:12px;}.small-muted {color:var(--muted)!important;font-size:.92rem;}
@media(max-width:900px){.grid{grid-template-columns:1fr}.top-user{display:none}}

/* V12.1 HARD FIX: prompt area always black */
[data-testid="stChatInput"] {
    background: #000000 !important;
}
[data-testid="stChatInput"] * {
    background-color: #000000 !important;
    color: #ffffff !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus {
    background: #000000 !important;
    color: #ffffff !important;
    border: 1px solid #282833 !important;
    box-shadow: none !important;
}

/* Keep sidebar collapse/reopen usable */

[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {display:none!important;}


/* Keep Streamlit header clickable so sidebar reopen works */
header,


/* Hide only Streamlit menu/toolbar/deploy elements, not the sidebar toggle */
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],


/* Sidebar toggle/reopen button must stay visible */


/* Make collapsed sidebar button match MAB.AI theme */


[data-testid="stChatInput"] *,
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div,
[data-testid="stChatInput"] section,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] label {
    background: #000000 !important;
    background-color: #000000 !important;
    color: #ffffff !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] div[data-baseweb="base-input"],
[data-testid="stChatInput"] div[data-baseweb="input"] {
    background: #000000 !important;
    background-color: #000000 !important;
    color: #ffffff !important;
    caret-color: #ffffff !important;
    border: 1px solid #282833 !important;
    border-radius: 18px !important;
    box-shadow: none !important;
}

/* Send button black/gold */
[data-testid="stChatInput"] button {
    background: #000000 !important;
    color: #ffd700 !important;
    border: 1px solid rgba(255,215,0,.65) !important;
    border-radius: 14px !important;
}

/* Remove remaining white bottom wrapper from Streamlit */
section[data-testid="stBottomBlockContainer"],
div[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] {
    background: #000000 !important;
    background-color: #000000 !important;
}

/* Entire app bottom area black */
.main,
.block-container,
[data-testid="stAppViewContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: transparent !important;
}


/* Keep Streamlit header alive because sidebar toggle lives there */
header,


/* Hide Streamlit extras, but NEVER hide sidebar toggle */
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],


/* Sidebar reopen button */


[data-testid="stSidebar"] > div {
    padding-top: 1.2rem !important;
}

/* Sidebar text */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: #ffffff !important;
}

/* Sidebar section headings */
[data-testid="stSidebar"] h3 {
    font-size: .92rem !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    color: rgba(255,255,255,.68) !important;
    margin-top: 1.15rem !important;
    margin-bottom: .55rem !important;
}

/* Sidebar divider */
[data-testid="stSidebar"] hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(255,215,0,.22), transparent) !important;
    margin: 1.1rem 0 !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton button {
    width: 100% !important;
    background:
        linear-gradient(180deg, rgba(18,18,24,.95), rgba(0,0,0,.95)) !important;
    color: #ffd700 !important;
    border: 1px solid rgba(255,215,0,.45) !important;
    border-radius: 16px !important;
    min-height: 46px !important;
    font-size: .96rem !important;
    font-weight: 850 !important;
    letter-spacing: -.01em !important;
    transition: all .18s ease !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.04) !important;
}

[data-testid="stSidebar"] .stButton button:hover {
    transform: translateY(-1px) !important;
    border-color: rgba(255,215,0,.9) !important;
    color: #fff4a3 !important;
    box-shadow:
        0 0 22px rgba(255,215,0,.18),
        inset 0 1px 0 rgba(255,255,255,.06) !important;
}

/* Sidebar selectbox premium */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #000000 !important;
    border: 1px solid rgba(255,215,0,.38) !important;
    border-radius: 16px !important;
    min-height: 46px !important;
}

/* Sidebar logo card */
.sidebar-logo-card {
    background: rgba(255,255,255,.025);
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 22px;
    padding: 14px;
    margin-bottom: 14px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.04);
}

.sidebar-logo-card img {
    width: 100%;
    max-width: 210px;
    display: block;
    margin: 0 auto;
    border-radius: 16px;
}

/* Account card premium */
.account-box {
    background:
        radial-gradient(circle at top right, rgba(255,215,0,.12), transparent 10rem),
        linear-gradient(180deg, rgba(22,22,30,.95), rgba(9,9,12,.95)) !important;
    border: 1px solid rgba(255,215,0,.22) !important;
    border-radius: 22px !important;
    padding: 16px 18px !important;
    margin: 12px 0 14px !important;
    box-shadow:
        0 18px 50px rgba(0,0,0,.35),
        inset 0 1px 0 rgba(255,255,255,.06) !important;
}

/* Make login/register sidebar button more premium */
[data-testid="stSidebar"] button[kind="secondary"] {
    background: #000 !important;
}

/* Chat input bottom final black */
[data-testid="stChatInput"],
[data-testid="stChatInput"] *,
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] section,
[data-testid="stChatInput"] form {
    background: #000000 !important;
    background-color: #000000 !important;
    color: #ffffff !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus {
    background: #000000 !important;
    background-color: #000000 !important;
    color: #ffffff !important;
    caret-color: #ffffff !important;
    border: 1px solid #282833 !important;
    border-radius: 18px !important;
    box-shadow: none !important;
}

section[data-testid="stBottomBlockContainer"],
div[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] {
    background: #000000 !important;
    background-color: #000000 !important;
}


/* V12.6 OLD SIDEBAR RESTORED - SAFE CSS ONLY */

/* Sidebar always visible when Streamlit state is expanded */
[data-testid="stSidebar"] {
    background: #07070b !important;
    border-right: 1px solid rgba(255,215,0,.16) !important;
    box-shadow: 18px 0 60px rgba(0,0,0,.35) !important;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

[data-testid="stSidebar"] .stButton button {
    width: 100% !important;
    background: #000000 !important;
    color: #ffd700 !important;
    border: 1px solid rgba(255,215,0,.55) !important;
    border-radius: 14px !important;
    min-height: 44px !important;
    font-weight: 850 !important;
}

[data-testid="stSidebar"] .stButton button:hover {
    border-color: #ffd700 !important;
    box-shadow: 0 0 18px rgba(255,215,0,.20) !important;
}

[data-testid="stSidebar"] hr {
    border: none !important;
    height: 1px !important;
    background: rgba(255,215,0,.18) !important;
}

/* Prompt final black fix without touching sidebar/header */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] section,
[data-testid="stChatInput"] form,
section[data-testid="stBottomBlockContainer"],
div[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] {
    background: #000000 !important;
    background-color: #000000 !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] div[data-baseweb="base-input"] {
    background: #000000 !important;
    background-color: #000000 !important;
    color: #ffffff !important;
    caret-color: #ffffff !important;
    border: 1px solid #282833 !important;
    border-radius: 18px !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] button {
    background: #000000 !important;
    color: #ffd700 !important;
    border: 1px solid rgba(255,215,0,.65) !important;
}



/* V12.8 SIDEBAR BACK - SAFE OLD DESIGN */
[data-testid="stSidebar"] {
    background: #07070b !important;
    border-right: 1px solid rgba(255,215,0,.16) !important;
    min-width: 300px !important;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

[data-testid="stSidebar"] .stButton button {
    width: 100% !important;
    background: #000000 !important;
    color: #ffd700 !important;
    border: 1px solid rgba(255,215,0,.55) !important;
    border-radius: 14px !important;
    min-height: 44px !important;
    font-weight: 850 !important;
}

[data-testid="stSidebar"] .stButton button:hover {
    border-color: #ffd700 !important;
    box-shadow: 0 0 18px rgba(255,215,0,.20) !important;
}

[data-testid="stSidebar"] hr {
    border: none !important;
    height: 1px !important;
    background: rgba(255,215,0,.18) !important;
}

.sidebar-logo-card {
    background: rgba(255,255,255,.025);
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 22px;
    padding: 14px;
    margin-bottom: 14px;
}

.sidebar-logo-card img {
    width: 100%;
    max-width: 210px;
    display: block;
    margin: 0 auto;
    border-radius: 16px;
}

.account-box {
    background: #15151d !important;
    border: 1px solid rgba(255,215,0,.22) !important;
    border-radius: 18px !important;
    padding: 14px 16px !important;
    margin-bottom: 12px !important;
}

/* Prompt stays black, but no sidebar/header manipulation */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] section,
[data-testid="stChatInput"] form,
section[data-testid="stBottomBlockContainer"],
div[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] {
    background: #000000 !important;
    background-color: #000000 !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] div[data-baseweb="base-input"] {
    background: #000000 !important;
    background-color: #000000 !important;
    color: #ffffff !important;
    caret-color: #ffffff !important;
    border: 1px solid #282833 !important;
    border-radius: 18px !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] button {
    background: #000000 !important;
    color: #ffd700 !important;
    border: 1px solid rgba(255,215,0,.65) !important;
}


/* FINAL SIDEBAR FIX - desktop open, mobile collapsible/reopenable */
.top-navbar.no-brand {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    height: 54px !important;
    margin-bottom: 8px !important;
    padding: 6px 20px !important;
}

/* Desktop sidebar: stable premium width */
[data-testid="stSidebar"] {
    background: #07070b !important;
    border-right: 1px solid rgba(255,215,0,.16) !important;
    box-shadow: 18px 0 60px rgba(0,0,0,.35) !important;
    min-width: 310px !important;
    width: 310px !important;
}

[data-testid="stSidebar"] > div {
    width: 310px !important;
    padding-top: 1.2rem !important;
}

/* IMPORTANT: Never hide Streamlit sidebar controls */
[data-testid="stSidebarCollapseButton"],
button[title="Close sidebar"],
button[aria-label="Close sidebar"],
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    z-index: 999999 !important;
}

/* Style the reopen button instead of hiding it */
[data-testid="collapsedControl"] button {
    background: #000000 !important;
    color: #ffd700 !important;
    border: 1px solid rgba(255,215,0,.55) !important;
    border-radius: 12px !important;
}

/* Mobile: allow Streamlit's native drawer behavior */
@media (max-width: 900px) {
    [data-testid="stSidebar"] {
        min-width: min(88vw, 320px) !important;
        width: min(88vw, 320px) !important;
        max-width: 88vw !important;
    }

    [data-testid="stSidebar"] > div {
        width: min(88vw, 320px) !important;
        max-width: 88vw !important;
    }

    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .hero {
        padding: 28px !important;
        border-radius: 26px !important;
    }
}

/* Black prompt whenever visible */
[data-testid="stChatInput"],
[data-testid="stChatInput"] *,
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] section,
[data-testid="stChatInput"] form,
section[data-testid="stBottomBlockContainer"],
div[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] {
    background: #000000 !important;
    background-color: #000000 !important;
    color: #ffffff !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus {
    background: #000000 !important;
    background-color: #000000 !important;
    color: #ffffff !important;
    caret-color: #ffffff !important;
    border: 1px solid #282833 !important;
    border-radius: 18px !important;
    box-shadow: none !important;
}

</style>
""", unsafe_allow_html=True)


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
    return {"user":None,"email":"","plan":"free","tokens":0,"role":"user","page":"chat","show_login":False,"language":"German","upgrade_message":"","memory_chat":[]}


init_db()
for key, value in defaults().items():
    if key not in st.session_state:
        st.session_state[key] = value

# V13.1 safety: older browser/session states may not have this key yet
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False


def sync_user():
    if not st.session_state.user:
        return
    user = refresh_user(st.session_state.user)
    if user:
        st.session_state.email = user["email"]; st.session_state.plan = user["plan"]; st.session_state.tokens = user["tokens"]; st.session_state.role = user["role"]


def login_success(user):
    st.session_state.user = user["username"]; st.session_state.email = user["email"]; st.session_state.plan = user["plan"]; st.session_state.tokens = user["tokens"]; st.session_state.role = user["role"]
    st.session_state.show_login = False; st.session_state.page = "chat"; st.session_state.memory_chat = []
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
        st.warning("Please login first.")
        st.session_state.show_login = True
        return False
    return True


def can_open_page(page):
    if page in ["chat","dashboard","premium","connect"]:
        return True
    if st.session_state.role == "admin":
        return True
    features = PLANS.get(st.session_state.plan, PLANS["free"])["features"]
    return "all" in features or page in features


def nav_button(label, page):
    locked = not can_open_page(page)
    text = label if not locked else f"🔒 {label}"
    if st.button(text, use_container_width=True, key=f"nav_{page}"):
        st.session_state.show_login = False
        if locked:
            st.session_state.page = "premium"; st.session_state.upgrade_message = f"{label} requires a higher plan."
        else:
            st.session_state.page = page
            if page == "chat":
                st.session_state.chat_started = True
        st.rerun()


def render_logo():
    if LOGO_B64:
        st.markdown(
            f'<div class="sidebar-logo-card"><img src="data:image/png;base64,{LOGO_B64}"></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown("## MAB.AI")


def premium_navbar():
    user_html = "Guest"
    if st.session_state.user:
        user_html = f"👤 {st.session_state.user} &nbsp; 🪙 {st.session_state.tokens} &nbsp; ⭐ {plan_label(st.session_state.plan)}"
    st.markdown(f'<div class="top-navbar no-brand"><div></div><div class="top-user">{user_html}</div></div>', unsafe_allow_html=True)


with st.sidebar:
    render_logo()
    st.markdown('<div class="small-muted" style="text-align:center;line-height:1.5;">AI workspace for creators,<br>coders and businesses.</div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.session_state.user:
        st.markdown(f'<div class="account-box"><b>👤 {st.session_state.user}</b><br>🪙 {st.session_state.tokens} tokens<br>⭐ {plan_label(st.session_state.plan)}<br>🛡️ {role_label(st.session_state.role)}</div>', unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True, key="logout_btn"):
            logout()
    else:
        if st.button("Login / Register", use_container_width=True, key="login_open_btn"):
            st.session_state.show_login = True; st.rerun()
    st.markdown("---")
    st.session_state.language = st.selectbox("Language", ["German","English","Spanish","French","Italian","Turkish","Arabic"], key="language_select")
    st.markdown("---")
    st.markdown("### Free"); nav_button("Memory Chat", "chat")
    st.markdown("### Pro"); nav_button("Coding Area", "coding"); nav_button("Image Generator", "image"); nav_button("Music Generator", "music"); nav_button("Short Reels Creator", "reels"); 
    st.markdown("### Grand"); nav_button("AI Video Generator", "video")
    st.markdown("### Account"); nav_button("User Dashboard", "dashboard"); nav_button("Support", "support"); nav_button("Buy Premium", "premium"); nav_button("Connect with", "connect")
    if st.session_state.role in ("admin", "moderator"):
        st.markdown("### Team"); nav_button("Admin Panel", "admin")

premium_navbar()

if st.session_state.show_login:
    st.markdown("# 🔐 Account")
    tab_login, tab_register = st.tabs(["Login", "Register"])
    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            login_clicked = st.form_submit_button("Login", use_container_width=True)
        if login_clicked:
            ok, msg, user = login_user(username, password)
            if ok:
                login_success(user); st.rerun()
            else:
                st.error(msg)
    with tab_register:
        with st.form("register_form", clear_on_submit=False):
            username = st.text_input("Username", key="register_username")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            register_clicked = st.form_submit_button("Register", use_container_width=True)
        if register_clicked:
            ok, msg = register_user(username, email, password)
            if ok: st.success(msg)
            else: st.error(msg)
    st.stop()

if st.session_state.page == "chat":
    if not st.session_state.memory_chat:
        inline_logo = f'<img src="data:image/png;base64,{LOGO_B64}" class="inline-logo">' if LOGO_B64 else "MAB.AI"
        st.markdown(f'<section class="hero"><div class="hero-title">Was kann {inline_logo} für dich tun?</div><p>Starte mit Memory Chat. Erstelle Texte, plane Projekte, sammle Ideen oder lass dir direkt helfen.</p><div class="grid"><div class="card"><b>Free</b><br>Memory Chat inklusive.</div><div class="card"><b>Pro</b><br>Coding, Bilder, Musik und Video-Reels.</div><div class="card"><b>Grand</b><br>AI Video Generator.</div><div class="card"><b>Elite</b><br>Alles freigeschaltet. Best API runs.</div></div></section>', unsafe_allow_html=True)

    if require_login():
        if not st.session_state.chat_started and not st.session_state.memory_chat:
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                if st.button("Start Memory Chat", key="start_memory_chat_btn", use_container_width=True):
                    st.session_state.chat_started = True
                    st.rerun()
            st.stop()

        for role, msg in st.session_state.memory_chat:
            with st.chat_message(role):
                st.markdown(msg)

        prompt = st.chat_input("Write something...")
        if prompt:
            st.session_state.memory_chat.append(("user", prompt))
            answer, cost, ok = process_chat(st.session_state.user, prompt, st.session_state.language, st.session_state.memory_chat[:-1])
            st.session_state.memory_chat.append(("assistant", answer))
            if ok:
                sync_user()
            st.rerun()

elif st.session_state.page == "coding":
    st.markdown("# 💻 Coding Area"); st.caption("Available from Pro. Cost: 5 tokens.")
    if require_login():
        task = st.text_area("What should I build or fix?", key="coding_task", height=220)
        if st.button("Run Coding Assistant", key="coding_btn", use_container_width=True):
            answer, cost, ok = process_coding(st.session_state.user, task, st.session_state.language)
            st.markdown(answer)
            if ok: st.success(f"Cost: {cost} tokens"); sync_user()

elif st.session_state.page == "image":
    st.markdown("# 🎨 Image Generator"); st.caption("Available from Pro. Cost: 15 tokens.")
    if require_login():
        prompt = st.text_area("What image should I create?", key="image_prompt", height=140)
        if st.button("Generate Image", key="image_btn", use_container_width=True):
            result, error, cost, ok = process_image(st.session_state.user, prompt)
            if ok: st.image(result, use_container_width=True); st.success(f"Cost: {cost} tokens"); sync_user()
            else: st.error(error)


elif st.session_state.page == "music":
    st.markdown("# 🎵 Music Generator")
    st.caption("Available from Pro. Cost: 18 tokens.")
    if require_login():
        prompt = st.text_area("What music should I create?", key="music_prompt", height=140, placeholder="Example: emotional trap beat, 90 BPM, dark piano, catchy hook...")
        if st.button("Generate Music", key="music_btn", use_container_width=True):
            result, error, cost, ok = process_music(st.session_state.user, prompt)
            if ok:
                st.success(f"Cost: {cost} tokens")
                if isinstance(result, str) and result.startswith("http"):
                    st.audio(result)
                    st.write(result)
                else:
                    st.markdown(result)
                sync_user()
            else:
                st.error(error)



elif st.session_state.page == "reels":
    st.markdown("# 🎞️ Short Reels Creator")
    st.caption("Available from Pro. Creates short AI video reels. Cost: 220 tokens.")

    if require_login():
        platform = st.selectbox("Platform", ["TikTok", "Instagram Reels", "YouTube Shorts"], key="reels_platform")
        prompt = st.text_area(
            "What short reel should I create?",
            key="reels_video_prompt",
            height=140,
            placeholder="Example: luxury product ad, 9:16, fast cuts, neon light, viral style..."
        )

        if st.button("Generate Short Reel Video", key="reels_video_btn", use_container_width=True):
            full_prompt = f"Create a short vertical 9:16 video reel for {platform}. {prompt}"
            result, error, cost, ok = process_video(st.session_state.user, full_prompt, "reels")
            if ok:
                st.success(f"Cost: {cost} tokens")
                st.write(result)
                if isinstance(result, str) and result.startswith("http"):
                    st.video(result)
                sync_user()
            else:
                st.error(error)



elif st.session_state.page == "video":
    st.markdown("# 🎬 AI Video Generator")
    st.caption("Available from Grand. Token-safe pricing for profit.")

    if require_login():
        st.markdown("### Choose video mode")
        mode = st.selectbox(
            "Video mode",
            list(VIDEO_MODES.keys()),
            key="video_mode",
            format_func=lambda x: f"{x} — {VIDEO_MODES[x]['cost']} tokens · {VIDEO_MODES[x]['seconds']} · {VIDEO_MODES[x]['quality']}"
        )

        mode_info = VIDEO_MODES[mode]
        st.info(f"Cost: {mode_info['cost']} tokens | Duration: {mode_info['seconds']} | {mode_info['margin_note']}")

        prompt = st.text_area(
            "What video should I create?",
            key="video_prompt",
            height=140,
            placeholder="Example: cinematic product ad, neon lighting, luxury mood, 6 seconds..."
        )

        if st.button("Generate AI Video", key="video_btn", use_container_width=True):
            mode_key = "video_" + mode.lower()
            result, error, cost, ok = process_video(st.session_state.user, prompt, mode_key)
            if ok:
                st.success(f"Cost: {cost} tokens")
                st.write(result)
                if isinstance(result, str) and result.startswith("http"):
                    st.video(result)
                sync_user()
            else:
                st.error(error)


elif st.session_state.page == "connect":
    st.markdown("# 🔗 Connect with")
    st.markdown('<div class="grid"><div class="card"><b>Google Docs</b>Documents and summaries.</div><div class="card"><b>Notion</b>Knowledge base assistant.</div><div class="card"><b>Email</b>Drafts and replies.</div><div class="card"><b>Shopify</b>Product and store automation.</div><div class="card"><b>Websites</b>Website summaries.</div><div class="card"><b>APIs</b>Connect your own tools.</div></div>', unsafe_allow_html=True)


elif st.session_state.page == "support":
    st.markdown("# 🆘 Support")
    st.caption("Send a message to the MAB.AI team.")

    if require_login():
        with st.form("support_form", clear_on_submit=True):
            category = st.selectbox("Category", ["Account", "Payment", "Tokens", "AI Generation", "Bug", "Other"], key="support_category")
            subject = st.text_input("Subject", key="support_subject")
            message = st.text_area("Message", key="support_message", height=180)
            send_support = st.form_submit_button("Send Support Message", use_container_width=True)

        if send_support:
            ok, msg = create_support_message(
                st.session_state.user,
                st.session_state.email,
                category,
                subject,
                message,
            )
            if ok:
                st.success(msg)
            else:
                st.error(msg)


elif st.session_state.page == "dashboard":
    st.markdown("# 📊 User Dashboard")
    if require_login():
        sync_user()
        c1,c2,c3 = st.columns(3); c1.metric("Plan", plan_label(st.session_state.plan)); c2.metric("Tokens", st.session_state.tokens); c3.metric("Role", role_label(st.session_state.role))
        st.markdown("## Redeem Code")
        with st.form("redeem_form"):
            code = st.text_input("Enter admin code", key="redeem_code_input")
            redeem_clicked = st.form_submit_button("Redeem Code", use_container_width=True)
        if redeem_clicked:
            ok, msg = redeem_code(st.session_state.user, code)
            if ok:
                st.success(msg); sync_user()
            else:
                st.error(msg)
        st.markdown("## Billing History")
        purchases = list_purchases(st.session_state.user)
        if not purchases: st.info("No purchases yet.")
        else: st.table([{"User":r[0],"Plan":plan_label(r[1]),"Stripe Session":r[2],"Status":r[3],"Created At":r[4]} for r in purchases])
        st.markdown("## Memory")
        key = st.text_input("Memory key", key="memory_key"); value = st.text_area("Memory value", key="memory_value")
        if st.button("Save Memory", key="memory_save_btn", use_container_width=True): add_memory(st.session_state.user, key, value); st.success("Memory saved.")
        st.write(load_memory(st.session_state.user))

elif st.session_state.page == "premium":
    st.markdown("# 💳 Buy Premium")
    st.caption("All premium packages are valid for 1 Month.")
    if st.session_state.get("upgrade_message"): st.warning(st.session_state.upgrade_message); st.session_state.upgrade_message = ""
    if require_login():
        cols = st.columns(4)
        for col, plan_key in zip(cols, ["free","pro","grand","elite"]):
            p = PLANS[plan_key]
            with col:
                st.markdown(f'<div class="card"><h3>{p["label"]}</h3><p><b>{p["price"]}</b> / 1 Month</p><p>{p["tokens"]} tokens</p><p>{p["description"]}</p></div>', unsafe_allow_html=True)
                if plan_key != "free":
                    if st.button(f"Buy {p['label']}", key=f"buy_{plan_key}", use_container_width=True):
                        url, error = create_checkout_session(st.session_state.user, plan_key)
                        if error: st.error(error); st.info("Add Stripe keys and price IDs in .env.")
                        else: st.link_button("Open Checkout", url, use_container_width=True)

        st.markdown("## Extra Token Packs")
        st.caption("Users can buy extra tokens anytime. This increases your margin because high-cost features consume more tokens.")

        pack_cols = st.columns(3)
        for col, pack_key in zip(pack_cols, ["small", "creator", "video"]):
            pack = TOKEN_PACKS[pack_key]
            with col:
                st.markdown(
                    f'<div class="card"><h3>{pack["label"]}</h3><p><b>{pack["price"]}</b></p><p>{pack["tokens"]} extra tokens</p><p>{pack["description"]}</p></div>',
                    unsafe_allow_html=True,
                )
                if st.button(f"Buy {pack['tokens']} Tokens", key=f"buy_pack_{pack_key}", use_container_width=True):
                    st.info("Stripe token-pack checkout can be connected here. For now Admin can grant tokens manually or with redeem codes.")

elif st.session_state.page == "admin":
    if st.session_state.role not in ("admin", "moderator"):
        st.error("No access.")
        st.stop()

    counts = support_counts()

    st.markdown("# 🛡️ Admin Panel")
    st.caption("Admin has full rights. Moderator can manage users, tokens and plans. Code creation and payment history are Admin-only.")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Support Total", counts["total"])
    m2.metric("Unread", counts["unread"])
    m3.metric("Open", counts["open"])
    m4.metric("Closed", counts["closed"])

    tab_users, tab_support, tab_team_chat, tab_codes, tab_payments = st.tabs(
        ["Accounts", f"Report / Support ({counts['unread']} unread)", "Admin Team Chat", "Codes", "Payment History"]
    )

    with tab_users:
        st.markdown("## Accounts")
        rows = list_users()
        st.table([
            {
                "Online": "🟢" if r[11] and (__import__("time").time() - r[11] < 300) else "⚫",
                "Username": r[0],
                "Email": r[1],
                "Verified": "✅" if r[9] else "❌",
                "IP": r[10] or "unknown",
                "Last Seen": r[11],
                "Plan": plan_label(r[2]),
                "Tokens": r[3],
                "Role": role_label(r[4]),
                "Images": r[5],
                "Videos": r[6],
                "Content": r[7],
                "Music": r[8],
            }
            for r in rows
        ])

        st.markdown("## Manage Account")
        col_a, col_b = st.columns(2)
        with col_a:
            target = st.text_input("Username", key="admin_target")
            plan = st.selectbox("Change account plan / tier", ["free", "pro", "grand", "elite"], format_func=plan_label, key="admin_plan")
            tokens = st.number_input("Add tokens", min_value=0, max_value=100000, value=100, key="admin_tokens")
        with col_b:
            roles = ["user", "moderator"] if st.session_state.role == "moderator" else ["user", "moderator", "admin"]
            role = st.selectbox("Change rights / role", roles, format_func=role_label, key="admin_role")
            st.info("Plans = Free / Pro / Grand / Elite. Roles = User / Moderator / Admin.")

        c1, c2, c3, c4 = st.columns(4)
        if c1.button("Update Plan / Tier", use_container_width=True):
            if target:
                set_plan(target.strip().lower(), plan)
                st.success("Plan / tier updated.")
        if c2.button("Add Tokens", use_container_width=True):
            if target:
                update_tokens(target.strip().lower(), int(tokens))
                st.success("Tokens added.")
        if c3.button("Update Role", use_container_width=True):
            if target:
                if st.session_state.role == "moderator" and role == "admin":
                    st.error("Moderators cannot create Admins.")
                else:
                    set_role(target.strip().lower(), role)
                    st.success("Role updated.")
        if c4.button("Delete User", use_container_width=True):
            if target:
                ok = delete_user(target.strip().lower())
                if ok:
                    st.success("User deleted.")
                else:
                    st.error("Cannot delete this user.")

        st.markdown("## Create Account")
        with st.form("admin_create_user"):
            new_user = st.text_input("New username")
            new_email = st.text_input("New email")
            new_password = st.text_input("New password", type="password")
            new_plan = st.selectbox("Plan", ["free", "pro", "grand", "elite"], format_func=plan_label)
            role_options = ["user", "moderator"] if st.session_state.role == "moderator" else ["user", "moderator", "admin"]
            new_role = st.selectbox("Role", role_options, format_func=role_label)
            create_clicked = st.form_submit_button("Create Account", use_container_width=True)

        if create_clicked:
            ok, msg = create_user(new_user, new_email, new_password, role=new_role, plan=new_plan)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    with tab_support:
        st.markdown("## Report / Support Inbox")
        status_filter = st.selectbox("Filter", ["all", "open", "closed"], key="support_filter")
        messages = list_support_messages(status_filter)

        if not messages:
            st.info("No support messages.")
        else:
            for msg in messages:
                mid, username, email, category, subject, body, status, is_read, created_at, updated_at = msg
                badge = "Unread" if not is_read else "Read"
                title = f"#{mid} · {subject} · {username} · {category} · {status.upper()} · {badge}"

                with st.expander(title, expanded=(not is_read)):
                    st.markdown(f"**User:** {username}")
                    st.markdown(f"**Email:** {email}")
                    st.markdown(f"**Category:** {category}")
                    st.markdown(f"**Created:** {created_at}")
                    st.markdown("**Message:**")
                    st.write(body)

                    a, b, c, d = st.columns(4)
                    if a.button("Mark Read", key=f"read_{mid}", use_container_width=True):
                        set_support_read(mid, 1)
                        st.rerun()
                    if b.button("Mark Unread", key=f"unread_{mid}", use_container_width=True):
                        set_support_read(mid, 0)
                        st.rerun()
                    if c.button("Open/Close", key=f"toggle_status_{mid}", use_container_width=True):
                        set_support_status(mid, "closed" if status == "open" else "open")
                        st.rerun()
                    if d.button("Delete", key=f"delete_support_{mid}", use_container_width=True):
                        delete_support_message(mid)
                        st.rerun()

    with tab_team_chat:
        st.markdown("## Admin Team Chat")
        st.caption("Internal chat for Admins and Moderators.")

        chat_rows = list_admin_chat(80)
        for username, role, message, created_at in chat_rows:
            st.markdown(f"**{role_label(role)} · {username}**")
            st.write(message)
            st.caption(str(created_at))
            st.markdown("---")

        with st.form("admin_team_chat_form", clear_on_submit=True):
            admin_msg = st.text_area("Write team message", height=120)
            send_admin_msg = st.form_submit_button("Send Team Message", use_container_width=True)

        if send_admin_msg:
            ok, msg = add_admin_chat(st.session_state.user, st.session_state.role, admin_msg)
            if ok:
                st.success("Message sent.")
                st.rerun()
            else:
                st.error(msg)

    with tab_codes:
        if st.session_state.role != "admin":
            st.info("Only Admin accounts can create or view redeem codes.")
        else:
            st.markdown("## Create Redeem Code")
            with st.form("create_code_form"):
                code_type = st.selectbox("Code type", ["tokens", "plan", "discount"])
                value = st.text_input("Discount value / note", value="10%")
                code_tokens = st.number_input("Tokens", min_value=0, max_value=100000, value=100)
                code_plan = st.selectbox("Plan for plan-code", ["free", "pro", "grand", "elite"], format_func=plan_label)
                max_uses = st.number_input("Max uses", min_value=1, max_value=10000, value=1)
                days_valid = st.number_input("Valid days", min_value=1, max_value=365, value=30)
                create_code_clicked = st.form_submit_button("Create Code", use_container_width=True)

            if create_code_clicked:
                code = create_redeem_code(code_type, value, code_tokens, code_plan, max_uses, st.session_state.user, days_valid)
                st.success(f"Code created: {code}")

            st.markdown("## All Redeem Codes")
            codes = list_codes()
            if not codes:
                st.info("No codes created yet.")
            else:
                st.table([
                    {
                        "Code": r[0],
                        "Type": r[1],
                        "Value": r[2],
                        "Tokens": r[3],
                        "Plan": plan_label(r[4]) if r[4] else "",
                        "Max Uses": r[5],
                        "Used": r[6],
                        "Created By": r[7],
                        "Created At": r[8],
                        "Expires At": r[9],
                        "Active": bool(r[10]),
                    }
                    for r in codes
                ])

    with tab_payments:
        if st.session_state.role != "admin":
            st.info("Payment history is Admin-only.")
        else:
            st.markdown("## Complete Payment History")
            all_purchases = list_purchases()
            if not all_purchases:
                st.info("No payments yet.")
            else:
                st.table([
                    {
                        "Username": r[0],
                        "Plan": plan_label(r[1]) if r[1] else "",
                        "Stripe Session": r[2],
                        "Status": r[3],
                        "Created At": r[4],
                    }
                    for r in all_purchases
                ])
