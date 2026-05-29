"""Live Match Center tab — premium-first fixtures hub."""
from __future__ import annotations

import streamlit as st

from config import FOOTBALL_LEAGUE_GROUPS, football_plan_rank
from services.football_access import (
    FootballAccessError,
    can_access_feature,
    can_run_action,
    consume_action,
)
from services.football_elite_live import EliteLiveIntelEngine, pro_preview_from_bundle
from services.football_leagues import CATEGORY_LABELS, league_ids_for_category
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
    render_premium_live_empty,
)
from ui.premium_foundation import render_upgrade_card

_FB_MC_DATA_VERSION = 2

_FILTER_KEYS = (
    "premium",
    "live",
    "heute",
    "morgen",
    "deutschland",
    "uefa",
    "europa_top",
    "favoriten",
    "alle",
)


def _all_league_options() -> list[dict]:
    seen: set[int] = set()
    out: list[dict] = []
    for lgs in FOOTBALL_LEAGUE_GROUPS.values():
        for lg in lgs:
            lid = int(lg["id"])
            if lid in seen:
                continue
            seen.add(lid)
            out.append(lg)
    return sorted(out, key=lambda x: str(x.get("name") or ""))


def _init_session() -> None:
    defaults = {
        "fb_mc_category": "premium",
        "fb_mc_favorites": [],
        "fb_mc_payload": None,
        "fb_mc_filter_sig": "",
        "fb_mc_show_all_live": False,
        "fb_mc_selected_fixture": None,
        "fb_mc_data_version": _FB_MC_DATA_VERSION,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    if st.session_state.get("fb_mc_data_version") != _FB_MC_DATA_VERSION:
        st.session_state.fb_mc_data_version = _FB_MC_DATA_VERSION
        st.session_state.fb_mc_payload = None


def _scope_for_category(category: str) -> str:
    if category == "live":
        return "live"
    if category == "heute":
        return "heute"
    if category == "morgen":
        return "morgen"
    return "all"


def _filter_signature(
    category: str,
    league_filter: set[int] | None,
    country: str,
    show_all_live: bool,
) -> str:
    ids = sorted(league_filter or [])
    return (
        f"{category}|{','.join(map(str, ids))}|{country.strip().lower()}|"
        f"all_live={int(show_all_live)}|v={_FB_MC_DATA_VERSION}"
    )


def _all_fixtures_from_payload(payload: dict) -> list:
    sections = payload.get("sections") or {}
    out: list = []
    for key in ("live_now", "later_today", "finished_today", "tomorrow"):
        out.extend(sections.get(key) or [])
    return out


def _resolve_fixture_id() -> int | None:
    selected = st.session_state.get("fb_mc_selected_fixture")
    if selected:
        try:
            return int(selected)
        except (TypeError, ValueError):
            pass
    pick_idx = st.session_state.get("fb_mc_detail_pick_idx")
    if pick_idx:
        try:
            return int(pick_idx)
        except (TypeError, ValueError):
            pass
    return None


def _render_empty_hint(payload: dict, category: str) -> None:
    total = int(payload.get("total_fixtures") or 0)
    if total > 0:
        return
    raw = int(payload.get("raw_merged_count") or 0)
    live_raw = int(payload.get("raw_live_count") or 0)
    today_local = payload.get("today_local") or "—"
    st.markdown(
        f'<div class="fb-empty">'
        f"Keine Spiele in dieser Ansicht (Datum lokal: <strong>{today_local}</strong>). "
        f"API-Rohdaten: {raw} Spiele, {live_raw} live weltweit."
        f"</div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Alle Ligen anzeigen", key="fb_mc_empty_alle", width="stretch"):
            st.session_state.fb_mc_category = "alle"
            st.session_state.fb_mc_show_all_live = True
            st.session_state.fb_mc_payload = None
            st.rerun()
    with c2:
        if st.button("Erneut laden", key="fb_mc_empty_reload", width="stretch"):
            st.session_state.fb_mc_payload = None
            st.rerun()


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

    cats = list(_FILTER_KEYS)
    cat_labels = [CATEGORY_LABELS[c] for c in cats]
    try:
        cat_idx = cats.index(st.session_state.fb_mc_category)
    except ValueError:
        cat_idx = 0
    picked_cat = st.radio(
        "Filter",
        cat_labels,
        index=cat_idx,
        horizontal=True,
        key="fb_mc_cat_radio",
        label_visibility="collapsed",
    )
    category = cats[cat_labels.index(picked_cat)]
    if category != st.session_state.fb_mc_category:
        st.session_state.fb_mc_category = category
        st.session_state.fb_mc_show_all_live = False
        st.session_state.fb_mc_payload = None
    else:
        st.session_state.fb_mc_category = category

    render_category_chips(CATEGORY_LABELS, category)

    favs: list[int] = list(st.session_state.fb_mc_favorites or [])
    show_all_live = bool(st.session_state.fb_mc_show_all_live)
    premium_only = category in ("premium", "live", "heute", "morgen") and not show_all_live
    if category == "alle":
        premium_only = False

    if category == "favoriten" and not favs:
        st.info("Noch keine Favoriten — unten im Expander Ligen auswählen und speichern.")

    league_filter = league_ids_for_category(category, favorites=favs)
    if category == "favoriten" and league_filter is not None and not league_filter:
        league_filter = set()

    country_filter = st.text_input(
        "Team / Land suchen (optional)",
        value="",
        key="fb_mc_country_filter",
        placeholder="z. B. Bayern, Germany, Real Madrid…",
    )

    sig = _filter_signature(category, league_filter, country_filter, show_all_live)
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

    scope = _scope_for_category(category)

    if refresh or st.session_state.fb_mc_payload is None:
        if category == "favoriten" and league_filter is not None and not league_filter:
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
                "premium_live_count": 0,
                "raw_live_count": 0,
                "raw_merged_count": 0,
                "show_all_live_prompt": False,
                "today_local": "",
            }
        else:
            with st.spinner("Spiele werden geladen…"):
                try:
                    st.session_state.fb_mc_payload = fetch_live_center_payload(
                        service,
                        username=username,
                        league_filter=league_filter,
                        country_filter=country_filter,
                        premium_only=premium_only,
                        show_all_live=show_all_live,
                        scope=scope,
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

    selected_fixture = _resolve_fixture_id()
    show_prompt = bool(payload.get("show_all_live_prompt"))

    if show_prompt:
        render_premium_live_empty(raw_live_count=int(payload.get("raw_live_count") or 0))
        if st.button(
            "Alle Live-Spiele anzeigen",
            key="fb_mc_show_all_live_btn",
            type="primary",
            width="stretch",
        ):
            st.session_state.fb_mc_show_all_live = True
            st.session_state.fb_mc_payload = None
            st.rerun()
    elif category == "premium" and not show_all_live:
        st.caption("Premium-Ansicht: Top-Ligen · sortiert nach Relevanz")

    _render_empty_hint(payload, category)

    show_sections = {
        "live_now": category in (
            "premium", "live", "heute", "deutschland", "uefa",
            "europa_top", "favoriten", "alle",
        ),
        "later_today": category in (
            "premium", "heute", "deutschland", "uefa", "europa_top", "favoriten", "alle",
        ),
        "finished_today": category in (
            "premium", "heute", "deutschland", "uefa", "europa_top", "favoriten", "alle",
        ),
        "tomorrow": category in ("premium", "morgen", "alle"),
    }

    if show_sections["live_now"]:
        render_match_section(
            "Heute live · Jetzt",
            sections.get("live_now") or [],
            empty="Keine Live-Spiele in den gewählten Top-Ligen.",
            key_prefix="live",
            elite_ok=elite_ok,
            selected_fixture=selected_fixture,
        )

    if show_sections["later_today"]:
        render_match_section(
            "Später heute",
            sections.get("later_today") or [],
            empty="Keine weiteren Top-Spiele heute.",
            key_prefix="later",
            elite_ok=elite_ok,
            selected_fixture=selected_fixture,
        )

    if show_sections["finished_today"]:
        render_match_section(
            "Beendet heute",
            sections.get("finished_today") or [],
            empty="Noch keine Ergebnisse in der Auswahl.",
            key_prefix="done",
            elite_ok=elite_ok,
            selected_fixture=selected_fixture,
        )

    if show_sections["tomorrow"]:
        render_match_section(
            "Morgen",
            sections.get("tomorrow") or [],
            empty="Keine Top-Spiele morgen in der Auswahl.",
            key_prefix="tom",
            elite_ok=elite_ok,
            selected_fixture=selected_fixture,
        )

    st.divider()
    st.markdown("### Match Detail")
    all_fx = _all_fixtures_from_payload(payload)
    opts = fixture_select_options(all_fx)
    fixture_id = selected_fixture
    if fixture_id and fixture_id not in opts.values():
        fixture_id = None

    if not opts and not fixture_id:
        st.info("Keine Spiele geladen — Filter „Alle Ligen“ testen oder aktualisieren.")
    else:
        labels = list(opts.keys())
        id_to_label = {v: k for k, v in opts.items()}
        default_idx = 0
        if fixture_id and fixture_id in id_to_label:
            try:
                default_idx = labels.index(id_to_label[fixture_id])
            except ValueError:
                default_idx = 0
        pick = (
            st.selectbox(
                "Spiel wählen",
                labels,
                index=default_idx if labels else 0,
                key="fb_mc_detail_pick",
            )
            if labels
            else None
        )

        if pick:
            fixture_id = opts[pick]
            st.session_state.fb_mc_selected_fixture = fixture_id

        if fixture_id:
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

            load_elite_auto = st.session_state.pop("fb_mc_load_elite", None)
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
                    load_elite = load_elite_auto == fixture_id or st.button(
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
        fav_labels = [f"{lg['name']} ({lg['country']})" for lg in options]
        label_to_id = {fav_labels[i]: int(options[i]["id"]) for i in range(len(options))}
        current_labels = [lbl for lbl, lid in label_to_id.items() if lid in favs]
        picked = st.multiselect(
            "Deine Favoriten",
            fav_labels,
            default=current_labels,
            key="fb_mc_fav_multiselect",
        )
        if st.button("Favoriten speichern", key="fb_mc_save_favs"):
            st.session_state.fb_mc_favorites = [
                label_to_id[l] for l in picked if l in label_to_id
            ]
            st.session_state.fb_mc_payload = None
            st.success("Favoriten gespeichert.")
            st.rerun()
