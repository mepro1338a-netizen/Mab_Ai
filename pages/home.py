import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MaByte",
    page_icon="🧠",
    layout="wide",
)


# =========================================================
# CSS
# =========================================================

def home_css() -> None:
    st.markdown(
        """
<style>

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(59,130,246,.12), transparent 28%),
        radial-gradient(circle at top right, rgba(168,85,247,.10), transparent 26%),
        linear-gradient(180deg, #071120 0%, #081426 38%, #09111d 100%);
}

/* remove streamlit spacing */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1380px !important;
}

/* =========================================================
HEADER
========================================================= */

.mb-hero {

    background:
        radial-gradient(circle at top right, rgba(168,85,247,.18), transparent 32%),
        radial-gradient(circle at top left, rgba(59,130,246,.16), transparent 34%),
        linear-gradient(135deg, rgba(10,22,45,.96), rgba(7,12,24,.98));

    border: 1px solid rgba(96,165,250,.18);

    border-radius: 30px;

    padding: 38px;

    margin-bottom: 28px;

    box-shadow:
        0 0 40px rgba(59,130,246,.08),
        0 24px 60px rgba(0,0,0,.34);
}

.mb-kicker {
    color: #c084fc;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: .22em;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.mb-title {
    color: #ffe7a3;
    font-size: 62px;
    line-height: .95;
    font-weight: 1000;
    letter-spacing: -2px;
}

.mb-subtitle {
    margin-top: 16px;
    max-width: 760px;
    color: #cbd5e1;
    font-size: 17px;
    line-height: 1.6;
}

.mb-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    padding: 10px 18px;

    border-radius: 999px;

    background:
        linear-gradient(135deg, #7c3aed, #a855f7);

    color: white;
    font-size: 13px;
    font-weight: 900;

    box-shadow:
        0 0 25px rgba(168,85,247,.32);

    margin-left: 16px;
}

/* =========================================================
CARDS
========================================================= */

.mb-card {

    background:
        radial-gradient(circle at top left, rgba(59,130,246,.06), transparent 30%),
        linear-gradient(145deg, rgba(9,19,36,.96), rgba(7,11,22,.98));

    border: 1px solid rgba(96,165,250,.10);

    border-radius: 26px;

    padding: 28px;

    min-height: 250px;

    box-shadow:
        0 14px 34px rgba(0,0,0,.24);

    transition: all .2s ease;
}

.mb-card:hover {

    transform: translateY(-4px);

    border-color: rgba(96,165,250,.24);

    box-shadow:
        0 0 30px rgba(59,130,246,.12),
        0 16px 42px rgba(0,0,0,.26);
}

.mb-icon {

    width: 58px;
    height: 58px;

    border-radius: 18px;

    display: flex;
    align-items: center;
    justify-content: center;

    background:
        linear-gradient(135deg, rgba(59,130,246,.18), rgba(168,85,247,.18));

    border: 1px solid rgba(255,255,255,.08);

    margin-bottom: 18px;

    color: #ffe7a3;

    font-size: 26px;
    font-weight: 900;
}

.mb-card-title {
    color: white;
    font-size: 20px;
    font-weight: 900;
    margin-bottom: 8px;
}

.mb-card-sub {
    color: #94a3b8;
    font-size: 14px;
    line-height: 1.5;
}

/* =========================================================
BUTTONS
========================================================= */

.stButton > button {

    width: 100%;

    height: 48px;

    border-radius: 16px;

    background:
        linear-gradient(135deg, rgba(29,78,216,.22), rgba(91,33,182,.22));

    border: 1px solid rgba(96,165,250,.20);

    color: white;

    font-size: 15px;

    font-weight: 900;

    transition: all .2s ease;

    box-shadow:
        0 12px 24px rgba(0,0,0,.18);

    backdrop-filter: blur(10px);
}

.stButton > button:hover {

    transform: translateY(-2px);

    border-color: rgba(255,255,255,.22);

    background:
        linear-gradient(135deg, rgba(59,130,246,.30), rgba(168,85,247,.28));

    box-shadow:
        0 0 24px rgba(59,130,246,.18);
}

/* =========================================================
METRICS
========================================================= */

[data-testid="metric-container"] {

    background:
        linear-gradient(145deg, rgba(9,19,36,.96), rgba(7,11,22,.98));

    border: 1px solid rgba(96,165,250,.10);

    border-radius: 24px;

    padding: 22px;

    box-shadow:
        0 14px 34px rgba(0,0,0,.22);
}

[data-testid="metric-container"] label {

    color: #60a5fa !important;

    font-size: 11px !important;

    font-weight: 1000 !important;

    letter-spacing: .16em !important;

    text-transform: uppercase !important;
}

[data-testid="metric-container"] div {

    color: #ffe7a3 !important;

    font-weight: 1000 !important;
}

/* =========================================================
SECTION TITLES
========================================================= */

.mb-section-title {
    color: #ffe7a3;
    font-size: 24px;
    font-weight: 1000;
    margin-bottom: 14px;
}

.mb-muted {
    color: #94a3b8;
    font-size: 14px;
}

/* =========================================================
ACTIVITY
========================================================= */

.mb-activity {

    background:
        linear-gradient(145deg, rgba(9,19,36,.96), rgba(7,11,22,.98));

    border: 1px solid rgba(96,165,250,.10);

    border-radius: 20px;

    padding: 18px;

    margin-bottom: 14px;
}

.mb-activity-title {
    color: white;
    font-size: 15px;
    font-weight: 900;
}

.mb-activity-sub {
    color: #94a3b8;
    font-size: 13px;
}

/* =========================================================
RESPONSIVE
========================================================= */

@media(max-width: 1100px) {

    .mb-title {
        font-size: 42px;
    }

    .mb-card {
        min-height: auto;
    }
}

</style>
""",
        unsafe_allow_html=True,
    )


# =========================================================
# START
# =========================================================

home_css()


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
<div class="mb-hero">

    <div class="mb-kicker">
        AI OPERATING SYSTEM
    </div>

    <div class="mb-title">
        MaByte Intelligence
        <span class="mb-badge">Elite</span>
    </div>

    <div class="mb-subtitle">
        Strategy. Content. Automation. Projects. 
        Built for modern AI workflows.
    </div>

</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# APP CARDS
# =========================================================

apps = [
    ("AI", "Assistant", "Chat, strategy and coding."),
    ("PR", "Projects", "Workspace and memory."),
    ("AU", "Automation", "AI workflows and systems."),
    ("FB", "Football AI", "Matchday and scouting."),
    ("MD", "Media", "Creator tools and studio."),
]

cols = st.columns(5)

for col, app in zip(cols, apps):

    icon, title, sub = app

    with col:

        st.markdown(
            f"""
<div class="mb-card">

    <div class="mb-icon">
        {icon}
    </div>

    <div class="mb-card-title">
        {title}
    </div>

    <div class="mb-card-sub">
        {sub}
    </div>

</div>
""",
            unsafe_allow_html=True,
        )

        st.button("Open", use_container_width=True)


st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# METRICS
# =========================================================

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Tokens", "18")

with m2:
    st.metric("Jobs", "34")

with m3:
    st.metric("Activity", "100/100")

with m4:
    st.metric("Plan", "Elite")


st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# LOWER AREA
# =========================================================

left, right = st.columns([2.2, 1])

with left:

    st.markdown(
        """
<div class="mb-section-title">
    Live Activity
</div>
""",
        unsafe_allow_html=True,
    )

    for i in range(3):

        st.markdown(
            f"""
<div class="mb-activity">

    <div class="mb-activity-title">
        AI Workflow #{i+1}
    </div>

    <div class="mb-activity-sub">
        Active automation running successfully.
    </div>

</div>
""",
            unsafe_allow_html=True,
        )

with right:

    st.markdown(
        """
<div class="mb-card">

    <div class="mb-section-title">
        Upgrade Elite+
    </div>

    <div class="mb-muted">
        More power, workflows and creator tools.
    </div>

</div>
""",
        unsafe_allow_html=True,
    )