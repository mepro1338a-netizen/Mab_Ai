import html
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
from ui.football_ui import (
    inject_football_ui_css,
    render_ai_module_preview,
    render_ai_pipeline_header,
    render_command_hero,
    render_content_package,
    render_export_bar,
    render_fixture_cards,
    render_league_results,
    render_match_banner,
    render_current_plan_banner,
    render_mesh_usage_bar,
    render_odds_dashboard,
    render_plan_card_html,
    render_odds_market_table,
    render_output_zone_end,
    render_output_zone_start,
    render_prediction_card,
    render_saas_legal,
    render_section_header,
    render_popular_leagues,
    render_standings_table,
    render_stat_row,
    render_summary_output,
    render_team_results,
    render_thumbnail_package,
    render_viral_intelligence,
    render_workflow_pipeline,
    POPULAR_LEAGUES,
)
from ui.premium_foundation import (
    render_feature_grid,
    render_upgrade_card,
)
from ui.football_premium import inject_football_premium_css
from pages.football_hub import (
    render_tab_automation,
    render_tab_betting_ai,
    render_tab_live_intel,
    render_tab_match_preview,
    render_tab_viral_studio,
)
from ui.prompt_ui import prompt_text_input
from services.football_odds import (
    calculate_tip_odds,
    fixture_options_from_list,
    parse_fixture_odds_payload,
    parse_prediction_insights,
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
    """Page-only styles — never override global sidebar (see ui_core)."""
    from ui.premium_foundation import BETA_GLOBAL_CSS
    from ui.styles import MB_THEME_VARS, inject_css, page_layout_css

    inject_football_ui_css()
    inject_football_premium_css()
    inject_css(MB_THEME_VARS + page_layout_css(1280, 88, 48) + BETA_GLOBAL_CSS + """
.fb-page-marker { display: none; }
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
    api_val = (
        f"{summary['api_used']:,}".replace(",", ".")
        if summary["live_api"]
        else "—"
    )
    api_hint = (
        f"Limit {summary['api_limit']:,}".replace(",", ".")
        if summary["live_api"]
        else "Football Plan aktivieren"
    )
    render_stat_row([
        ("Football Plan", summary["plan_label"], "Aktive Stufe"),
        ("AI Analysen", f"{summary['ai_used']}/{ai_lim_txt}", "Heute verbraucht"),
        ("API Mesh", api_val, api_hint),
        ("Tier Level", str(summary["tier"] or "—"), "Feature-Stufe 0–3"),
    ])
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
        "analysis": "Analyse",
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
        "tiktok hook": "TikTok Hook",
        "tiktok caption": "TikTok Caption",
        "instagram reel caption": "Instagram Caption",
        "twitter thread": "Twitter Thread",
        "x/twitter thread": "Twitter Thread",
        "youtube shorts title": "YouTube Title",
        "youtube shorts description": "YouTube Description",
        "thumbnail prompt": "Thumbnail Prompt",
        "hashtags": "Hashtags",
        "cta": "CTA",
        "posting strategy": "Posting Strategy",
    }

    sections = {title: "" for title in section_map.values()}

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
        sections["TikTok Hook"] = result

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

def render_full_export(result, filename="mabyte_matchday_package.txt"):
    render_export_bar("Full Package Export")
    st.download_button(
        "↓ Komplettes Matchday Package",
        data=result.encode("utf-8"),
        file_name=filename,
        mime="text/plain",
        key=f"dl_{safe_filename(filename)}",
        width="stretch",
    )


def render_ai_package_results(
    result: str,
    club: str,
    opponent: str,
    platform: str,
    tone: str,
    project,
    *,
    key_prefix: str = "fb_pkg",
    badge: str = "Matchday Content Package",
    show_thumbnails: bool = True,
    show_viral: bool = True,
    show_improve: bool = True,
    export_name: str = "mabyte_matchday_package.txt",
) -> None:
    """Professional AI output — cards, viral ring, thumbnails."""
    render_section_header(badge, f"{club} vs {opponent} · {platform} · {tone}")
    render_match_banner(club, opponent, platform, tone, badge=badge)

    sections = split_sections(result)
    render_content_package(sections, key_prefix=key_prefix)
    render_full_export(result, filename=export_name)

    if show_thumbnails:
        with st.spinner("Thumbnail Intelligence…"):
            thumbnails = generate_thumbnail_system(club, opponent)
        render_thumbnail_package(thumbnails)
        st.download_button(
            "↓ Thumbnail System",
            data=thumbnails.encode("utf-8"),
            file_name="mabyte_thumbnail_system.txt",
            mime="text/plain",
            key=f"{key_prefix}_thumb_dl",
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

    if show_viral:
        with st.spinner("Viral Intelligence…"):
            analysis = analyze_viral_score(result)
        render_viral_intelligence(
            analysis.get("score", 0),
            analysis.get("feedback", ""),
        )

    if show_improve:
        improve = st.button(
            "Package optimieren (Viral Boost)",
            width="stretch",
            key=f"{key_prefix}_improve",
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
            with st.spinner("Optimiere Viralität…"):
                improved = improve_package(result)
            st.session_state.fb_ai_package = improved
            st.session_state.fb_ai_badge = "Optimized Package · Viral Boost"
            st.rerun()

    with st.expander("Technische Rohdaten", expanded=False):
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


def _league_options() -> dict[str, int]:
    opts: dict[str, int] = {}
    for lg in POPULAR_LEAGUES:
        opts[f"{lg['name']} — {lg['country']}"] = int(lg["id"])
    for row in st.session_state.get("football_leagues") or []:
        league = row.get("league") or {}
        lid = league.get("id")
        name = league.get("name")
        if lid and name:
            country = league.get("country") or ""
            opts[f"{name} — {country}"] = int(lid)
    return opts


def _fixture_pick_options() -> dict[str, int]:
    """Merge loaded fixtures for Elite Odds Lab picker."""
    combined: list = []
    for key in (
        "football_upcoming_fixtures",
        "football_league_upcoming",
        "football_live_fixtures",
        "football_recent_fixtures",
    ):
        combined.extend(st.session_state.get(key) or [])
    return fixture_options_from_list(combined)


def render_football_live_data(summary: dict) -> None:
    if summary.get("plan") == "none":
        render_upgrade_card(
            "Football Intelligence freischalten",
            "Live-Daten, Tabellen und Match Center ab Football Starter.",
            "football_starter",
            button_key="fb_need_starter",
            on_upgrade=open_premium,
        )
        return

    service = get_football_service()
    username = current_username()

    if not service.is_configured():
        st.markdown(
            """
<div class="fb-empty">
    Live-Daten werden gerade angebunden. Dein Plan ist aktiv —
    versuche es in wenigen Minuten erneut oder kontaktiere den Support.
</div>
            """,
            unsafe_allow_html=True,
        )
        return

    render_mesh_usage_bar(int(summary["api_used"]), int(summary["api_limit"]))
    render_workflow_pipeline([
        ("Team finden", "active"),
        ("Liga wählen", "pending"),
        ("Spiele laden", "pending"),
        ("Live Center", "pending"),
    ])

    tab_teams, tab_leagues, tab_matches, tab_live = st.tabs(
        ["Teams", "Ligen", "Match Center", "Live"]
    )

    with tab_teams:
        render_section_header(
            "Team Intelligence",
            "Suche Clubs weltweit — Spielplan, Ergebnisse und Vergleiche.",
        )
        c1, c2 = st.columns([4, 1])
        with c1:
            st.text_input(
                "Team suchen",
                placeholder="Arsenal, Bayern, Real Madrid, Barca…",
                key="football_team_search_query",
                label_visibility="collapsed",
            )
        with c2:
            if st.button("Suchen", key="football_search_teams_btn", width="stretch"):
                q = st.session_state.get("football_team_search_query", "").strip()
                if len(q) < 2:
                    st.warning("Mindestens 2 Zeichen.")
                else:
                    try:
                        with st.spinner("Teams werden geladen…"):
                            st.session_state.football_team_results = service.search_teams(
                                q, username=username,
                            )
                    except FootballAPIError as exc:
                        st.error(str(exc))

        teams = st.session_state.get("football_team_results") or []
        if teams:
            render_team_results(teams)
        team_id = _pick_team_id()

        if team_id:
            a1, a2, a3 = st.columns(3)
            with a1:
                n = st.slider("Nächste", 1, 12, 6, key="football_next_n")
            with a2:
                if st.button("Anstehend laden", key="football_load_fixtures", width="stretch"):
                    try:
                        st.session_state.football_upcoming_fixtures = service.get_upcoming_fixtures(
                            team_id, next_count=n, username=username,
                        )
                    except FootballAPIError as exc:
                        st.error(str(exc))
            with a3:
                if st.button("Ergebnisse laden", key="football_load_results", width="stretch"):
                    try:
                        st.session_state.football_recent_fixtures = service.get_recent_fixtures(
                            team_id, last_count=6, username=username,
                        )
                    except FootballAPIError as exc:
                        st.error(str(exc))

            st.markdown("**Anstehende Spiele**")
            render_fixture_cards(
                st.session_state.get("football_upcoming_fixtures") or [],
                empty_msg="Team wählen und «Anstehend laden».",
            )
            st.markdown("**Letzte Ergebnisse**")
            render_fixture_cards(
                st.session_state.get("football_recent_fixtures") or [],
                empty_msg="«Ergebnisse laden» für Historie.",
            )

            def _h2h_block():
                opp_teams = st.session_state.get("football_team_results") or []
                opp_opts: dict[str, int] = {}
                for row in opp_teams:
                    t = row.get("team") or {}
                    tid = t.get("id")
                    if tid and int(tid) != team_id:
                        opp_opts[team_display_name(row)] = int(tid)
                if opp_opts:
                    opp_name = st.selectbox(
                        "Gegner wählen",
                        list(opp_opts.keys()),
                        key="fb_h2h_opp_pick",
                    )
                    opp_id = opp_opts.get(opp_name)
                else:
                    opp_id = None
                    st.caption("Zuerst zwei Teams suchen — oder Gegner-ID unten.")
                    raw = st.text_input(
                        "Gegner-ID (optional)",
                        key="fb_opp_team_id",
                        placeholder="Nur falls nötig",
                    )
                    if raw:
                        try:
                            opp_id = int(raw)
                        except ValueError:
                            st.warning("Ungültige ID.")
                if st.button("Direktvergleich laden", key="football_load_h2h", width="stretch"):
                    if not opp_id:
                        st.warning("Gegner auswählen.")
                        return
                    try:
                        st.session_state.football_h2h = service.get_head_to_head(
                            team_id, int(opp_id), username=username,
                        )
                    except (FootballAPIError, ValueError) as exc:
                        st.error(str(exc))
                render_fixture_cards(
                    st.session_state.get("football_h2h") or [],
                    empty_msg="Direktvergleich starten.",
                )

            gated_api_block(
                "api_head_to_head",
                "Head-to-Head",
                "Historischer Direktvergleich — Football Pro",
                _h2h_block,
            )

    with tab_leagues:
        render_section_header(
            "Liga Intelligence",
            "Top-Ligen, Tabellen und Spielpläne — ohne technische IDs.",
        )
        render_popular_leagues()

        lc1, lc2 = st.columns([3, 1])
        with lc1:
            st.text_input(
                "Liga suchen",
                placeholder="Premier, Bundesliga, Champions…",
                key="fb_league_search",
                label_visibility="collapsed",
            )
        with lc2:
            if st.button("Suchen", key="fb_search_leagues", width="stretch"):
                q = st.session_state.get("fb_league_search", "").strip()
                if len(q) < 2:
                    st.warning("Mindestens 2 Zeichen.")
                else:
                    try:
                        st.session_state.football_leagues = service.search_leagues(
                            q, username=username,
                        )
                    except FootballAPIError as exc:
                        st.error(str(exc))

        if st.session_state.get("football_leagues"):
            render_league_results(st.session_state.get("football_leagues") or [])

        league_opts = _league_options()
        if league_opts:
            pick = st.selectbox(
                "Aktive Liga",
                list(league_opts.keys()),
                key="fb_league_pick",
            )
            st.session_state.fb_active_league_id = league_opts.get(pick, 39)
        else:
            st.session_state.fb_active_league_id = 39

        league_id = int(st.session_state.get("fb_active_league_id") or 39)
        st.caption(f"Aktive Liga ausgewählt · Daten für Saison {st.session_state.get('fb_season', 'aktuell')}")
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Tabelle", key="football_load_standings", width="stretch"):
                try:
                    st.session_state.football_standings = service.get_standings(
                        league_id, username=username,
                    )
                except FootballAPIError as exc:
                    st.error(str(exc))
        with b2:
            if st.button("Kommende Spiele", key="fb_league_upcoming", width="stretch"):
                try:
                    st.session_state.football_league_upcoming = (
                        service.get_league_upcoming_fixtures(
                            league_id, next_count=12, username=username,
                        )
                    )
                except FootballAPIError as exc:
                    st.error(str(exc))
        with b3:
            if st.button("Letzte Spiele", key="fb_league_recent", width="stretch"):
                try:
                    st.session_state.football_league_recent = (
                        service.get_league_recent_fixtures(
                            league_id, last_count=12, username=username,
                        )
                    )
                except FootballAPIError as exc:
                    st.error(str(exc))

        if st.session_state.get("football_standings"):
            st.markdown("**Tabelle**")
            render_standings_table(st.session_state.get("football_standings") or [])
        st.markdown("**Kommende Liga-Spiele**")
        render_fixture_cards(
            st.session_state.get("football_league_upcoming") or [],
            empty_msg="Liga wählen → «Kommende Spiele».",
        )
        st.markdown("**Letzte Liga-Spiele**")
        render_fixture_cards(
            st.session_state.get("football_league_recent") or [],
            empty_msg="«Letzte Spiele» für Ergebnisse.",
        )

        gated_api_block(
            "api_multi_league",
            "Multi-League Hub",
            "Mehrere Ligen parallel — Football Elite",
            lambda: render_league_results(st.session_state.get("football_leagues") or []),
        )

    with tab_matches:
        render_section_header(
            "Match Center",
            "Alle geladenen Spiele auf einen Blick — sortiert nach Relevanz.",
        )
        upcoming = st.session_state.get("football_upcoming_fixtures") or []
        league_up = st.session_state.get("football_league_upcoming") or []
        recent = st.session_state.get("football_recent_fixtures") or []
        if upcoming:
            st.markdown("**Anstehend**")
            render_fixture_cards(upcoming)
        if league_up:
            st.markdown("**Liga · Kommend**")
            render_fixture_cards(league_up)
        if recent:
            st.markdown("**Ergebnisse**")
            render_fixture_cards(recent)
        if not (upcoming or league_up or recent):
            render_fixture_cards(
                [],
                empty_msg="Lade Spiele unter Teams oder Ligen — sie erscheinen hier zentral.",
            )

    with tab_live:
        render_section_header(
            "Live Center",
            "Echtzeit-Spiele — intelligent gecacht für Performance.",
        )

        def _live_block():
            if st.button("Live aktualisieren", key="football_refresh_live", width="stretch"):
                try:
                    with st.spinner("Live-Spiele werden geladen…"):
                        st.session_state.football_live_fixtures = service.get_live_fixtures(
                            username=username,
                        )
                except FootballAPIError as exc:
                    st.error(str(exc))
            live_rows = st.session_state.get("football_live_fixtures") or []
            if live_rows:
                st.markdown(
                    f'<span class="fb-league-chip"><strong>{len(live_rows)}</strong> Live-Spiele</span>',
                    unsafe_allow_html=True,
                )
            render_fixture_cards(
                live_rows,
                empty_msg="Keine Live-Spiele — Aktualisieren drücken.",
            )

        gated_api_block(
            "api_live_scores",
            "Live Scores",
            "Weltweite Live-Spiele — Football Pro",
            _live_block,
        )


# =========================================================
# AI CONTENT UI
# =========================================================

def render_football_ai_engine(summary: dict) -> None:
    project = active_project()
    plan = summary.get("plan", "none")

    render_section_header(
        "Creator Studio",
        "Professionelle Matchday-Inhalte für TikTok, Instagram, X und YouTube.",
    )

    if plan == "none":
        st.warning("Football Premium erforderlich — Creator Studio ab Starter.")
        if st.button("Pläne ansehen", key="fb_ai_go_premium", width="stretch"):
            open_premium()
        st.divider()

    min_plan = "Pro" if summary["tier"] >= 2 else ("Starter" if summary["tier"] >= 1 else "—")
    ai_lim = summary.get("ai_limit")
    ai_lim_txt = str(ai_lim) if isinstance(ai_lim, int) else str(ai_lim)
    render_stat_row([
        ("Creator Studio", min_plan, "Deine Stufe"),
        ("AI heute", f"{summary.get('ai_used', 0)}/{ai_lim_txt}", "Analysen"),
        ("Module", "10+", "Multi-Platform"),
        ("Export", "TXT", "Sofort nutzbar"),
    ])

    with st.expander("Enthaltene Features", expanded=False):
        render_feature_matrix(summary)

    st.markdown('<div class="fb-ai-studio">', unsafe_allow_html=True)
    left, right = st.columns([1.05, 1], gap="large")

    with left:
        st.markdown(
            '<div class="fb-scanline" style="margin-bottom:14px;">Match Setup</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            club = st.text_input(
                "Club",
                placeholder="Arsenal",
                key="football_ai_club_input",
            )
        with c2:
            opponent = st.text_input(
                "Gegner",
                placeholder="Manchester City",
                key="football_ai_opponent_input",
            )

        p1, p2 = st.columns(2)
        with p1:
            platform = st.selectbox(
                "Hauptplattform",
                ["TikTok", "Instagram", "X/Twitter", "YouTube Shorts"],
                key="football_ai_platform",
            )
        with p2:
            tone = st.selectbox(
                "Content Tone",
                ["Viral", "Aggressive", "Emotional", "Funny", "Professional", "Tactical"],
                key="football_ai_tone",
            )

        can_preview, _, _ = can_access_feature(
            current_username(), "ai_match_preview", session_football_plan(),
        )
        can_summary, _, _ = can_access_feature(
            current_username(), "ai_match_summary", session_football_plan(),
        )

        b1, b2 = st.columns(2)
        with b1:
            generate_summary = st.button(
                "Match Summary",
                width="stretch",
                disabled=not can_summary,
                key="fb_btn_summary",
            )
        with b2:
            generate = st.button(
                "Matchday Package",
                width="stretch",
                disabled=not can_preview,
                key="fb_btn_package",
            )
        if not can_preview and plan != "none":
            st.caption("Volles Package ab Football Pro.")

    with right:
        render_ai_module_preview()
    st.markdown("</div>", unsafe_allow_html=True)
    render_saas_legal(
        "Generierte Inhalte sind Entwürfe für dein Creator-Business — "
        "prüfe Fakten vor Veröffentlichung."
    )

    if generate_summary:
        if not club or not opponent:
            st.warning("Bitte Club und Gegner eingeben.")
            return
        try:
            consume_action(current_username(), "match_recap", session_football_plan())
        except FootballGateError as exc:
            st.error(str(exc))
            return
        with st.spinner("AI Match Summary wird erstellt…"):
            summary_text = generate_matchday_package(club, opponent, platform, tone)[:2500]
        render_summary_output(summary_text, club, opponent)
        st.download_button(
            "↓ Summary herunterladen",
            data=summary_text.encode("utf-8"),
            file_name=f"mabyte_summary_{safe_filename(club)}_vs_{safe_filename(opponent)}.txt",
            mime="text/plain",
            key="fb_summary_dl",
            width="stretch",
        )
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

        with st.spinner("MaByte generiert Multi-Platform Matchday Package…"):
            result = generate_matchday_package(club, opponent, platform, tone)

        st.session_state.fb_ai_package = result
        st.session_state.fb_ai_meta = {
            "club": club,
            "opponent": opponent,
            "platform": platform,
            "tone": tone,
        }
        st.session_state.fb_ai_badge = "Matchday Content Package"

    pkg = st.session_state.get("fb_ai_package")
    meta = st.session_state.get("fb_ai_meta") or {}
    if pkg and meta:
        st.divider()
        render_output_zone_start()
        render_ai_pipeline_header()
        _, clear = st.columns([5, 1])
        with clear:
            if st.button("Neues Match", key="fb_clear_pkg", width="stretch"):
                for k in ("fb_ai_package", "fb_ai_meta", "fb_ai_badge"):
                    st.session_state.pop(k, None)
                st.rerun()
        render_ai_package_results(
            pkg,
            meta.get("club", club),
            meta.get("opponent", opponent),
            meta.get("platform", platform),
            meta.get("tone", tone),
            project,
            key_prefix="fb_pkg_main",
            badge=st.session_state.get("fb_ai_badge", "Matchday Content Package"),
        )
        render_output_zone_end()


def render_football_odds_calculator(summary: dict) -> None:
    render_section_header(
        "Odds Lab",
        "Elite Match Intelligence + Value-Analyse für Selbstständige & Analysten.",
    )
    user = current_username()
    plan = session_football_plan()
    ok, _, need = can_access_feature(user, "ai_betting_intelligence", plan)

    if not ok:
        render_upgrade_card(
            "Betting Intelligence — Football Pro",
            "Live-Marktdaten, Prognosen und mathematische Value-Bet-Analyse.",
            need,
            button_key="fb_odds_upgrade",
            on_upgrade=open_premium,
        )
        return

    render_saas_legal(
        "MaByte liefert nur mathematische Analysen — keine Wettberatung, keine Wetten, kein Echtgeld. "
        "Alle Entscheidungen liegen bei dir."
    )

    service = get_football_service()
    username = current_username()
    intel_col, calc_col = st.columns([1.05, 1], gap="large")

    with intel_col:
        st.markdown(
            '<div class="fb-scanline" style="margin-bottom:10px;">Elite Data Feed</div>',
            unsafe_allow_html=True,
        )
        fx_opts = _fixture_pick_options()
        fixture_id: int | None = None

        if fx_opts:
            pick_label = st.selectbox(
                "Spiel aus Match Center",
                ["—"] + list(fx_opts.keys()),
                key="fb_odds_fixture_pick",
            )
            if pick_label and pick_label != "—":
                fixture_id = fx_opts[pick_label]
        else:
            st.caption("Tipp: Lade zuerst Spiele im Data Mesh — dann erscheinen sie hier.")

        manual = st.number_input(
            "Spiel-Referenz (optional)",
            min_value=0,
            value=0,
            step=1,
            key="fb_odds_fixture_manual",
            help="Nur wenn das Spiel nicht in der Liste ist.",
        )
        if manual > 0:
            fixture_id = int(manual)

        if st.button("Elite Daten laden", key="fb_odds_load_elite", width="stretch"):
            if not fixture_id:
                st.warning("Spiel wählen oder Referenz eingeben.")
            elif not service.is_configured():
                st.error("Live-Daten temporär nicht verfügbar.")
            else:
                try:
                    with st.spinner("Lade Marktdaten & Prognose…"):
                        st.session_state.fb_odds_markets = parse_fixture_odds_payload(
                            service.get_fixture_odds(fixture_id, username=username)
                        )
                        pred_rows = service.get_fixture_predictions(
                            fixture_id, username=username,
                        )
                        if pred_rows:
                            st.session_state.fb_odds_prediction = parse_prediction_insights(
                                pred_rows[0]
                            )
                        else:
                            st.session_state.pop("fb_odds_prediction", None)
                        st.session_state.fb_odds_fixture_id = fixture_id
                except FootballAPIError as exc:
                    st.error(str(exc))

        if st.session_state.get("fb_odds_prediction"):
            render_prediction_card(st.session_state.fb_odds_prediction)
            ins = st.session_state.fb_odds_prediction
            if ins.get("home_pct") is not None:
                st.session_state.fb_odds_suggest_prob = float(ins["home_pct"])

        markets = st.session_state.get("fb_odds_markets") or []
        if markets:
            render_odds_market_table(markets)
            labels = [m["label"] for m in markets]
            picked = st.selectbox(
                "Quote übernehmen",
                ["—"] + labels,
                key="fb_odds_market_pick",
            )
            if picked and picked != "—" and picked != st.session_state.get("fb_odds_last_pick"):
                for m in markets:
                    if m["label"] == picked:
                        st.session_state.fb_odds_prefill = float(m["odd"])
                        st.session_state.fb_odds_last_pick = picked
                        pred_ins = st.session_state.get("fb_odds_prediction") or {}
                        sel = (m.get("selection") or "").lower()
                        if "home" in sel and pred_ins.get("home_pct") is not None:
                            st.session_state.fb_odds_suggest_prob = float(pred_ins["home_pct"])
                        elif "away" in sel and pred_ins.get("away_pct") is not None:
                            st.session_state.fb_odds_suggest_prob = float(pred_ins["away_pct"])
                        elif "draw" in sel and pred_ins.get("draw_pct") is not None:
                            st.session_state.fb_odds_suggest_prob = float(pred_ins["draw_pct"])
                        st.rerun()
                        break

    with calc_col:
        st.markdown(
            '<div class="fb-scanline" style="margin-bottom:10px;">Value Rechner</div>',
            unsafe_allow_html=True,
        )
        default_odd = float(st.session_state.get("fb_odds_prefill", 2.10))
        default_prob = float(st.session_state.get("fb_odds_suggest_prob", 52.0))

        with st.form("fb_odds_form", border=False):
            c1, c2 = st.columns(2)
            with c1:
                odds = st.number_input(
                    "Quote (Dezimal)",
                    min_value=1.01,
                    value=default_odd,
                    step=0.01,
                    key="fb_odds_input_odd",
                )
            with c2:
                stake = st.number_input(
                    "Einsatz",
                    min_value=0.0,
                    value=10.0,
                    step=1.0,
                    key="fb_odds_input_stake",
                )
            prob = st.number_input(
                "Deine Gewinn-Wahrscheinlichkeit %",
                min_value=0.0,
                max_value=100.0,
                value=default_prob,
                step=0.5,
                key="fb_odds_input_prob",
            )
            match_note = prompt_text_input(
                placeholder="Optional: eigene Match-Notiz",
                label="Notiz",
                key="fb_odds_input_note",
            )
            calc = st.form_submit_button("Analyse starten", width="stretch")

    if calc:
        try:
            result = calculate_tip_odds(odds, stake, prob)
            st.session_state.fb_odds_result = result
            st.session_state.fb_odds_note = match_note
        except ValueError as exc:
            st.error(str(exc))

    result = st.session_state.get("fb_odds_result")
    if result:
        st.divider()
        render_output_zone_start()
        render_section_header("Analyse-Ergebnis", "Value, Edge, EV & Risiko auf einen Blick")
        render_odds_dashboard(result, st.session_state.get("fb_odds_note", ""))
        render_output_zone_end()


def render_football_plans_tab(summary: dict) -> None:
    """Subscription & plan comparison — SaaS pricing page."""
    render_section_header(
        "Dein Plan",
        "Übersicht, Limits und Upgrade — transparent für dein Business.",
    )

    plan_key = summary.get("plan") or "none"
    ai_lim = summary["ai_limit"]
    ai_lim_disp = str(ai_lim) if isinstance(ai_lim, int) else str(ai_lim)

    if plan_key != "none":
        render_current_plan_banner(
            summary["plan_label"],
            plan_key,
            ai_used=int(summary.get("ai_used") or 0),
            ai_limit=ai_lim_disp,
            api_used=int(summary.get("api_used") or 0),
            api_limit=int(summary.get("api_limit") or 0),
            live_api=bool(summary.get("live_api")),
        )
    else:
        st.markdown(
            """
<div class="fb-empty">
    Noch kein Football Premium aktiv — wähle eine Stufe und starte mit Live-Daten & Creator Studio.
</div>
            """,
            unsafe_allow_html=True,
        )

    render_workflow_pipeline([
        ("Plan wählen", "active" if plan_key == "none" else "done"),
        ("Features nutzen", "active" if plan_key != "none" else "pending"),
        ("Upgrade", "pending"),
    ])

    with st.expander("Deine Feature-Freigaben", expanded=plan_key != "none"):
        render_feature_matrix(summary)

    st.markdown(
        '<div class="fb-scanline" style="margin:18px 0 10px 0;">Football Premium Stufen</div>',
        unsafe_allow_html=True,
    )
    render_saas_legal(
        "Alle Preise monatlich kündbar. MaByte ist ein Analyse- und Creator-Tool — "
        "keine Wettplattform."
    )

    tiers = [
        ("football_starter", FOOTBALL_PLANS["football_starter"]),
        ("football_pro", FOOTBALL_PLANS["football_pro"]),
        ("football_elite", FOOTBALL_PLANS["football_elite"]),
    ]
    recommended = "football_pro"
    if plan_key == "football_starter":
        recommended = "football_pro"
    elif plan_key == "football_pro":
        recommended = "football_elite"
    elif plan_key == "football_elite":
        recommended = "football_elite"

    cols = st.columns(3, gap="medium")
    for col, (key, plan) in zip(cols, tiers):
        with col:
            render_plan_card_html(
                key,
                plan.get("label", key),
                plan.get("price", ""),
                plan.get("badge", ""),
                plan.get("description", ""),
                plan.get("highlights", []),
                daily_ai=int(plan.get("daily_ai_analyses") or 0),
                daily_api=int(plan.get("daily_api_requests") or 0),
                is_current=(plan_key == key),
                recommended=(key == recommended and plan_key != key),
            )
            if plan_key == key:
                st.markdown(
                    '<div class="fb-odds-verdict positive" style="text-align:center;margin-top:10px;">'
                    "Aktiver Plan</div>",
                    unsafe_allow_html=True,
                )
            elif plan_key == "none" or (
                plan_key == "football_starter" and key != "football_starter"
            ) or (plan_key == "football_pro" and key == "football_elite"):
                if st.button(
                    f"Upgrade · {plan.get('label', '')}",
                    key=f"fb_pick_{key}",
                    width="stretch",
                ):
                    open_premium()
            else:
                st.caption("Bereits in deiner Stufe enthalten oder höher.")

    if plan_key != "football_elite":
        st.divider()
        if st.button("Alle Pläne & Checkout im Premium Center", key="fb_plans_premium", width="stretch"):
            open_premium()


def render_football() -> None:
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()
        return

    football_css()
    st.markdown('<div class="fb-page fb-premium">', unsafe_allow_html=True)

    summary = usage_summary(current_username(), session_football_plan())
    api_line = (
        f"{summary['api_used']:,} / {summary['api_limit']:,} API".replace(",", ".")
        if summary.get("live_api")
        else "API nach Plan-Freischaltung"
    )

    render_command_hero(
        "Football Intelligence",
        "AI Plattform für Creator, Wett-Analysten & Fußball-Media — nicht nur Live Scores.",
        summary["plan_label"],
        api_line,
    )

    project = active_project()
    if project:
        st.markdown(
            f'<span class="fb-league-chip">Projekt <strong>{html.escape(str(project.get("title")))}</strong></span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="fb-league-chip">Kein Projekt-Memory aktiv</span>',
            unsafe_allow_html=True,
        )

    render_plan_status()
    st.divider()

    user = current_username()
    plan = session_football_plan()
    hub_kw = dict(summary=summary, username=user, session_plan=plan, open_premium=open_premium)

    tab_mesh, tab_live, tab_bet, tab_prev, tab_vir, tab_auto, tab_plan = st.tabs(
        [
            "Data Mesh",
            "Live Intel",
            "Betting AI",
            "Match Preview",
            "Viral Studio",
            "Automation",
            "Dein Plan",
        ]
    )

    with tab_mesh:
        render_football_live_data(summary)

    with tab_live:
        render_tab_live_intel(**hub_kw)

    with tab_bet:
        render_tab_betting_ai(**hub_kw)

    with tab_prev:
        render_tab_match_preview(**hub_kw)

    with tab_vir:
        render_tab_viral_studio(**hub_kw)

    with tab_auto:
        render_tab_automation(**hub_kw)

    with tab_plan:
        render_football_plans_tab(summary)

    st.markdown("</div>", unsafe_allow_html=True)
