import io
import re
import streamlit as st
from openai import OpenAI

from config import FOOTBALL_FEATURES, FOOTBALL_PLANS, OPENAI_API_KEY, OPENAI_TEXT_MODEL
from database import (
    save_project_memory,
    get_project,
)
from services.football_access import (
    FootballAccessError as FootballGateError,
    can_access_feature,
    can_export_reels,
    can_run_action,
    consume_action,
    feature_label,
    usage_summary,
)
from ui.premium_foundation import (
    premium_foundation_css,
    render_feature_grid,
    render_page_hero,
    render_upgrade_card,
)
from services.football_service import (
    FootballAPIError,
    fixture_label,
    fixture_team_names,
    format_fixture_stats,
    get_football_service,
    team_display_name,
)
from ui.styles import inject_css, page_layout_css, gradient_title_css

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


def current_username() -> str:
    return str(st.session_state.get("user") or "")


def session_football_plan() -> str:
    return str(st.session_state.get("football_plan") or "none")


def football_css() -> None:
    premium_foundation_css(1280, 88, """
.fb-title {
    font-size: 38px;
    font-weight: 1000;
    color: #ffe7a3 !important;
    margin-top: 8px;
}
.fb-hero {
    border-radius: 28px;
    padding: 28px 32px;
    margin-bottom: 22px;
    background:
        radial-gradient(circle at 88% 18%, rgba(34,197,94,.18), transparent 32%),
        radial-gradient(circle at 12% 0%, rgba(168,85,247,.20), transparent 34%),
        linear-gradient(135deg, rgba(12,18,42,.96), rgba(7,22,18,.94));
    border: 1px solid rgba(255,231,163,.14);
    box-shadow: 0 24px 60px rgba(0,0,0,.32);
}
.fb-kicker {
    color: #86efac !important;
    font-size: 11px;
    font-weight: 1000;
    letter-spacing: .2em;
    text-transform: uppercase;
}
.fb-title {
    margin-top: 8px;
}
.fb-sub {
    color: #cbd5e1 !important;
    font-size: 15px;
    line-height: 1.55;
    max-width: 820px;
    margin-top: 10px;
}
.fb-plan-pill {
    display: inline-flex;
    padding: 8px 14px;
    border-radius: 999px;
    background: linear-gradient(135deg, #166534, #15803d);
    color: #ecfccb !important;
    font-size: 12px;
    font-weight: 1000;
    margin-top: 12px;
}
.fb-plan-pill.locked {
    background: linear-gradient(135deg, #4c1d95, #312e81);
}
.fb-upgrade {
    border-radius: 22px;
    padding: 22px 24px;
    border: 1px dashed rgba(255,231,163,.28);
    background: rgba(15,23,42,.55);
    margin-bottom: 16px;
}
.fb-upgrade h4 {
    color: #ffe7a3 !important;
    margin: 0 0 8px 0;
}
""")


def open_premium() -> None:
    st.session_state.page = "premium"
    st.rerun()


def render_plan_status() -> dict:
    summary = usage_summary(current_username(), session_football_plan())
    ai_lim = summary["ai_limit"]
    ai_lim_txt = str(ai_lim) if isinstance(ai_lim, int) else ai_lim
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Football Plan", summary["plan_label"])
    with c2:
        st.metric(
            "AI Analysen heute",
            f"{summary['ai_used']}/{ai_lim_txt}",
        )
    with c3:
        if summary["live_api"]:
            st.metric(
                "API Requests heute",
                f"{summary['api_used']:,}".replace(",", "."),
                help=f"Tageslimit: {summary['api_limit']:,}".replace(",", "."),
            )
        else:
            st.metric("API", "—", help="Football Plan erforderlich")
    with c4:
        st.metric("Stufe", summary["tier"] or "—")
    return summary


def render_feature_matrix(summary: dict) -> None:
    feats = summary.get("features") or {}
    by_cat: dict[str, list[tuple[str, bool]]] = {}
    for fid, meta in FOOTBALL_FEATURES.items():
        cat = meta.get("category", "api")
        by_cat.setdefault(cat, []).append(
            (meta.get("label", fid), bool(feats.get(fid)))
        )
    labels = {
        "api": "API & Live Data",
        "ai": "AI Content",
        "export": "Export",
        "automation": "Automation",
    }
    for cat, items in by_cat.items():
        st.markdown(f"**{labels.get(cat, cat)}**")
        render_feature_grid(items)


def gated_api_block(
    feature_id: str,
    title: str,
    description: str,
    render_fn,
) -> None:
    user = current_username()
    plan = session_football_plan()
    ok, msg, need = can_access_feature(user, feature_id, plan)
    if ok:
        render_fn()
    else:
        render_upgrade_card(
            title,
            description or msg,
            need,
            button_key=f"up_{feature_id}",
            on_upgrade=open_premium,
        )


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

def _pick_team_id() -> int | None:
    teams = st.session_state.get("football_team_results") or []
    if not teams:
        return None
    team_options = {}
    for row in teams:
        team = row.get("team") or {}
        tid = team.get("id")
        if tid:
            team_options[team_display_name(row)] = int(tid)
    if not team_options:
        return None
    selected_name = st.selectbox(
        "Team auswählen",
        list(team_options.keys()),
        key="football_selected_team_name",
    )
    return team_options.get(selected_name)


def render_football_live_data(summary: dict) -> None:
    if summary.get("plan") == "none":
        render_upgrade_card(
            "Football Premium erforderlich",
            "API-Daten und Football AI starten ab Football Starter.",
            "football_starter",
            button_key="fb_need_starter",
            on_upgrade=open_premium,
        )
        return

    service = get_football_service()
    username = current_username()

    if not service.is_configured():
        st.info(
            "API-Football Key fehlt auf dem Server (FOOTBALL_API_KEY). "
            "Dein Plan ist aktiv — Daten erscheinen nach Konfiguration in Railway/.env."
        )
        st.caption("Provider: api-sports.io · Requests werden gecacht")
        return

    st.subheader("Daten & API")
    st.caption(
        f"Gecachte Requests · heute {summary['api_used']:,} / {summary['api_limit']:,}".replace(",", ".")
    )

    search_col, search_btn_col = st.columns([3, 1])
    with search_col:
        st.text_input(
            "Team suchen",
            placeholder="z.B. Arsenal, Bayern, Real Madrid",
            key="football_team_search_query",
        )
    with search_btn_col:
        st.write("")
        if st.button("Teams suchen", width="stretch", key="football_search_teams_btn"):
            q = st.session_state.get("football_team_search_query", "").strip()
            if q:
                try:
                    with st.spinner("Suche Teams..."):
                        st.session_state.football_team_results = service.search_teams(
                            q, username=username,
                        )
                except FootballAPIError as exc:
                    st.error(str(exc))
            else:
                st.warning("Bitte Teamname eingeben.")

    team_id = _pick_team_id()

    st.markdown("#### Starter — Fixtures, Results, Standings")
    fc1, fc2 = st.columns(2)
    with fc1:
        if team_id and st.button("Fixtures laden", key="football_load_fixtures", width="stretch"):
            try:
                n = st.session_state.get("football_next_n", 5)
                st.session_state.football_upcoming_fixtures = service.get_upcoming_fixtures(
                    team_id, next_count=n, username=username,
                )
            except FootballAPIError as exc:
                st.error(str(exc))
        if team_id:
            st.slider("Nächste Spiele", 1, 10, 5, key="football_next_n")
    with fc2:
        if team_id and st.button("Results laden", key="football_load_results", width="stretch"):
            try:
                st.session_state.football_recent_fixtures = service.get_recent_fixtures(
                    team_id, last_count=5, username=username,
                )
            except FootballAPIError as exc:
                st.error(str(exc))

    for label, key in (
        ("Anstehend", "football_upcoming_fixtures"),
        ("Ergebnisse", "football_recent_fixtures"),
    ):
        rows = st.session_state.get(key) or []
        if rows:
            st.caption(label)
            for item in rows[:8]:
                st.write(fixture_label(item))

    league_id = st.number_input("Liga-ID (Standings)", min_value=1, value=39, key="fb_league_id")
    if st.button("Standings laden", key="football_load_standings"):
        try:
            st.session_state.football_standings = service.get_standings(
                int(league_id), username=username,
            )
        except FootballAPIError as exc:
            st.error(str(exc))
    if st.session_state.get("football_standings"):
        with st.expander("Tabelle", expanded=False):
            st.json(st.session_state.football_standings)

    st.divider()
    st.markdown("#### Pro — Live, H2H, Stats, Predictions")

    def _live_block():
        if st.button("Live Scores", key="football_refresh_live", width="stretch"):
            try:
                st.session_state.football_live_fixtures = service.get_live_fixtures(
                    username=username,
                )
            except FootballAPIError as exc:
                st.error(str(exc))
        for item in (st.session_state.get("football_live_fixtures") or [])[:10]:
            h, a = fixture_team_names(item)
            g = item.get("goals") or {}
            st.write(f"**{h}** {g.get('home','-')} : {g.get('away','-')} **{a}**")

    gated_api_block(
        "api_live_scores",
        feature_label("api_live_scores"),
        "Live-Spiele weltweit",
        _live_block,
    )

    if team_id:
        def _h2h_block():
            opp = st.text_input("Gegner Team-ID", key="fb_opp_team_id")
            if st.button("H2H laden", key="football_load_h2h"):
                try:
                    st.session_state.football_h2h = service.get_head_to_head(
                        team_id, int(opp), username=username,
                    )
                except FootballAPIError as exc:
                    st.error(str(exc))
            for row in st.session_state.get("football_h2h") or []:
                st.write(fixture_label(row))

        gated_api_block(
            "api_head_to_head",
            "Head-to-Head",
            "Direktvergleich zweier Teams",
            _h2h_block,
        )

    st.divider()
    st.markdown("#### Elite — Multi-League & erweitert")

    def _multi_league_block():
        q = st.text_input("Liga suchen", key="fb_league_search")
        if st.button("Ligen suchen", key="fb_search_leagues"):
            try:
                st.session_state.football_leagues = service.search_leagues(
                    q, username=username,
                )
            except FootballAPIError as exc:
                st.error(str(exc))
        for row in (st.session_state.get("football_leagues") or [])[:8]:
            league = row.get("league") or {}
            st.write(f"{league.get('name')} ({league.get('country')})")

    gated_api_block(
        "api_multi_league",
        "Multi-League Monitoring",
        "Mehrere Ligen parallel durchsuchen",
        _multi_league_block,
    )

    st.caption("Player Stats, Injuries & Predictions — ab Football Pro.")


# =========================================================
# AI CONTENT UI
# =========================================================

def render_football_ai_engine(summary: dict) -> None:
    project = active_project()
    plan = summary.get("plan", "none")

    if plan == "none":
        st.warning(
            "Kein Football Premium Plan aktiv. "
            "Starter ab 19,99€ — Pro für Matchday Engine — Elite für Live API."
        )
        if st.button("Football Pläne vergleichen", key="fb_ai_go_premium", width="stretch"):
            open_premium()
        st.divider()

    top1, top2, top3, top4 = st.columns(4)

    with top1:
        st.metric("Platforms", "4")

    with top2:
        st.metric("Content Types", "10+")

    with top3:
        min_plan = "Pro" if summary["tier"] >= 2 else ("Starter" if summary["tier"] >= 1 else "—")
        st.metric("Matchday Engine", min_plan)

    with top4:
        st.metric("AI heute", summary.get("ai_used", 0))

    render_feature_matrix(summary)
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

        can_preview, _, _ = can_access_feature(
            current_username(), "ai_match_preview", session_football_plan(),
        )
        can_summary, _, _ = can_access_feature(
            current_username(), "ai_match_summary", session_football_plan(),
        )

        generate_summary = st.button(
            "Simple AI Match Summary (Starter)",
            width="stretch",
            disabled=not can_summary,
        )
        generate = st.button(
            "Multi Platform Matchday Package (Pro+)",
            width="stretch",
            disabled=not can_preview,
        )
        if not can_preview and plan != "none":
            st.caption("Matchday Package ab Football Pro.")

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

    if generate_summary:
        if not club or not opponent:
            st.warning("Bitte Club und Gegner eingeben.")
            return
        try:
            consume_action(current_username(), "match_recap", session_football_plan())
        except FootballGateError as exc:
            st.error(str(exc))
            return
        with st.spinner("Erstelle Match Summary..."):
            summary_text = generate_matchday_package(club, opponent, platform, tone)[:2500]
        st.subheader("AI Match Summary")
        st.markdown(summary_text)
        return

    if generate:
        if not club or not opponent:
            st.warning("Bitte Club und Gegner eingeben.")
            return

        ok, gate_msg = can_run_action(
            current_username(),
            "matchday_package",
            session_football_plan(),
        )
        if not ok:
            st.error(gate_msg)
            if st.button("Plan upgraden", key="fb_upgrade_matchday"):
                open_premium()
            return

        try:
            consume_action(
                current_username(),
                "matchday_package",
                session_football_plan(),
            )
        except FootballGateError as exc:
            st.error(str(exc))
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
            ok, gate_msg = can_run_action(
                current_username(),
                "optimized_package",
                session_football_plan(),
            )
            if not ok:
                st.error(gate_msg)
                return
            try:
                consume_action(
                    current_username(),
                    "optimized_package",
                    session_football_plan(),
                )
            except FootballGateError as exc:
                st.error(str(exc))
                return

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

    football_css()

    summary = usage_summary(current_username(), session_football_plan())

    render_page_hero(
        "Football Intelligence",
        "Starter · Pro · Elite",
        "Stufenweise API & AI: Starter (Basis-Daten + Summary), Pro (Predictions, H2H, Reels-Export), "
        "Elite (Multi-League, Automation, hohe Limits). Gecacht — keine Dauer-Polls.",
    )
    st.caption(f"Aktiver Plan: **{summary['plan_label']}**")

    project = active_project()
    if project:
        st.success(f"Aktives Projekt: {project.get('title')}")
    else:
        st.info("Kein aktives Projekt. AI-Ergebnisse werden ohne Projekt-Memory erzeugt.")

    render_plan_status()
    st.divider()

    tab_live, tab_ai, tab_plans = st.tabs(
        ["Daten & API", "AI Content Engine", "Dein Plan"]
    )

    with tab_live:
        render_football_live_data(summary)

    with tab_ai:
        render_football_ai_engine(summary)

    with tab_plans:
        render_feature_matrix(summary)
        st.divider()
        st.subheader("Football Premium Stufen")
        for key in ("football_starter", "football_pro", "football_elite"):
            plan = FOOTBALL_PLANS[key]
            with st.container(border=True):
                st.markdown(f"### {plan.get('label')} — {plan.get('price')}")
                st.write(plan.get("description", ""))
                api_note = (
                    "Live API inklusive"
                    if plan.get("live_api_access")
                    else "Kein Live-API (nur AI)"
                )
                st.caption(
                    f"{plan.get('ai_actions', 0):,} AI Actions · {api_note}".replace(",", ".")
                )
                for item in plan.get("highlights", []):
                    st.write(f"✓ {item}")
                if summary.get("plan") == key:
                    st.success("Dein aktueller Plan")
                elif st.button(f"{plan.get('label')} wählen", key=f"fb_pick_{key}"):
                    open_premium()
