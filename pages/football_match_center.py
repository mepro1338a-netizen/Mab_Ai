"""Live Match Center tab — professional live fixtures hub."""
from __future__ import annotations

import streamlit as st

from config import football_plan_rank
from services.football_access import (
    FootballAccessError,
    can_access_feature,
    can_run_action,
    consume_action,
)
from services.football_elite_live import EliteLiveIntelEngine, pro_preview_from_bundle
from services.football_leagues import CATEGORY_LABELS, LEAGUE_CATALOG, leagues_for_category
from services.football_match_center import fetch_live_center_payload, fetch_match_detail
from services.football_service import FootballAPIError, get_football_service
from ui.football_components import inject_football_components_css, render_elite_live_dashboard
from ui.football_match_center import (
    fixture_select_options,
    inject_match_center_css,
    render_category_chips,
    render_match_detail_panel,
    render_match_section,
    render_mc_header,
)
from ui.premium_foundation import render_upgrade_card


def _all_league_options() -> list[dict]:
    seen: set[int] = set()
    out: list[dict] = []
    for lgs in LEAGUE_CATALOG.values():
        for lg in lgs:
            lid = int(lg["id"])
            if lid in seen:
                continue
            seen.add(lid)
            out.append(lg)
    return sorted(out, key=lambda x: x["name"])


def _init_session() -> None:
    defaults = {
        "fb_mc_category": "deutschland",
        "fb_mc_favorites": [],
        "fb_mc_payload": None,
        "fb_mc_filter_sig": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _filter_signature(category: str, league_filter: set[int] | None, country: str) -> str:
    ids = sorted(league_filter or [])
    return f"{category}|{','.join(map(str, ids))}|{country.strip().lower()}"


def _all_fixtures_from_payload(payload: dict) -> list:
    sections = payload.get("sections") or {}
    out: list = []
    for key in ("live_now", "later_today", "finished_today", "tomorrow"):
        out.extend(sections.get(key) or [])
    return out


def render_tab_live_match_center(
    summary: dict,
    *,
    username: str,
    session_plan: str,
    open_premium,
) -> None:
    _init_session()
    inject_match_center_css()
    inject_football_components_css()

    rank = football_plan_rank(session_plan or "none")
    if rank < 1 or session_plan in ("none", ""):
        render_upgrade_card(
            "Live Match Center",
            "Live-Spiele, Ligen und Match Details ab Football Starter.",
            "football_starter",
            button_key="fb_mc_starter_up",
            on_upgrade=open_premium,
        )
        return

    service = get_football_service()
    if not service.is_configured():
        st.markdown(
            '<div class="fb-empty">Football API wird vorbereitet — FOOTBALL_API_KEY fehlt noch. '
            "Dein Plan bleibt aktiv.</div>",
            unsafe_allow_html=True,
        )
        return

    elite_ok, _, _ = can_access_feature(username, "ai_elite_live_intelligence", session_plan)
    pro_ok, _, pro_need = can_access_feature(username, "ai_live_match_intelligence", session_plan)

    cats = list(CATEGORY_LABELS.keys())
    cat_labels = [CATEGORY_LABELS[c] for c in cats]
    try:
        cat_idx = cats.index(st.session_state.fb_mc_category)
    except ValueError:
        cat_idx = 0
    picked_cat = st.radio(
        "Liga-Bereich",
        cat_labels,
        index=cat_idx,
        horizontal=True,
        key="fb_mc_cat_radio",
        label_visibility="collapsed",
    )
    st.session_state.fb_mc_category = cats[cat_labels.index(picked_cat)]
    render_category_chips(CATEGORY_LABELS, st.session_state.fb_mc_category)

    favs: list[int] = list(st.session_state.fb_mc_favorites or [])
    category = st.session_state.fb_mc_category
    leagues = leagues_for_category(category, favorites=favs)

    if category == "favoriten" and not leagues:
        st.info("Noch keine Favoriten — unten im Expander Ligen auswählen und speichern.")

    league_names = [lg["name"] for lg in leagues]
    selected_leagues = st.multiselect(
        "Ligen filtern (leer = alle in Kategorie)",
        league_names,
        key=f"fb_mc_league_multiselect_{category}",
    )
    country_filter = st.text_input(
        "Land filtern (optional, z. B. Germany)",
        value="",
        key="fb_mc_country_filter",
        placeholder="Leer = alle Länder",
    )

    if selected_leagues:
        name_to_id = {lg["name"]: int(lg["id"]) for lg in leagues}
        league_filter: set[int] | None = {
            name_to_id[n] for n in selected_leagues if n in name_to_id
        }
    elif leagues:
        league_filter = {int(lg["id"]) for lg in leagues}
    else:
        league_filter = set()

    sig = _filter_signature(category, league_filter, country_filter)
    if sig != st.session_state.fb_mc_filter_sig:
        st.session_state.fb_mc_filter_sig = sig
        st.session_state.fb_mc_payload = None

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        refresh = st.button(
            "Live Center aktualisieren",
            type="primary",
            key="fb_mc_refresh",
            width="stretch",
        )
    with c2:
        st.caption("Live: 60s Cache")
    with c3:
        st.caption("Fixtures: 10min Cache")

    if refresh or st.session_state.fb_mc_payload is None:
        if category == "favoriten" and not league_filter:
            st.session_state.fb_mc_payload = {
                "configured": True,
                "errors": [],
                "sections": {
                    "live_now": [],
                    "later_today": [],
                    "finished_today": [],
                    "tomorrow": [],
                },
                "total_fixtures": 0,
            }
        else:
            with st.spinner("Spiele werden geladen…"):
                try:
                    st.session_state.fb_mc_payload = fetch_live_center_payload(
                        service,
                        username=username,
                        league_filter=league_filter or None,
                        country_filter=country_filter,
                    )
                except FootballAPIError as exc:
                    st.error(str(exc))
                    return

    payload = st.session_state.fb_mc_payload or {}
    for err in payload.get("errors") or []:
        st.warning(err)

    sections = payload.get("sections") or {}
    live_n = len(sections.get("live_now") or [])
    today_n = live_n + len(sections.get("later_today") or []) + len(
        sections.get("finished_today") or []
    )
    render_mc_header(
        live_count=live_n,
        today_count=today_n,
        api_used=int(summary.get("api_used") or 0),
        api_limit=int(summary.get("api_limit") or 0),
    )

    render_match_section(
        "Heute live · Jetzt",
        sections.get("live_now") or [],
        empty="Keine Live-Spiele in den gewählten Ligen.",
    )
    render_match_section(
        "Später heute",
        sections.get("later_today") or [],
        empty="Keine weiteren Spiele heute.",
    )
    render_match_section(
        "Beendet heute",
        sections.get("finished_today") or [],
        empty="Noch keine Ergebnisse heute.",
    )
    render_match_section(
        "Morgen",
        sections.get("tomorrow") or [],
        empty="Keine Spiele morgen in der Auswahl.",
    )

    st.divider()
    st.markdown("### Match Detail")
    all_fx = _all_fixtures_from_payload(payload)
    opts = fixture_select_options(all_fx)
    if not opts:
        st.info("Keine Spiele geladen — Filter anpassen oder aktualisieren.")
    else:
        pick = st.selectbox("Spiel wählen", ["—"] + list(opts.keys()), key="fb_mc_detail_pick")
        if pick != "—":
            fixture_id = opts[pick]
            cache_key = f"fb_mc_detail_{fixture_id}"
            pick_sig = f"{fixture_id}|{session_plan}"
            if st.session_state.get("fb_mc_detail_sig") != pick_sig:
                st.session_state.fb_mc_detail_sig = pick_sig
                st.session_state.pop(cache_key, None)
            if cache_key not in st.session_state:
                with st.spinner("Match-Daten werden geladen…"):
                    st.session_state[cache_key] = fetch_match_detail(
                        service,
                        fixture_id,
                        username=username,
                        session_plan=session_plan,
                    )

            detail = st.session_state.get(cache_key)
            if detail:
                render_match_detail_panel(
                    detail,
                    elite_ok=elite_ok,
                    pro_ok=pro_ok,
                )

            if rank >= 2:
                st.markdown("#### Elite Live Intelligence")
                if not pro_ok and not elite_ok:
                    render_upgrade_card(
                        "Live Intelligence",
                        "AI Match Preview ab Pro — Vollanalyse ab Elite.",
                        pro_need or "football_pro",
                        button_key="fb_mc_pro_intel",
                        on_upgrade=open_premium,
                    )
                else:
                    load_elite = st.button(
                        "AI Intelligence laden",
                        key="fb_mc_elite_load",
                        width="stretch",
                    )
                    elite_cache = f"fb_mc_elite_{fixture_id}"
                    if load_elite:
                        action = "deep_match_analysis" if elite_ok else "basic_prediction"
                        ok_run, msg = can_run_action(username, action, session_plan)
                        if not ok_run:
                            st.error(msg)
                        else:
                            try:
                                consume_action(username, action, session_plan)
                            except FootballAccessError as exc:
                                st.error(str(exc))
                            else:
                                engine = EliteLiveIntelEngine(service)
                                with st.spinner("Elite Bundle wird aggregiert…"):
                                    try:
                                        bundle = engine.fetch_bundle(
                                            fixture_id, username=username
                                        )
                                        st.session_state[elite_cache] = bundle
                                    except FootballAPIError as exc:
                                        st.error(str(exc))

                    bundle = st.session_state.get(elite_cache)
                    if bundle:
                        if elite_ok:
                            render_elite_live_dashboard(bundle)
                        else:
                            preview = pro_preview_from_bundle(bundle)
                            st.markdown("**Pro Preview**")
                            st.json(preview)
                        st.caption(
                            "Keine Wettempfehlung. Bildungs- & Analysezweck — "
                            "verantwortungsvoll nutzen."
                        )
            elif rank == 1:
                st.caption(
                    "Pro: Predictions, H2H, Lineups, Events · "
                    "Elite: Live Intelligence & Value-Hinweise."
                )

    with st.expander("Favoriten-Ligen verwalten", expanded=False):
        options = _all_league_options()
        labels = [f"{lg['name']} ({lg['country']})" for lg in options]
        label_to_id = {labels[i]: int(options[i]["id"]) for i in range(len(options))}
        current_labels = [
            lbl for lbl, lid in label_to_id.items() if lid in favs
        ]
        picked = st.multiselect(
            "Deine Favoriten",
            labels,
            default=current_labels,
            key="fb_mc_fav_multiselect",
        )
        if st.button("Favoriten speichern", key="fb_mc_save_favs"):
            st.session_state.fb_mc_favorites = [label_to_id[l] for l in picked if l in label_to_id]
            st.session_state.fb_mc_payload = None
            st.success("Favoriten gespeichert.")
            st.rerun()
