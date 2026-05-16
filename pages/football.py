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
# VIRAL ANALYSIS
# =========================================================

def analyze_viral_score(content):
    if not OPENAI_API_KEY:
        return {
            "score": 82,
            "feedback": """
- Hook stÃ¤rker emotionalisieren
- Mehr Spannung im ersten Satz
- CTA aggressiver formulieren
"""
        }

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
Du bist ein Elite Social Media Growth Strategist.

Bewerte Football Content auf:
- ViralitÃ¤t
- Engagement Potential
- Watchtime Potential
- Plattform Fit
- EmotionalitÃ¤t

Antworte exakt so:

SCORE: <zahl>

FEEDBACK:
- Punkt
- Punkt
- Punkt
"""
            },
            {
                "role": "user",
                "content": content[:5000],
            }
        ],
        temperature=0.4,
    )

    text = response.choices[0].message.content
    score = 75

    match = re.search(r"SCORE:\s*(\d+)", text)

    if match:
        score = int(match.group(1))

    feedback = text.split("FEEDBACK:")[-1].strip()

    return {
        "score": score,
        "feedback": feedback,
    }


# =========================================================
# OPTIMIZER
# =========================================================

def improve_package(original_content):
    if not OPENAI_API_KEY:
        return original_content + "\n\n[Improved Version Demo]"

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
Du bist ein Elite Viral Football Growth Strategist.

Verbessere:
- Hook StÃ¤rke
- EmotionalitÃ¤t
- Engagement
- Watchtime
- ViralitÃ¤t
- CTA StÃ¤rke
- Plattform Optimierung

Mache den Content aggressiver, moderner und creator-orientierter.
"""
            },
            {
                "role": "user",
                "content": original_content[:7000],
            }
        ],
        temperature=0.95,
    )

    return response.choices[0].message.content


# =========================================================
# THUMBNAIL ENGINE
# =========================================================

def generate_thumbnail_system(club, opponent):
    if not OPENAI_API_KEY:
        return f"""
## YouTube Thumbnail
Ultra emotional football thumbnail of {club} vs {opponent}, cinematic stadium lights, dramatic facial expressions, high contrast, viral sports YouTube thumbnail, intense atmosphere, red and blue lighting, shocked fans, modern football media style

## TikTok Cover
Vertical football cover art for {club} vs {opponent}, modern typography, aggressive emotions, high saturation, creator-style football graphics

## Instagram Cover
Modern football reel cover with dynamic action pose, clean bold text, elite football creator aesthetic

## Text Overlay Ideas
- THIS MATCH CHANGES EVERYTHING
- THEY ARE FINISHED
- THE BIGGEST MATCH YET

## Negative Prompt
low quality, blurry, ugly face, distorted anatomy, bad typography, watermark, low contrast
"""

    prompt = f"""
Erstelle ein Football Thumbnail System fÃ¼r:

Club:
{club}

Gegner:
{opponent}

Erstelle:

## YouTube Thumbnail

## TikTok Cover

## Instagram Cover

## Text Overlay Ideas

## Negative Prompt

Sehr modern, viral und creator-orientiert.
"""

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
Du bist ein Elite Sports Thumbnail Designer.

Du erstellst:
- virale Thumbnail Prompts
- CTR optimierte Cover
- moderne Creator Designs
- aggressive Football Visuals

Denke wie:
- groÃŸe YouTube Football Creator
- TikTok Sports Creators
- moderne Sports Media Brands
"""
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.95,
    )

    return response.choices[0].message.content


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

def generate_matchday_package(club, opponent, platform, tone):
    if not OPENAI_API_KEY:
        return f"""
## TikTok Hook
Demo Hook fÃ¼r {club} gegen {opponent}

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
Folge fÃ¼r mehr Football Content

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

Erstelle hochwertige Inhalte fÃ¼r:

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
- groÃŸe TikTok Football Creator
- FuÃŸball Meme Pages
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
        "tiktok hook": "ðŸŽ£ TikTok Hook",
        "tiktok caption": "ðŸ“± TikTok Caption",
        "instagram reel caption": "ðŸ“¸ Instagram Caption",
        "twitter thread": "ðŸ§µ Twitter Thread",
        "x/twitter thread": "ðŸ§µ Twitter Thread",
        "youtube shorts title": "â–¶ï¸ YouTube Title",
        "youtube shorts description": "ðŸ“º YouTube Description",
        "thumbnail prompt": "ðŸ–¼ï¸ Thumbnail Prompt",
        "hashtags": "#ï¸âƒ£ Hashtags",
        "cta": "ðŸ“¢ CTA",
        "posting strategy": "ðŸ“ˆ Posting Strategy",
    }

    sections = {
        "ðŸŽ£ TikTok Hook": "",
        "ðŸ“± TikTok Caption": "",
        "ðŸ“¸ Instagram Caption": "",
        "ðŸ§µ Twitter Thread": "",
        "â–¶ï¸ YouTube Title": "",
        "ðŸ“º YouTube Description": "",
        "ðŸ–¼ï¸ Thumbnail Prompt": "",
        "#ï¸âƒ£ Hashtags": "",
        "ðŸ“¢ CTA": "",
        "ðŸ“ˆ Posting Strategy": "",
    }

    current = None

    for line in result.splitlines():
        clean = line.strip()
        lower = clean.lower()
        lower = re.sub(r"^[#\-\d\.\)\s]+", "", lower).strip()

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
        sections["ðŸŽ£ TikTok Hook"] = result

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

    tabs = st.tabs(list(sections.keys()))

    for i, title in enumerate(sections.keys()):
        with tabs[i]:
            content = sections[title].strip()

            if not content:
                content = "Kein Inhalt generiert."

            st.markdown(content)

            st.divider()

            st.code(content)

            st.download_button(
                f"â¬‡ï¸ Download {title}",
                data=content.encode("utf-8"),
                file_name=f"mabyte_{safe_filename(title)}.txt",
                mime="text/plain",
                width="stretch",
            )


# =========================================================
# FULL EXPORT
# =========================================================

def render_full_export(result, filename="mabyte_matchday_package.txt"):
    st.subheader("ðŸ“¦ Full Package Export")

    export_data = io.BytesIO()
    export_data.write(result.encode("utf-8"))
    export_data.seek(0)

    st.download_button(
        "â¬‡ï¸ Download Full Package",
        data=export_data,
        file_name=filename,
        mime="text/plain",
        width="stretch",
    )


# =========================================================
# MAIN UI
# =========================================================

def render_football():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    st.title("âš½ Football Intelligence")

    st.caption(
        "Multi Platform AI Matchday Engine fÃ¼r viralen Football Content."
    )

    project = active_project()

    if project:
        st.success(f"Aktives Projekt: {project.get('title')}")
    else:
        st.info("Kein aktives Projekt ausgewÃ¤hlt. Memory wird nicht gespeichert.")

    st.divider()

    top1, top2, top3, top4 = st.columns(4)

    with top1:
        st.metric("Platforms", "4")

    with top2:
        st.metric("Content Types", "10+")

    with top3:
        st.metric("AI Pipeline", "Active")

    with top4:
        st.metric("Export Engine", "Online")

    st.divider()

    left, right = st.columns([1, 1], gap="large")

    with left:
        club = st.text_input("Club", placeholder="Arsenal")

        opponent = st.text_input("Opponent", placeholder="Manchester City")

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
            "ðŸš€ Generate Multi Platform Package",
            width="stretch",
        )

    with right:
        with st.container(border=True):
            st.markdown("### âš¡ Generated Content")
            st.write("âœ… TikTok Hook")
            st.write("âœ… TikTok Caption")
            st.write("âœ… Instagram Caption")
            st.write("âœ… Twitter Thread")
            st.write("âœ… YouTube Title")
            st.write("âœ… YouTube Description")
            st.write("âœ… Thumbnail Intelligence")
            st.write("âœ… Hashtags")
            st.write("âœ… CTA")
            st.write("âœ… Posting Strategy")
            st.write("âœ… Viral Intelligence")
            st.write("âœ… AI Optimization")
            st.write("âœ… Export System")

    st.divider()

    if generate:
        if not club or not opponent:
            st.warning("Bitte Club und Gegner eingeben.")
            return

        with st.spinner("MaByte generiert Multi Platform Matchday Package..."):
            result = generate_matchday_package(
                club,
                opponent,
                platform,
                tone,
            )

        st.subheader("ðŸš€ Matchday Content Package")

        render_package_tabs(result)

        st.divider()

        render_full_export(
            result,
            filename="mabyte_matchday_package.txt",
        )

        st.divider()

        with st.spinner("Generiere Thumbnail System..."):
            thumbnails = generate_thumbnail_system(
                club,
                opponent,
            )

        st.subheader("ðŸ–¼ï¸ Thumbnail Intelligence")

        st.markdown(thumbnails)

        st.download_button(
            "â¬‡ï¸ Download Thumbnail System",
            data=thumbnails.encode("utf-8"),
            file_name="mabyte_thumbnail_system.txt",
            mime="text/plain",
            width="stretch",
        )

        if project:
            save_project_memory(
                project_id=project.get("id"),
                username=st.session_state.get("user"),
                workspace="football",
                memory_type="thumbnail_system",
                content=thumbnails[:5000],
            )

        st.divider()

        with st.spinner("Analysiere Viral Potential..."):
            analysis = analyze_viral_score(result)

        score = analysis.get("score", 0)
        feedback = analysis.get("feedback", "")

        st.subheader("ðŸ”¥ Viral Intelligence")

        c1, c2 = st.columns([1, 2])

        with c1:
            st.metric("Viral Score", f"{score}/100")
            st.progress(min(score, 100) / 100)

        with c2:
            st.markdown(feedback)

        st.divider()

        improve = st.button(
            "âš¡ Improve Package",
            width="stretch",
        )

        if improve:
            with st.spinner("MaByte optimiert ViralitÃ¤t..."):
                improved = improve_package(result)

            st.subheader("ðŸš€ Optimized Package")

            render_package_tabs(improved)

            st.divider()

            render_full_export(
                improved,
                filename="mabyte_optimized_matchday_package.txt",
            )

            if project:
                save_project_memory(
                    project_id=project.get("id"),
                    username=st.session_state.get("user"),
                    workspace="football",
                    memory_type="optimized_package",
                    content=improved[:5000],
                )

                st.success("Optimized Package gespeichert.")

        st.divider()

        with st.expander("Raw Output anzeigen"):
            st.markdown(result)

        if project:
            save_project_memory(
                project_id=project.get("id"),
                username=st.session_state.get("user"),
                workspace="football",
                memory_type="multi_platform_package",
                content=result[:5000],
            )

            st.success("Package in Projekt-Memory gespeichert.")
