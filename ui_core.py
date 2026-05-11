import streamlit as st


# =========================================================
# GLOBAL UI
# =========================================================

def load_global_styles():

    logged_in = st.session_state.get("logged_in", False)

    sidebar_css = ""

    # Sidebar NUR vor Login verstecken
    if not logged_in:
        sidebar_css = """
        [data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="collapsedControl"] {
            display: none;
        }
        """

    st.markdown(
        f"""
<style>

/* =========================
   GLOBAL
========================= */

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background:
        radial-gradient(circle at top, rgba(56,189,248,.10), transparent 30%),
        linear-gradient(180deg, #020617 0%, #071127 100%);
    color: white;
}}

.block-container {{
    padding-top: 1rem;
    max-width: 1350px;
}}

{sidebar_css}

/* =========================
   SIDEBAR
========================= */

[data-testid="stSidebar"] {{
    background: linear-gradient(
        180deg,
        rgba(4,12,28,.98),
        rgba(7,25,55,.98)
    );
    border-right: 1px solid rgba(125,211,252,.12);
}}

[data-testid="stSidebar"] * {{
    color: white !important;
}}

/* =========================
   BUTTONS
========================= */

.stButton > button {{
    width: 100%;
    border: none;
    border-radius: 18px;
    padding: 14px;
    font-weight: 800;
    font-size: 15px;
    color: white;
    background: linear-gradient(
        90deg,
        #2563eb,
        #22d3ee
    );
    box-shadow: 0 0 25px rgba(34,211,238,.25);
    transition: .2s ease;
}}

.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 0 35px rgba(34,211,238,.40);
}}

/* =========================
   INPUTS
========================= */

.stTextInput input,
.stTextArea textarea {{
    border-radius: 18px !important;
    border: 1px solid rgba(125,211,252,.25) !important;
    background: rgba(15,23,42,.92) !important;
    color: white !important;
    padding: 14px !important;
    font-size: 16px !important;
}}

.stTextInput input:focus,
.stTextArea textarea:focus {{
    border: 1px solid #38bdf8 !important;
    box-shadow: 0 0 20px rgba(56,189,248,.25);
}}

/* =========================
   TABS
========================= */

.stTabs [data-baseweb="tab"] {{
    border-radius: 16px;
    padding: 10px 24px;
    background: rgba(15,23,42,.90);
    color: white;
    font-weight: 800;
}}

.stTabs [aria-selected="true"] {{
    background: linear-gradient(
        90deg,
        #2563eb,
        #22d3ee
    ) !important;
}}

/* =========================
   CARDS
========================= */

.glass-card {{
    background: linear-gradient(
        145deg,
        rgba(8,15,35,.98),
        rgba(10,35,75,.92)
    );

    border: 1px solid rgba(125,211,252,.15);

    border-radius: 28px;

    padding: 28px;

    box-shadow: 0 0 35px rgba(56,189,248,.12);
}}

</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# LOGIN CHECK
# =========================================================

def require_login():

    if not st.session_state.get("logged_in"):
        st.switch_page("pages/auth.py")