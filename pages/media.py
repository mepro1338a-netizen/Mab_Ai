import streamlit as st


# =========================================================
# HELPERS
# =========================================================

def ensure_logged_in():

    if not st.session_state.get("logged_in"):

        st.session_state.page = "auth"

        st.rerun()


def user_plan():

    return st.session_state.get(
        "plan",
        "free"
    )


def tokens():

    return int(
        st.session_state.get(
            "tokens",
            0
        ) or 0
    )


# =========================================================
# CSS
# =========================================================

def media_css():

    st.markdown(
        """
<style>

.main .block-container{
    max-width:1280px;
    padding-top:5rem;
    padding-bottom:3rem;
}

.media-hero{
    border-radius:28px;
    padding:30px;
    margin-bottom:24px;

    background:
        radial-gradient(circle at top right, rgba(56,189,248,.22), transparent 30%),
        linear-gradient(135deg,#020617,#0f172a);

    border:1px solid rgba(255,255,255,.08);

    box-shadow:
        0 20px 50px rgba(0,0,0,.28);
}

.media-kicker{
    color:#ffd36a;
    font-size:12px;
    font-weight:900;
    letter-spacing:.14em;
    text-transform:uppercase;
}

.media-title{
    color:#ffffff;
    font-size:42px;
    font-weight:1000;
    line-height:1.05;
    margin-top:10px;
}

.media-sub{
    color:#cbd5e1;
    font-size:15px;
    line-height:1.6;
    margin-top:14px;
    max-width:850px;
}

.studio-card{
    border-radius:24px;
    padding:22px;

    background:
        linear-gradient(
            180deg,
            rgba(15,23,42,.95),
            rgba(30,41,59,.92)
        );

    border:1px solid rgba(255,255,255,.08);

    box-shadow:
        0 12px 30px rgba(0,0,0,.22);

    margin-bottom:18px;
}

.studio-title{
    color:#ffffff;
    font-size:20px;
    font-weight:900;
    margin-bottom:6px;
}

.studio-sub{
    color:#94a3b8;
    font-size:13px;
    line-height:1.5;
}

.preview-box{
    border-radius:18px;
    padding:14px;

    background:
        linear-gradient(
            180deg,
            rgba(59,130,246,.18),
            rgba(15,23,42,.85)
        );

    border:1px solid rgba(59,130,246,.20);

    margin-bottom:10px;
}

.preview-label{
    color:#7dd3fc;
    font-size:11px;
    font-weight:900;
    letter-spacing:.08em;
    text-transform:uppercase;
}

.preview-value{
    color:#ffffff;
    font-size:15px;
    font-weight:800;
    margin-top:5px;
}

.stButton > button{
    border:none!important;
    border-radius:16px!important;

    background:
        linear-gradient(
            135deg,
            #38bdf8,
            #2563eb
        )!important;

    color:white!important;

    min-height:46px!important;

    font-weight:900!important;

    box-shadow:
        0 12px 24px rgba(37,99,235,.25)!important;
}

div[data-testid="stMetric"]{
    background:
        linear-gradient(
            135deg,
            #0f172a,
            #1e293b
        )!important;

    border:1px solid rgba(255,255,255,.08)!important;

    border-radius:22px!important;

    padding:16px!important;
}

div[data-testid="stMetricLabel"]{
    color:#7dd3fc!important;
    font-size:11px!important;
    font-weight:900!important;
}

div[data-testid="stMetricValue"]{
    color:#ffffff!important;
    font-size:28px!important;
    font-weight:1000!important;
}

</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# HERO
# =========================================================

def hero():

    st.markdown(
        """
<div class="media-hero">

    <div class="media-kicker">
        AI CONTENT STUDIO
    </div>

    <div class="media-title">
        Create viral short-form content.
    </div>

    <div class="media-sub">
        Erstelle kompakte Reels, Hooks, Captions,
        Scripts, CTA Flows und Creator Assets
        mit AI Workflows.
    </div>

</div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# CODING
# =========================================================

def render_coding_ai():

    st.title("💻 Developer OS")

    st.info(
        "Coding Workspace aktiv."
    )


# =========================================================
# IMAGE
# =========================================================

def render_image_ai():

    st.title("🎨 Creative Workspace")

    st.info(
        "Image Workspace aktiv."
    )


# =========================================================
# MUSIC
# =========================================================

def render_music_generator():

    media_css()

    st.title("🎵 Music Studio")

    st.caption(
        "Songs kosten jetzt 100 Tokens."
    )

    topic = st.text_input(
        "Song Thema"
    )

    genre = st.selectbox(
        "Genre",
        [
            "Rap",
            "Trap",
            "Pop",
            "EDM",
            "Phonk",
        ],
    )

    st.metric(
        "Kosten",
        "100 Tokens"
    )

    if st.button(
        "🎵 Song generieren",
        use_container_width=True
    ):

        if not topic:

            st.warning(
                "Bitte Thema eingeben."
            )

            return

        st.success(
            "Song Package erstellt."
        )

        st.markdown(
            f"""
## Song

**Thema:** {topic}

**Genre:** {genre}

- Hook
- Chorus
- Lyrics
- Viral Caption
- Music Prompt
            """
        )


# =========================================================
# REELS
# =========================================================

def render_reels_creator():

    media_css()

    hero()

    top1, top2, top3 = st.columns(3)

    with top1:
        st.metric(
            "Max Video",
            "7s"
        )

    with top2:
        st.metric(
            "Format",
            "Short-form"
        )

    with top3:
        st.metric(
            "Plan",
            user_plan().upper()
        )

    st.divider()

    left, center, right = st.columns(
        [1.1, 1.3, .9],
        gap="large"
    )

    # =====================================================
    # LEFT
    # =====================================================

    with left:

        st.markdown(
            """
<div class="studio-card">

    <div class="studio-title">
        Creative Brief
    </div>

    <div class="studio-sub">
        Beschreibe dein Reel.
    </div>

</div>
            """,
            unsafe_allow_html=True,
        )

        topic = st.text_area(
            "Thema",
            height=130,
            placeholder="z.B. Warum Arsenal dieses Jahr gefährlich ist..."
        )

        platform = st.selectbox(
            "Plattform",
            [
                "TikTok",
                "Instagram Reels",
                "YouTube Shorts",
            ],
        )

        content_type = st.selectbox(
            "Content Typ",
            [
                "Football Reel",
                "Storytelling",
                "Educational",
                "Meme Page",
                "Personal Brand",
            ],
        )

        tone = st.selectbox(
            "Ton",
            [
                "Viral",
                "Bold",
                "Funny",
                "Premium",
            ],
        )

    # =====================================================
    # CENTER
    # =====================================================

    with center:

        st.markdown(
            """
<div class="studio-card">

    <div class="studio-title">
        Creator Output
    </div>

    <div class="studio-sub">
        Hook, Script und Posting Flow.
    </div>

</div>
            """,
            unsafe_allow_html=True,
        )

        template = st.selectbox(
            "Template",
            [
                "Viral Package",
                "Football Matchday",
                "Creator Growth",
                "Ad Creative",
            ],
        )

        voice = st.selectbox(
            "Voice",
            [
                "Creator",
                "Narrator",
                "Coach",
                "Analyst",
            ],
        )

        cta = st.text_input(
            "CTA",
            placeholder="Folge für mehr..."
        )

        seconds = st.slider(
            "Videolänge",
            min_value=3,
            max_value=7,
            value=7,
        )

        st.markdown(
            f"""
<div class="preview-box">

    <div class="preview-label">
        Hook
    </div>

    <div class="preview-value">
        0–2 Sekunden
    </div>

</div>

<div class="preview-box">

    <div class="preview-label">
        Main Scene
    </div>

    <div class="preview-value">
        2–5 Sekunden
    </div>

</div>

<div class="preview-box">

    <div class="preview-label">
        CTA
    </div>

    <div class="preview-value">
        5–7 Sekunden
    </div>

</div>
            """,
            unsafe_allow_html=True,
        )

    # =====================================================
    # RIGHT
    # =====================================================

    with right:

        st.markdown(
            """
<div class="studio-card">

    <div class="studio-title">
        Creator Queue
    </div>

    <div class="studio-sub">
        Workflow & Export.
    </div>

</div>
            """,
            unsafe_allow_html=True,
        )

        st.metric(
            "Kosten",
            "25 Tokens"
        )

        st.metric(
            "Verfügbar",
            tokens()
        )

        st.info(
            "Auto Posting folgt später."
        )

    st.divider()

    if st.button(
        "🚀 Content Package generieren",
        use_container_width=True
    ):

        if not topic:

            st.warning(
                "Bitte Thema eingeben."
            )

            return

        st.success(
            "Content Package erstellt."
        )

        st.markdown(
            f"""
# Viral Hook

{topic} verändert alles.

# Script

0-2s:
Aggressiver Einstieg.

2-5s:
Main Point.

5-7s:
CTA.

# Caption

Dieses Reel wird viral.

# Hashtags

#football #viral #fyp
            """
        )


# =========================================================
# VIDEO
# =========================================================

def render_video_generator():

    media_css()

    st.title("🎬 Media Studio")

    st.info(
        "Video Generator aktiv."
    )


# =========================================================
# MAIN
# =========================================================

def render_media(active_tool="reels"):

    ensure_logged_in()

    if active_tool == "coding":

        render_coding_ai()

    elif active_tool == "image":

        render_image_ai()

    elif active_tool == "music":

        render_music_generator()

    elif active_tool == "reels":

        render_reels_creator()

    elif active_tool == "video":

        render_video_generator()

    else:

        render_reels_creator()