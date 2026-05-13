import io
import re
import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL
from database import (
    save_project_memory,
    get_project,
)

client = OpenAI(api_key=OPENAI_API_KEY)


# =========================================================
# HELPERS
# =========================================================

def active_project():

    project_id = st.session_state.get("active_project_id")

    if not project_id:
        return None

    return get_project(project_id)


# =========================================================
# AI GENERATION
# =========================================================

def generate_matchday_package(
    club,
    opponent,
    platform,
    tone,
):

    if not OPENAI_API_KEY:

        return f"""
## TikTok Hook
Demo Hook für {club} gegen {opponent}

## TikTok Caption
Demo TikTok Caption

## Instagram Reel Caption
Demo Instagram Caption

## X/Twitter Thread
1. Demo Thread

## YouTube Shorts Title
Demo YouTube Titel

## YouTube Shorts Description
Demo Shorts Beschreibung

## Thumbnail Prompt
Demo Thumbnail Prompt

## Hashtags
#{club} #Football #Matchday

## CTA
Folge für mehr Football Content

## Posting Strategy
Poste 2 Stunden vor Kickoff
"""

    prompt = f"""
Erstelle ein komplettes virales Football Matchday Content System.

Club:
{club}

Gegner:
{opponent}

Hauptplattform:
{platform}

Ton:
{tone}

Erstelle hochwertige Inhalte für:

## TikTok Hook

## TikTok Caption

## Instagram Reel Caption

## X/Twitter Thread

## YouTube Shorts Title

## YouTube Shorts Description

## Thumbnail Prompt

## Hashtags

## CTA

## Posting Strategy

Antworte modern, viral, emotional und creator-orientiert.
"""

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
Du bist ein Elite Football Content Strategist.

Du erstellst:
- virale Hooks
- Creator Scripts
- Football Storytelling
- Social Media Packages
- moderne Plattform-optimierte Inhalte

Denke wie:
- große TikTok Football Creator
- Fußball Meme Pages
- moderne Social Media Teams
- Elite Football Media Brands
""",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.9,
    )

    return response.choices[0].message.content


# =========================================================
# SECTION SPLITTING
# =========================================================

def split_sections(result):

    section_map = {
        "tiktok hook": "🎣 TikTok Hook",
        "tiktok caption": "📱 TikTok Caption",
        "instagram reel caption": "📸 Instagram Caption",
        "twitter thread": "🧵 Twitter Thread",
        "x/twitter thread": "🧵 Twitter Thread",
        "youtube shorts title": "▶️ YouTube Title",
        "youtube shorts description": "📺 YouTube Description",
        "thumbnail prompt": "🖼️ Thumbnail Prompt",
        "hashtags": "#️⃣ Hashtags",
        "cta": "📢 CTA",
        "posting strategy": "📈 Posting Strategy",
    }

    sections = {
        "🎣 TikTok Hook": "",
        "📱 TikTok Caption": "",
        "📸 Instagram Caption": "",
        "🧵 Twitter Thread": "",
        "▶️ YouTube Title": "",
        "📺 YouTube Description": "",
        "🖼️ Thumbnail Prompt": "",
        "#️⃣ Hashtags": "",
        "📢 CTA": "",
        "📈 Posting Strategy": "",
    }

    current = None

    for line in result.splitlines():

        clean = line.strip()

        lower = clean.lower()

        lower = re.sub(
            r"^[#\-\d\.\)\s]+",
            "",
            lower,
        ).strip()

        matched = None

        for key, title in section_map.items():

            if lower.startswith(key):

                matched = title
                break

        if matched:

            current = matched
            continue

        if current:
            sections[current] += line + "\n"

    fallback_empty = all(
        not value.strip()
        for value in sections.values()
    )

    if fallback_empty:
        sections["🎣 TikTok Hook"] = result

    return sections


# =========================================================
# FILE HELPERS
# =========================================================

def safe_filename(title):

    return (
        title.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "")
    )


# =========================================================
# PACKAGE TABS
# =========================================================

def render_package_tabs(result):

    sections = split_sections(result)

    tabs = st.tabs(
        list(sections.keys())
    )

    for i, title in enumerate(sections.keys()):

        with tabs[i]:

            content = sections[title].strip()

            if not content:
                content = "Kein Inhalt generiert."

            st.markdown(content)

            st.divider()

            st.code(content)

            st.download_button(
                f"⬇️ Download {title}",
                data=content.encode("utf-8"),
                file_name=f"mabyte_{safe_filename(title)}.txt",
                mime="text/plain",
                use_container_width=True,
            )


# =========================================================
# FULL EXPORT
# =========================================================

def render_full_export(result):

    st.subheader("📦 Full Package Export")

    export_data = io.BytesIO()

    export_data.write(
        result.encode("utf-8")
    )

    export_data.seek(0)

    st.download_button(
        "⬇️ Download Full Matchday Package",
        data=export_data,
        file_name="mabyte_matchday_package.txt",
        mime="text/plain",
        use_container_width=True,
    )


# =========================================================
# UI
# =========================================================

def render_football():

    if not st.session_state.get("logged_in"):

        st.session_state.page = "auth"
        st.rerun()
        return

    st.title("⚽ Football Intelligence")

    st.caption(
        "Multi Platform AI Matchday Engine für viralen Football Content."
    )

    project = active_project()

    if project:

        st.success(
            f"Aktives Projekt: {project.get('title')}"
        )

    else:

        st.info(
            "Kein aktives Projekt ausgewählt. Memory wird nicht gespeichert."
        )

    st.divider()

    top1, top2, top3, top4 = st.columns(4)

    with top1:
        st.metric(
            "Platforms",
            "4",
        )

    with top2:
        st.metric(
            "Content Types",
            "10",
        )

    with top3:
        st.metric(
            "AI Pipeline",
            "Active",
        )

    with top4:
        st.metric(
            "Export Engine",
            "Online",
        )

    st.divider()

    left, right = st.columns(
        [1, 1],
        gap="large",
    )

    with left:

        club = st.text_input(
            "Club",
            placeholder="Arsenal",
        )

        opponent = st.text_input(
            "Opponent",
            placeholder="Manchester City",
        )

        platform = st.selectbox(
            "Primary Platform",
            [
                "TikTok",
                "Instagram",
                "X/Twitter",
                "YouTube Shorts",
            ],
        )

        tone = st.selectbox(
            "Content Tone",
            [
                "Viral",
                "Aggressive",
                "Emotional",
                "Funny",
                "Professional",
                "Tactical",
            ],
        )

        generate = st.button(
            "🚀 Generate Multi Platform Package",
            use_container_width=True,
        )

    with right:

        with st.container(border=True):

            st.markdown(
                "### ⚡ Generated Content"
            )

            st.write("✅ TikTok Hook")
            st.write("✅ TikTok Caption")
            st.write("✅ Instagram Caption")
            st.write("✅ Twitter Thread")
            st.write("✅ YouTube Title")
            st.write("✅ YouTube Description")
            st.write("✅ Thumbnail Prompt")
            st.write("✅ Hashtags")
            st.write("✅ CTA")
            st.write("✅ Posting Strategy")
            st.write("✅ Export System")

    st.divider()

    if generate:

        if not club or not opponent:

            st.warning(
                "Bitte Club und Gegner eingeben."
            )

            return

        with st.spinner(
            "MaByte generiert Multi Platform Matchday Package..."
        ):

            result = generate_matchday_package(
                club,
                opponent,
                platform,
                tone,
            )

        st.subheader(
            "🚀 Matchday Content Package"
        )

        render_package_tabs(result)

        st.divider()

        render_full_export(result)

        st.divider()

        with st.expander(
            "Raw Output anzeigen"
        ):

            st.markdown(result)

        if project:

            save_project_memory(
                project_id=project.get("id"),
                username=st.session_state.get("user"),
                workspace="football",
                memory_type="multi_platform_package",
                content=result[:5000],
            )

            st.success(
                "Package in Projekt-Memory gespeichert."
            )