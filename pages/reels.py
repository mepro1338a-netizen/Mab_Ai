"""
MaByte Reel Studio — viral football shorts: script, voice, render, publish.
"""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Callable

import streamlit as st

from config import normalize_app_base_url
from database import get_user, save_usage, spend_tokens, update_tokens
from pricing import get_reel_script_cost, get_reel_video_cost
from services.reel_engine import REEL_MODES, REEL_PLATFORMS, ReelEngine, ReelScriptRequest
from services.social_publish import PLATFORMS, SocialPublishService
from services.video_render import (
    RenderScene,
    build_render_spec,
    ensure_reel_dirs,
    render_vertical_reel,
)
from ui.prompt_ui import inject_ma_prompt_css, prompt_text_area
from ui.reel_components import (
    inject_reel_studio_css,
    reel_feature_allowed,
    render_ai_result,
    render_encoder_status,
    render_export_progress,
    render_football_templates,
    render_locked_feature,
    render_plan_badge,
    render_topbar,
    render_workspace_header,
    user_plan_key,
)


def _username() -> str:
    return str(st.session_state.get("user") or "")


def _tokens() -> int:
    return int(st.session_state.get("tokens", 0) or 0)


def _sync_user() -> None:
    from ui_core import sync_session_user

    user = get_user(_username())
    if user:
        sync_session_user(user)


def _charge(tool: str, prompt: str, cost: int) -> bool:
    if _tokens() < cost:
        st.error(f"Nicht genug Tokens ({_tokens()} / {cost}).")
        return False
    ok, msg = spend_tokens(_username(), cost)
    if not ok:
        st.error(msg)
        return False
    save_usage(
        username=_username(),
        tool=tool,
        prompt=str(prompt)[:1000],
        tokens_used=cost,
        cost_tokens=cost,
        api_provider="openai",
        status="charged",
    )
    _sync_user()
    return True


def _refund(cost: int, tool: str, prompt: str) -> None:
    user = get_user(_username())
    if not user:
        return
    update_tokens(_username(), int(user.get("tokens") or 0) + cost)
    save_usage(
        username=_username(),
        tool=tool,
        prompt=str(prompt)[:1000],
        tokens_used=0,
        cost_tokens=-cost,
        api_provider="refund",
        status="refunded",
    )
    _sync_user()


def _run_ai_tab(
    *,
    tool: str,
    cost: int,
    prompt_key: str,
    spinner: str,
    generator,
) -> None:
    if not _charge(tool, prompt_key, cost):
        return
    try:
        with st.spinner(spinner):
            result = generator()
        save_usage(
            username=_username(),
            tool=tool,
            prompt=prompt_key[:200],
            tokens_used=0,
            cost_tokens=0,
            api_provider="openai",
            status="success",
        )
        if result.content:
            st.session_state.reel_last_script = result.content
            if "# Viral Hook" in result.content or "Hook" in result.content:
                for line in result.content.splitlines():
                    if line.strip() and not line.startswith("#"):
                        st.session_state.reel_preview_hook = line.strip()[:60]
                        break
        render_ai_result(result.content, source=result.source, error=result.error)
        st.download_button(
            "Download",
            data=result.content.encode("utf-8"),
            file_name=f"mabyte_reel_{uuid.uuid4().hex[:6]}.md",
            mime="text/markdown",
            key=f"dl_{tool}",
        )
    except Exception as exc:
        _refund(cost, tool, prompt_key)
        st.error(f"Generierung fehlgeschlagen: {exc}")


def _common_inputs() -> ReelScriptRequest:
    topic = st.session_state.get("reel_topic", "") or ""
    return ReelScriptRequest(
        topic=topic,
        platform=st.session_state.get("reel_platform", REEL_PLATFORMS[0]),
        match_context=st.session_state.get("reel_match", ""),
        mode=st.session_state.get("reel_mode", "hype"),
        duration_sec=int(st.session_state.get("reel_duration", 30)),
        cta=st.session_state.get("reel_cta", "Folge für mehr Fußball-Content"),
    )


def _tab_script_ai(engine: ReelEngine, user: dict) -> None:
    st.markdown("**Script AI** — virale Skripte, CTA, Hashtags, Thumbnail-Text")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.selectbox("Plattform", REEL_PLATFORMS, key="reel_platform")
    with c2:
        st.selectbox("Modus", REEL_MODES, format_func=lambda x: x.title(), key="reel_mode")
    with c3:
        st.slider("Länge (s)", 15, 60, 30, key="reel_duration")

    topic = prompt_text_area(
        placeholder="z.B. Bayern vs Dortmund — warum dieses Derby viral geht…",
        key="reel_topic",
        height=100,
    )
    st.text_input("Match Story (optional)", key="reel_match")
    st.text_input("CTA", key="reel_cta")

    cost = get_reel_script_cost()
    st.caption(f"Kosten: {cost} Tokens")

    if st.button("Virales Reel-Skript generieren", type="primary", key="btn_reel_script_ai"):
        if not (topic or "").strip():
            st.warning("Bitte Thema eingeben.")
            return
        req = _common_inputs()
        st.session_state.reel_preview_platform = req.platform

        def gen():
            return engine.generate_script(req)

        _run_ai_tab(
            tool="reel_script",
            cost=cost,
            prompt_key=topic,
            spinner="Script AI schreibt…",
            generator=gen,
        )


def _tab_hooks(engine: ReelEngine, user: dict) -> None:
    if not reel_feature_allowed("hooks", user):
        render_locked_feature("hooks")
        return
    st.markdown("**Hook Generator** — 5+ virale Einstiege")
    if st.button("Hooks generieren", type="primary", key="btn_reel_hooks"):
        req = _common_inputs()
        if not req.topic.strip():
            st.warning("Bitte zuerst Thema unter Script AI eintragen.")
            return
        cost = max(40, get_reel_script_cost() // 2)

        def gen():
            return engine.generate_hooks(req)

        _run_ai_tab(tool="reel_hooks", cost=cost, prompt_key=req.topic, spinner="Hooks…", generator=gen)


def _tab_voiceover(engine: ReelEngine, user: dict) -> None:
    if not reel_feature_allowed("voiceover", user):
        render_locked_feature("voiceover")
        return
    from services.reel_engine import voice_catalog

    st.markdown("**Voice AI** — ElevenLabs & OpenAI TTS (Vorbereitung)")
    voices = voice_catalog()
    st.selectbox(
        "Stimme",
        [v["id"] for v in voices],
        format_func=lambda i: next(v["label"] for v in voices if v["id"] == i),
        key="reel_voice_id",
    )
    st.caption("TTS-API wird nach Key-Freigabe aktiviert — jetzt: Voiceover-Skript.")

    if st.button("Voiceover-Paket erstellen", type="primary", key="btn_reel_voice"):
        req = _common_inputs()
        script = st.session_state.get("reel_last_script", req.topic)
        cost = max(35, get_reel_script_cost() // 2)

        def gen():
            return engine.generate_voiceover_pack(req, script)

        _run_ai_tab(tool="reel_voice", cost=cost, prompt_key=script[:200], spinner="Voice…", generator=gen)


def _tab_clip_builder(user: dict) -> None:
    if not reel_feature_allowed("clip_builder", user):
        render_locked_feature("clip_builder")
        return

    st.markdown("**Clip Builder** — 9:16 Export, Untertitel, Zoom, Branding")
    render_encoder_status()

    wm = st.text_input("Wasserzeichen", value="MaByte", key="reel_watermark")
    brand = st.color_picker("Brand-Farbe", "#a855f7", key="reel_brand_color")
    music = st.text_input("Musik-Track (Pfad/URL später)", key="reel_music")

    uploaded = st.file_uploader(
        "Clips hochladen",
        type=["mp4", "mov", "webm", "png", "jpg"],
        accept_multiple_files=True,
        key="reel_uploads",
    )
    if uploaded:
        _, clips_dir = ensure_reel_dirs(_username())
        for f in uploaded:
            dest = clips_dir / f.name
            dest.write_bytes(f.getvalue())
        st.success(f"{len(uploaded)} Datei(en) in Clip Library.")

    if st.button("9:16 Reel rendern", type="primary", key="btn_reel_render"):
        script = st.session_state.get("reel_last_script", "MaByte Reel")
        spec = build_render_spec(title="Fußball Reel", script=script)
        spec.watermark = wm
        spec.brand_color = brand
        spec.music_track = music

        prog = st.empty()

        def on_progress(p: float, msg: str) -> None:
            prog.progress(p, text=msg)

        cost = get_reel_video_cost(7)
        if not _charge("reel_render", "render", cost):
            return

        try:
            with st.spinner("Rendering…"):
                result = render_vertical_reel(spec, username=_username(), progress=on_progress)
            if result.ok and result.output_path and Path(result.output_path).exists():
                st.video(result.output_path)
                st.success(result.message)
            elif result.spec_json_path:
                st.info(result.message)
                st.caption(f"Spec: {result.spec_json_path}")
            else:
                st.warning(result.message)
        except Exception as exc:
            _refund(cost, "reel_render", "render")
            st.error(str(exc))


def _tab_captions(engine: ReelEngine, user: dict) -> None:
    if not reel_feature_allowed("captions", user):
        render_locked_feature("captions")
        return
    st.markdown("**Auto Captions** — SRT + Burn-in Style")
    if st.button("Captions generieren", type="primary", key="btn_reel_captions"):
        script = st.session_state.get("reel_last_script", "")
        if not script.strip():
            st.warning("Zuerst ein Skript unter Script AI erzeugen.")
            return
        platform = st.session_state.get("reel_platform", REEL_PLATFORMS[0])
        cost = 30

        def gen():
            return engine.generate_captions(script, platform)

        _run_ai_tab(tool="reel_captions", cost=cost, prompt_key=script[:200], spinner="Captions…", generator=gen)


def _tab_publish(user: dict) -> None:
    if not reel_feature_allowed("publish", user):
        render_locked_feature("publish")
        return

    svc = SocialPublishService(_username(), normalize_app_base_url())
    st.markdown("**Publish Center** — OAuth, Queue, Drafts, Schedule")

    cols = st.columns(len(PLATFORMS))
    for col, plat in zip(cols, svc.list_platforms()):
        with col:
            status = "✓ Key" if plat["connected"] else "○ Demo"
            st.markdown(f"**{plat['label']}** · {status}")
            if st.button(f"Connect {plat['id']}", key=f"oauth_{plat['id']}", width="stretch"):
                st.info(f"OAuth-URL (Vorbereitung): {plat['connect_url']}")

    st.divider()
    title = st.text_input("Titel", key="pub_title")
    caption = st.text_area("Caption", key="pub_caption", height=80)
    hashtags = st.text_input("Hashtags", key="pub_tags")
    platform = st.selectbox("Ziel", [p["id"] for p in PLATFORMS], format_func=lambda i: next(p["label"] for p in PLATFORMS if p["id"] == i))
    scheduled = st.text_input("Schedule (ISO, optional)", placeholder="2026-05-25T18:00:00Z")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Als Draft speichern", key="pub_draft"):
            svc.add_draft(platform=platform, title=title, caption=caption, hashtags=hashtags, scheduled_at=scheduled)
            st.success("Draft gespeichert.")
    with c2:
        if st.button("In Queue", key="pub_queue"):
            d = svc.add_draft(platform=platform, title=title, caption=caption, hashtags=hashtags)
            ok, msg = svc.queue_for_posting(d.id)
            st.success(msg) if ok else st.warning(msg)

    if reel_feature_allowed("auto_posting", user):
        st.markdown("**Elite:** Auto-Posting & Multi-Platform")
        if st.button("Simuliert posten (Dry-Run)", key="pub_sim"):
            drafts = svc.list_drafts(status="queued") or svc.list_drafts()
            if not drafts:
                st.warning("Keine Drafts in Queue.")
            else:
                ok, msg = svc.simulate_post(drafts[0]["id"])
                st.success(msg) if ok else st.error(msg)
    else:
        st.caption("Auto-Posting ab Elite-Plan.")

    st.subheader("Queue & Drafts")
    for item in svc.list_drafts()[:8]:
        st.markdown(
            f"- **{item.get('platform')}** · {item.get('status')} · "
            f"{item.get('title', '')[:40]} · {item.get('created_at', '')[:16]}"
        )


def _tab_assets() -> None:
    st.markdown("**Content Assets** — Uploads, Templates, Thumbnails")
    st.file_uploader("Brand Assets", type=["png", "svg", "jpg"], key="reel_brand_upload")
    st.markdown("**Football Templates**")
    render_football_templates()
    st.markdown("**Thumbnail Presets**")
    thumbs = ["DERBY", "GOAL", "LINEUP", "HOT TAKE", "TRANSFER"]
    tc = st.columns(len(thumbs))
    for col, t in zip(tc, thumbs):
        with col:
            if st.button(t, key=f"thumb_{t}", width="stretch"):
                st.session_state.reel_preview_hook = t


def render_reels_studio_page() -> None:
    """Entry from pages/media.py when active_tool=reels."""
    inject_reel_studio_css()
    inject_ma_prompt_css()

    user = get_user(_username()) or {}
    engine = ReelEngine()

    st.markdown('<div class="reel-studio">', unsafe_allow_html=True)

    col_t, col_p = st.columns([4, 1])
    with col_t:
        render_topbar(tokens=_tokens(), cost_hint=f"Script ab {get_reel_script_cost()} Tokens")
    with col_p:
        render_plan_badge()

    render_workspace_header()

    tab_script, tab_hook, tab_voice, tab_clip, tab_cap, tab_pub = st.tabs(
        [
            "Script AI",
            "Hook Generator",
            "Voiceover",
            "Clip Builder",
            "Auto Captions",
            "Publish Center",
        ]
    )

    with tab_script:
        _tab_script_ai(engine, user)

    with tab_hook:
        _tab_hooks(engine, user)

    with tab_voice:
        _tab_voiceover(engine, user)

    with tab_clip:
        _tab_clip_builder(user)
        with st.expander("Content Assets"):
            _tab_assets()

    with tab_cap:
        _tab_captions(engine, user)

    with tab_pub:
        _tab_publish(user)

    st.markdown("</div>", unsafe_allow_html=True)
