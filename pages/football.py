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


def generate_matchday_package(
    club,
    opponent,
    platform,
    tone,
):

    if not OPENAI_API_KEY:

        return f"""
# Demo Matchday Package

Club:
{club}

Opponent:
{opponent}

Platform:
{platform}

Tone:
{tone}

OPENAI_API_KEY fehlt aktuell.
"""

    prompt = f"""
Erstelle ein komplettes virales Matchday Content Package.

Club:
{club}

Gegner:
{opponent}

Plattform:
{platform}

Ton:
{tone}

Erstelle:

1. Viral Hook
2. Reel Script
3. TikTok Caption
4. X/Twitter Thread
5. Thumbnail Prompt
6. Hashtags
7. CTA
8. Posting Strategy

Antworte hochwertig, kreativ und modern.
"""

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
Du bist ein Elite Football Content Strategist.
Du erstellst viralen modernen Social Media Football Content.
Denke wie große Football Creator auf TikTok, Instagram und X.
""",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.9,
    )

    return response.choices[0].message.content


# =========================================================
# MAIN
# =========================================================

def render_football():

    if not st.session_state.get("logged_in"):

        st.session_state.page = "auth"
        st.rerun()
        return

    st.title("⚽ Football Intelligence")

    st.caption(
        "AI Matchday Engine für viralen Football Content."
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
            "Platform",
            [
                "TikTok",
                "Instagram",
                "X/Twitter",
                "YouTube Shorts",
            ],
        )

        tone = st.selectbox(
            "Tone",
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
            "🚀 Generate Matchday Package",
            use_container_width=True,
        )

    with right:

        st.markdown(
            """
### ⚡ Package Output

Der AI Agent erstellt:

- Viral Hook
- Reel Script
- Caption
- Twitter Thread
- Thumbnail Prompt
- Hashtags
- CTA
- Posting Strategy
"""
        )

    st.divider()

    if generate:

        if not club or not opponent:

            st.warning(
                "Bitte Club und Gegner eingeben."
            )

            return

        with st.spinner(
            "MaByte generiert virales Matchday Package..."
        ):

            result = generate_matchday_package(
                club,
                opponent,
                platform,
                tone,
            )

        st.markdown(result)

        if project:

            save_project_memory(
                project_id=project.get("id"),
                username=st.session_state.get("user"),
                workspace="football",
                memory_type="matchday_package",
                content=result[:5000],
            )

            st.success(
                "Package in Projekt-Memory gespeichert."
            )