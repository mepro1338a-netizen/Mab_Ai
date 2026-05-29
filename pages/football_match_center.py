"""Live Match Center — simple premium-first hub."""

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

from services.football_leagues import VIEW_LABELS, league_ids_for_view

from services.football_match_center import fetch_live_center_payload, fetch_match_detail

from services.football_service import FootballAPIError, get_football_service

from ui.football_components import inject_football_components_css, render_elite_live_dashboard

from ui.football_match_center import (

    fixture_select_options,

    inject_match_center_css,

    render_match_detail_panel,

    render_match_grid,

    render_mc_header,

    render_premium_live_empty,

)

from ui.premium_foundation import render_upgrade_card



_FB_MC_DATA_VERSION = 3

_VIEWS = ("top", "live", "heute", "deutschland", "europa")





def _init_session() -> None:

    defaults = {

        "fb_mc_view": "top",

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

        st.session_state.fb_mc_view = "top"





def _filter_sig(view: str, show_all: bool) -> str:

    return f"{view}|all={int(show_all)}|v={_FB_MC_DATA_VERSION}"





def _fixtures_for_view(payload: dict, view: str) -> list:

    sections = payload.get("sections") or {}

    if view == "live":

        return list(sections.get("live_now") or [])

    if view == "heute":

        out = []

        out.extend(sections.get("live_now") or [])

        out.extend(sections.get("later_today") or [])

        out.extend(sections.get("finished_today") or [])

        return out

    if view == "morgen":

        return list(sections.get("tomorrow") or [])

    out = []

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

            "Live-Spiele und Match-Analyse ab Football Starter.",

            "football_starter",

            button_key="fb_mc_starter_up",

            on_upgrade=open_premium,

        )

        return



    service = get_football_service()

    if not service.is_configured():

        st.markdown(

            '<div class="fb-empty">FOOTBALL_API_KEY fehlt — API wird angebunden.</div>',

            unsafe_allow_html=True,

        )

        return



    elite_ok, _, _ = can_access_feature(username, "ai_elite_live_intelligence", session_plan)

    pro_ok, _, pro_need = can_access_feature(username, "ai_live_match_intelligence", session_plan)



    view = st.session_state.fb_mc_view

    if view not in _VIEWS:

        view = "top"

        st.session_state.fb_mc_view = view



    view_labels = [VIEW_LABELS[v] for v in _VIEWS]
    try:
        view_idx = _VIEWS.index(view)
    except ValueError:
        view_idx = 0
    picked_label = st.radio(
        "Ansicht",
        view_labels,
        index=view_idx,
        horizontal=True,
        key="fb_mc_view_radio",
        label_visibility="collapsed",
    )
    new_view = _VIEWS[view_labels.index(picked_label)]
    if new_view != st.session_state.fb_mc_view:
        st.session_state.fb_mc_view = new_view
        st.session_state.fb_mc_payload = None
    view = st.session_state.fb_mc_view



    show_all = bool(st.session_state.fb_mc_show_all_live)

    league_ids = league_ids_for_view("alle" if show_all else view)



    sig = _filter_sig(view, show_all)

    if sig != st.session_state.fb_mc_filter_sig:

        st.session_state.fb_mc_filter_sig = sig

        st.session_state.fb_mc_payload = None



    col_btn, col_info = st.columns([2, 1])

    with col_btn:

        if st.button("Aktualisieren", type="primary", key="fb_mc_refresh", width="stretch"):

            st.session_state.fb_mc_payload = None

    with col_info:

        st.caption(f"Datum · {payload_today if (payload_today := '') else '…'}")



    if st.session_state.fb_mc_payload is None:

        with st.spinner("Lade Top-Ligen…"):

            try:

                st.session_state.fb_mc_payload = fetch_live_center_payload(

                    service,

                    username=username,

                    league_filter=league_ids,

                    show_all_live=show_all,

                    view="alle" if show_all else view,

                )

            except FootballAPIError as exc:

                st.error(str(exc))

                return



    payload = st.session_state.fb_mc_payload or {}

    today_local = payload.get("today_local") or ""

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



    hint = {

        "top": "Bundesliga, UEFA & Topligen — heute & live",

        "live": "Nur laufende Spiele in Top-Ligen",

        "heute": "Alle Spiele von heute (DE/UEFA/Top)",

        "deutschland": "1.–3. Liga & DFB-Pokal",

        "europa": "Champions League, Premier League, La Liga & Co.",

    }.get(view, "")

    st.caption(f"{hint} · Kalender: {today_local}")



    if payload.get("show_all_live_prompt"):

        render_premium_live_empty(raw_live_count=int(payload.get("raw_live_count") or 0))

        if st.button("Weltweit live anzeigen", key="fb_mc_all_live", width="stretch"):

            st.session_state.fb_mc_show_all_live = True

            st.session_state.fb_mc_payload = None

            st.rerun()



    fixtures = _fixtures_for_view(payload, view)

    selected = st.session_state.get("fb_mc_selected_fixture")

    try:

        selected = int(selected) if selected else None

    except (TypeError, ValueError):

        selected = None



    if not fixtures:

        st.markdown(

            '<div class="fb-empty">Keine Spiele in dieser Ansicht. '

            "Probiere <strong>Heute</strong> oder <strong>Deutschland</strong>, "

            "oder warte auf den nächsten Spieltag.</div>",

            unsafe_allow_html=True,

        )

        if st.button("Alle Ligen weltweit", key="fb_mc_fallback_alle"):

            st.session_state.fb_mc_show_all_live = True

            st.session_state.fb_mc_payload = None

            st.rerun()

    else:

        render_match_grid(

            fixtures,

            key_prefix=f"mc_{view}",

            selected_fixture=selected,

        )



    st.divider()

    st.markdown("#### Spielanalyse")

    opts = fixture_select_options(fixtures)

    fixture_id = selected if selected in opts.values() else None



    if not opts:

        st.caption("Klicke bei einem Spiel auf **Analyse**.")

    else:

        labels_list = list(opts.keys())

        id_to_label = {v: k for k, v in opts.items()}

        idx = 0

        if fixture_id and fixture_id in id_to_label:

            try:

                idx = labels_list.index(id_to_label[fixture_id])

            except ValueError:

                idx = 0

        pick = st.selectbox("Spiel", labels_list, index=idx, key="fb_mc_pick")

        if pick:

            fixture_id = opts[pick]

            st.session_state.fb_mc_selected_fixture = fixture_id



        if fixture_id:

            cache_key = f"fb_mc_detail_{fixture_id}"

            sig_d = f"{fixture_id}|{session_plan}"

            if st.session_state.get("fb_mc_detail_sig") != sig_d:

                st.session_state.fb_mc_detail_sig = sig_d

                st.session_state.pop(cache_key, None)

            if cache_key not in st.session_state:

                with st.spinner("Lade Analyse…"):

                    st.session_state[cache_key] = fetch_match_detail(

                        service,

                        fixture_id,

                        username=username,

                        session_plan=session_plan,

                    )

            detail = st.session_state.get(cache_key)

            if detail:

                render_match_detail_panel(detail, elite_ok=elite_ok, pro_ok=pro_ok)



            if rank >= 2 and (pro_ok or elite_ok):

                if st.button("AI Intelligence", key="fb_mc_ai", width="stretch"):

                    action = "deep_match_analysis" if elite_ok else "basic_prediction"

                    ok_run, msg = can_run_action(username, action, session_plan)

                    if not ok_run:

                        st.error(msg)

                    else:

                        try:

                            consume_action(username, action, session_plan)

                            bundle = EliteLiveIntelEngine(service).fetch_bundle(

                                fixture_id, username=username

                            )

                            st.session_state[f"fb_mc_elite_{fixture_id}"] = bundle

                        except (FootballAccessError, FootballAPIError) as exc:

                            st.error(str(exc))

                bundle = st.session_state.get(f"fb_mc_elite_{fixture_id}")

                if bundle:

                    if elite_ok:

                        render_elite_live_dashboard(bundle)

                    else:

                        st.json(pro_preview_from_bundle(bundle))



    with st.expander("Mehr Optionen"):

        if st.button("Weltweit · alle Live-Spiele", key="fb_mc_exp_all"):

            st.session_state.fb_mc_show_all_live = True

            st.session_state.fb_mc_payload = None

            st.rerun()

        st.caption("Nur für internationale Kleinligen — nicht empfohlen für Top-Analyse.")


