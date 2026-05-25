import io
import re
import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL
from database import (
    save_project_memory,
    get_project,
)
from services.football_service import (
    FootballAPIError,
    fixture_label,
    fixture_team_names,
    format_fixture_stats,
    get_football_service,
    team_display_name,
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
- Hook stärker emotionalisieren
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
- Viralität
- Engagement Potential
- Watchtime Potential
- Plattform Fit
- Emotionalität

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
- Hook Stärke
- Emotionalität
- Engagement
- Watchtime
- Viralität
- CTA Stärke
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
Erstelle ein Football Thumbnail System für:

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
- große YouTube Football Creator
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

    return get_project(project_id, username=st.session_state.get("user"))


# =========================================================
# AI GENERATION
# =========================================================

def generate_matchday_package(club, opponent, platform, tone):
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
# LIVE DATA UI
# =========================================================

def render_football_live_data() -> None:
    service = get_football_service()
    username = st.session_state.get("user") or ""

    if not service.is_configured():
        st.info(
            "Live Match Data benoetigt einen API-Football Key. "
            "Setze `FOOTBALL_API_KEY` in Railway oder `.env`."
        )
        st.caption("Provider: API-Football (api-sports.io)")
        return

    st.subheader("Live Match Data")
    st.caption("Fixtures, Live-Spiele und Head-to-Head via API-Football.")

    search_col, search_btn_col = st.columns([3, 1])
    with search_col:
        team_query = st.text_input(
            "Team suchen",
            placeholder="z.B. Arsenal, Bayern, Real Madrid",
            key="football_team_search_query",
        )
    with search_btn_col:
        st.write("")
        search_teams = st.button(
            "Teams suchen",
            width="stretch",
            key="football_search_teams_btn",
        )

    if search_teams and team_query.strip():
        try:
            with st.spinner("Suche Teams..."):
                st.session_state.football_team_results = service.search_teams(
                    team_query.strip(),
                    username=username,
                )
        except FootballAPIError as exc:
            st.error(str(exc))

    teams = st.session_state.get("football_team_results") or []
    team_id = None

    if teams:
        team_options = {}
        for row in teams:
            team = row.get("team") or {}
            team_key = team.get("id")
            if team_key:
                team_options[team_display_name(row)] = int(team_key)

        if team_options:
            selected_name = st.selectbox(
                "Team auswaehlen",
                list(team_options.keys()),
                key="football_selected_team_name",
            )
            team_id = team_options.get(selected_name)
    elif search_teams and team_query.strip():
        st.warning("Keine Teams gefunden.")

    live_col, fixture_col = st.columns(2)

    with live_col:
        st.markdown("### Live Spiele")
        if st.button("Live aktualisieren", key="football_refresh_live", width="stretch"):
            try:
                with st.spinner("Lade Live-Spiele..."):
                    st.session_state.football_live_fixtures = service.get_live_fixtures(
                        username=username,
                    )
            except FootballAPIError as exc:
                st.error(str(exc))

        live_fixtures = st.session_state.get("football_live_fixtures") or []
        if live_fixtures:
            for item in live_fixtures[:12]:
                home, away = fixture_team_names(item)
                goals = item.get("goals") or {}
                status = ((item.get("fixture") or {}).get("status") or {}).get("long") or "Live"
                st.write(f"**{home}** {goals.get('home', '-')} : {goals.get('away', '-')} **{away}**")
                st.caption(f"{status} | {fixture_label(item)}")
        else:
            st.caption("Keine Live-Spiele geladen. Klicke auf Live aktualisieren.")

    with fixture_col:
        st.markdown("### Team Fixtures")
        if team_id:
            next_n = st.slider("Anzahl naechste Spiele", 1, 10, 5, key="football_next_n")
            if st.button("Fixtures laden", key="football_load_fixtures", width="stretch"):
                try:
                    with st.spinner("Lade Fixtures..."):
                        st.session_state.football_upcoming_fixtures = service.get_upcoming_fixtures(
                            team_id,
                            next_count=next_n,
                            username=username,
                        )
                except FootballAPIError as exc:
                    st.error(str(exc))
        else:
            st.caption("Suche und waehle zuerst ein Team.")

    upcoming = st.session_state.get("football_upcoming_fixtures") or []
    selected_fixture = None

    if upcoming:
        fixture_map = {
            fixture_label(row): row
            for row in upcoming
        }
        selected_label = st.selectbox(
            "Fixture auswaehlen",
            list(fixture_map.keys()),
            key="football_selected_fixture_label",
        )
        selected_fixture = fixture_map.get(selected_label)

    if selected_fixture:
        home, away = fixture_team_names(selected_fixture)
        meta = selected_fixture.get("fixture") or {}
        league = selected_fixture.get("league") or {}
        venue = meta.get("venue") or {}

        info1, info2, info3 = st.columns(3)
        with info1:
            st.metric("Heim", home)
        with info2:
            st.metric("Auswaerts", away)
        with info3:
            st.metric("Status", ((meta.get("status") or {}).get("short") or "NS"))

        st.caption(
            f"{league.get('name', '')} | {meta.get('date', '')} | "
            f"{venue.get('name', 'Unbekanntes Stadion')}"
        )

        action1, action2, action3 = st.columns(3)
        with action1:
            if st.button("Details laden", key="football_load_fixture_detail", width="stretch"):
                fixture_id = meta.get("id")
                if fixture_id:
                    try:
                        with st.spinner("Lade Fixture-Details..."):
                            st.session_state.football_fixture_detail = service.get_fixture(
                                int(fixture_id),
                                username=username,
                            )
                            st.session_state.football_fixture_stats = service.get_fixture_statistics(
                                int(fixture_id),
                                username=username,
                            )
                    except FootballAPIError as exc:
                        st.error(str(exc))

        with action2:
            if st.button("Head-to-Head", key="football_load_h2h", width="stretch"):
                home_id = ((selected_fixture.get("teams") or {}).get("home") or {}).get("id")
                away_id = ((selected_fixture.get("teams") or {}).get("away") or {}).get("id")
                if home_id and away_id:
                    try:
                        with st.spinner("Lade Head-to-Head..."):
                            st.session_state.football_h2h = service.get_head_to_head(
                                int(home_id),
                                int(away_id),
                                username=username,
                            )
                    except FootballAPIError as exc:
                        st.error(str(exc))

        with action3:
            if st.button("Fuer AI uebernehmen", key="football_use_for_ai", width="stretch"):
                st.session_state.football_ai_club_input = home
                st.session_state.football_ai_opponent_input = away
                st.success(f"Uebernommen: {home} vs {away}. Wechsle zum Tab AI Content Engine.")

        detail = st.session_state.get("football_fixture_detail")
        if detail:
            with st.expander("Fixture Details", expanded=False):
                st.json(detail)

        stats = st.session_state.get("football_fixture_stats") or []
        if stats:
            with st.expander("Match Statistiken", expanded=False):
                st.markdown(format_fixture_stats(stats))

        h2h_rows = st.session_state.get("football_h2h") or []
        if h2h_rows:
            with st.expander("Head-to-Head Historie", expanded=False):
                for row in h2h_rows:
                    st.write(fixture_label(row))


# =========================================================
# AI CONTENT UI
# =========================================================

def render_football_ai_engine() -> None:
    project = active_project()

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
        club = st.text_input(
            "Club",
            placeholder="Arsenal",
            key="football_ai_club_input",
        )

        opponent = st.text_input(
            "Opponent",
            placeholder="Manchester City",
            key="football_ai_opponent_input",
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
            with st.spinner("MaByte optimiert Viralität..."):
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


def render_football() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    st.title("Football Intelligence")

    st.caption(
        "Live Match Data + Multi Platform AI Matchday Engine fuer viralen Football Content."
    )

    project = active_project()
    if project:
        st.success(f"Aktives Projekt: {project.get('title')}")
    else:
        st.info("Kein aktives Projekt ausgewaehlt. Memory wird nicht gespeichert.")

    st.divider()

    tab_live, tab_ai = st.tabs(["Live Match Data", "AI Content Engine"])

    with tab_live:
        render_football_live_data()

    with tab_ai:
        render_football_ai_engine()
