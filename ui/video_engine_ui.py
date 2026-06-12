"""
Unified Video / Reels Studio UI — Create, Preview, Queue, Schedule, Accounts, History.
"""
from __future__ import annotations

import html
import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from database import get_user, save_usage, spend_tokens, update_tokens
from db.app import create_reel_job, list_queued_reel_jobs, update_reel_job
from db.video_engine import (
    get_video_job,
    list_scheduled_posts,
    list_video_jobs,
    update_scheduled_post,
)
from pricing import GEN_AI, GEN_AI_HD, GEN_STUDIO, cost_label, get_video_generation_cost
from services.plan_guard import is_free_plan, require_plan_feature, user_has_feature
from services.video_engine import (
    can_access_plan_feature,
    can_use_ai_video,
    can_use_automation,
    create_automation_rule,
    engine_status,
    get_job_bundle,
    max_duration_for_plan,
    plan_rank,
    run_video_job,
)
from services.video_providers import ai_provider_available
from services.social_oauth import SOCIAL_PLATFORMS
from services.social_publish import SocialPublishService
from ui.styles import inject_css

PLATFORM_LABELS = {
    "tiktok": "TikTok",
    "instagram_reels": "Instagram Reels",
    "youtube_shorts": "YouTube Shorts",
}

STUDIO_CSS = """
.stApp:has(.ve-studio) section.main .block-container {
    padding-top: 20px !important;
    max-width: 900px !important;
    padding-bottom: 32px !important;
}
.ve-head {
    display: flex; flex-wrap: wrap; justify-content: space-between;
    align-items: flex-start; gap: 10px; margin-bottom: 12px;
}
.ve-title { color: #fff !important; font-size: 20px; font-weight: 800; }
.ve-sub { color: #94a3b8 !important; font-size: 12px; }
.ve-pill {
    padding: 6px 12px; border-radius: 999px; font-size: 12px; font-weight: 700;
    background: rgba(168,85,247,.12); border: 1px solid rgba(168,85,247,.28);
    color: #e9d5ff !important;
}
.ve-pill strong { color: #fff !important; }
.ve-badge {
    display: inline-block; padding: 4px 10px; border-radius: 999px;
    font-size: 10px; font-weight: 800; text-transform: uppercase;
    letter-spacing: .08em; margin-right: 6px;
}
.ve-badge.ready { background: rgba(34,197,94,.15); color: #86efac !important; }
.ve-badge.rendering { background: rgba(59,130,246,.15); color: #93c5fd !important; }
.ve-badge.failed { background: rgba(239,68,68,.15); color: #fca5a5 !important; }
.ve-badge.draft { background: rgba(148,163,184,.12); color: #cbd5e1 !important; }
.ve-badge.scheduled { background: rgba(168,85,247,.15); color: #e9d5ff !important; }
.ve-badge.queued { background: rgba(251,191,36,.12); color: #fcd34d !important; }
.ve-badge.ready_to_publish { background: rgba(34,211,238,.12); color: #67e8f9 !important; }
.ve-prompt-label {
    color: #c4b5fd !important; font-size: 11px; font-weight: 800;
    letter-spacing: .14em; text-transform: uppercase; margin: 0 0 8px 2px;
}
.st-key-ve_prompt [data-testid="stTextArea"] > label { display: none !important; }
.st-key-ve_prompt [data-testid="stTextArea"] > div,
.st-key-ve_prompt [data-testid="stTextArea"] div[data-baseweb="textarea"] {
    background: linear-gradient(145deg, rgba(88,28,135,.98), rgba(49,16,78,.99)) !important;
    border: 1px solid rgba(192,132,252,.55) !important;
    border-radius: 20px !important;
    box-shadow: 0 0 40px rgba(168,85,247,.25) !important;
}
.st-key-ve_prompt textarea {
    background: transparent !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 16px !important;
    padding: 16px 18px !important;
    border: none !important;
}
.st-key-ve_prompt textarea::placeholder {
    color: rgba(255,255,255,.45) !important;
    -webkit-text-fill-color: rgba(255,255,255,.45) !important;
}
.st-key-ve_generate .stButton > button {
    min-height: 50px !important; border-radius: 16px !important; font-weight: 800 !important;
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,.12) !important;
}
.ve-upgrade {
    padding: 16px; border-radius: 16px; margin: 12px 0;
    background: linear-gradient(135deg, rgba(88,28,135,.25), rgba(30,20,50,.9));
    border: 1px solid rgba(168,85,247,.35);
}
.ve-upgrade-title { color: #fff !important; font-weight: 800; font-size: 15px; }
.ve-upgrade-sub { color: #94a3b8 !important; font-size: 12px; margin-top: 6px; }
"""


def inject_studio_css() -> None:
    inject_css(STUDIO_CSS)


def _status_badge(status: str) -> str:
    s = (status or "draft").lower()
    cls = s if s in (
        "ready", "rendering", "failed", "scheduled", "posted", "queued", "ready_to_publish"
    ) else "draft"
    return f'<span class="ve-badge {cls}">{html.escape(s)}</span>'


# =========================================================
# INLINE: ui.social_connections_ui (single consumer)
# =========================================================


def _soc_badge(status: str) -> str:
    labels = {
        "connected": ("verbunden", "ready"),
        "expired": ("Token abgelaufen", "failed"),
        "disconnected": ("nicht verbunden", "draft"),
        "api_pending": ("API Review", "scheduled"),
        "not_configured": ("Server nicht konfiguriert", "failed"),
    }
    text, cls = labels.get(status, (status, "draft"))
    return f'<span class="ve-badge {cls}">{html.escape(text)}</span>'


def _soc_format_expires(iso: str) -> str:
    if not iso:
        return "—"
    try:
        return iso.replace("T", " ")[:16] + " UTC"
    except Exception:
        return "—"


def _soc_render_oauth_connect(username: str, pid: str, label: str, *, reconnect: bool = False) -> None:
    from services.social_oauth import connect_auth_url, social_oauth_ready

    url = connect_auth_url(username, pid)
    btn_label = "Erneut verbinden" if reconnect else f"{label} verbinden"
    if url:
        st.link_button(
            btn_label,
            url,
            type="primary",
            width="stretch",
            key=f"soc_oauth_{pid}_{'re' if reconnect else 'new'}",
        )
    else:
        st.button(
            btn_label,
            disabled=True,
            width="stretch",
            key=f"soc_oauth_dis_{pid}",
        )
        if not social_oauth_ready():
            st.caption("OAUTH_STATE_SECRET in Railway setzen.")
        else:
            st.caption("API-Keys für diese Plattform in Railway setzen.")


def render_connected_accounts(username: str) -> None:
    from services.social_oauth import platform_configured, social_oauth_ready

    try:
        from db.video_engine import init_video_engine_tables

        init_video_engine_tables()
    except Exception:
        pass

    try:
        svc = SocialPublishService(username)
        states = svc.connection_states()
    except Exception as exc:
        st.error("Verbindungen konnten nicht geladen werden.")
        st.caption("Datenbank-Tabellen werden beim nächsten Seitenaufruf initialisiert.")
        with st.expander("Technische Details"):
            st.code(str(exc)[:400])
        return

    if not social_oauth_ready():
        st.warning(
            "**OAUTH_STATE_SECRET** fehlt in Railway — OAuth-Verbindungen sind deaktiviert. "
            "Setze ein langes zufälliges Secret und starte den Service neu."
        )

    st.caption(
        "YouTube: `YOUTUBE_OAUTH_CLIENT_ID`, `YOUTUBE_OAUTH_CLIENT_SECRET`, `OAUTH_STATE_SECRET` · "
        "Redirect: `/?page=social_oauth`"
    )

    for st_info in states:
        pid = st_info["id"]
        label = st_info["label"]
        status = st_info["status"]
        meta = SOCIAL_PLATFORMS.get(pid) or {}

        st.markdown(
            f'<div style="margin:12px 0 8px 0;">{_soc_badge(status)} '
            f'<strong style="color:#fff;">{html.escape(label)}</strong></div>',
            unsafe_allow_html=True,
        )

        if st_info.get("account_label") and status in ("connected", "expired"):
            st.caption(f"Kanal: **{html.escape(str(st_info['account_label']))}**")
        if st_info.get("channel_id") and pid == "youtube_shorts":
            st.caption(f"Channel-ID: `{html.escape(str(st_info['channel_id']))}`")

        if status == "connected" and pid == "youtube_shorts":
            if st_info.get("has_refresh_token"):
                st.caption(
                    f"Token gültig bis ca. {_soc_format_expires(st_info.get('token_expires_at', ''))} "
                    "(Refresh aktiv)"
                )
            else:
                st.warning("Kein Refresh-Token — bitte erneut verbinden.")

            cache_key = f"yt_ch_{username}"
            if st.button(
                "Kanalstatus aktualisieren",
                key=f"soc_ch_{pid}",
                width="stretch",
            ):
                with st.spinner("Lade Kanal…"):
                    info, err = svc.youtube_channel_status(pid)
                if err:
                    st.error(err)
                elif info:
                    st.session_state[cache_key] = info

            info = st.session_state.get(cache_key)
            if info:
                st.markdown(
                    f"**{html.escape(str(info.get('title', '')))}** · "
                    f"{html.escape(str(info.get('subscriber_count', '—')))} Abonnenten · "
                    f"{html.escape(str(info.get('video_count', '—')))} Videos"
                )
                thumb = info.get("thumbnail")
                if thumb:
                    try:
                        st.image(str(thumb), width=72)
                    except Exception:
                        pass

        if status == "expired":
            st.caption("Bitte erneut verbinden — Access-Token ist abgelaufen.")

        if status == "not_configured":
            st.caption("API-Keys fehlen auf dem Server (Railway Variables).")
        elif not meta.get("api_ready"):
            st.caption(meta.get("review_note", "Publishing API in Vorbereitung."))

        c1, c2 = st.columns(2)
        with c1:
            if status in ("connected", "expired"):
                _soc_render_oauth_connect(username, pid, label, reconnect=True)
            elif status == "disconnected" and platform_configured(pid):
                _soc_render_oauth_connect(username, pid, label)
            elif status == "disconnected":
                st.button(
                    f"{label} verbinden",
                    disabled=True,
                    width="stretch",
                    key=f"soc_dis_{pid}",
                )
            else:
                st.button(
                    "Nicht verfügbar",
                    disabled=True,
                    width="stretch",
                    key=f"soc_na_{pid}",
                )

        with c2:
            if status == "connected":
                if st.button("Trennen", key=f"soc_disc_{pid}", width="stretch"):
                    svc.disconnect(pid)
                    st.session_state.pop(f"yt_ch_{username}", None)
                    st.success("Getrennt.")
                    st.rerun()

        st.divider()


def _sync_user(username: str) -> None:
    from ui_core import sync_session_user

    user = get_user(username)
    if user:
        sync_session_user(user)


def _safe_tab(label: str, fn, *args, **kwargs) -> None:
    """Isolate tab failures so Create/Preview keep working."""
    try:
        fn(*args, **kwargs)
    except Exception as exc:
        st.error(f"{label}: Dieser Bereich konnte nicht geladen werden.")
        st.caption("Bitte Seite neu laden oder Support kontaktieren.")
        with st.expander("Technische Details"):
            st.code(str(exc)[:500])


def _refund(username: str, cost: int, tool: str, prompt: str) -> None:
    user = get_user(username)
    if not user:
        return
    update_tokens(username, int(user.get("tokens") or 0) + int(cost))
    save_usage(
        username=username,
        tool=tool,
        prompt=str(prompt)[:1000],
        tokens_used=0,
        cost_tokens=-int(cost),
        api_provider="refund",
        status="refunded",
    )
    _sync_user(username)


def render_video_engine_studio(
    *,
    mode: str,
    username: str,
    tokens: int,
    user: dict,
) -> None:
    """mode: 'reel' | 'video'"""
    feature = "reels" if mode == "reel" else "video"
    if not require_plan_feature(
        feature,
        user=user,
        button_key=f"ve_studio_gate_{mode}",
    ):
        return

    inject_studio_css()
    plan = str(user.get("plan") or "free")
    studio_type = "reel" if mode == "reel" else "video"
    title = "Creator Studio"
    subtitle = (
        "Shorts · 3–7s für TikTok, Reels & YouTube"
        if mode == "reel"
        else "Video · längere Clips & Shorts"
    )
    max_dur = max_duration_for_plan(plan, studio_type)
    min_dur = 3 if mode == "reel" else 8
    default_dur = 5 if mode == "reel" else 15

    st.markdown('<div class="ve-studio">', unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="ve-head">
    <div>
        <div class="ve-title">{html.escape(title)}</div>
        <div class="ve-sub">{html.escape(subtitle)}</div>
    </div>
    <div class="ve-pill">Guthaben <strong>{tokens:,}</strong> Tokens</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    status = engine_status()
    prov = status.get("providers", {})
    ai_ok = status.get("ai_ready", False)
    st.caption(
        "MaByte Engine · KI-Video "
        + ("bereit ✓" if ai_ok else "— API-Key in Railway setzen")
        + " · "
        + ", ".join(f"{k} {'✓' if v else '○'}" for k, v in prov.items())
    )

    notice = st.session_state.pop("social_oauth_notice", None)
    if notice:
        level, text = notice
        getattr(st, level)(text)

    try:
        from db.video_engine import init_video_engine_tables

        init_video_engine_tables()
    except Exception:
        pass

    if studio_type == "reel":
        try:
            queued_n = len(list_queued_reel_jobs(username, limit=20))
        except Exception:
            queued_n = 0
        if queued_n:
            st.info(
                f"**{queued_n} Reel(s)** in der Queue — Tab „Queue“ → "
                "„Queue jetzt abarbeiten“ (ca. 1–3 Min.)."
            )

    tabs = st.tabs(["Erstellen", "Bibliothek", "Veröffentlichen"])

    with tabs[0]:
        _tab_create(
            mode=mode,
            studio_type=studio_type,
            username=username,
            tokens=tokens,
            user=user,
            plan=plan,
            min_dur=min_dur,
            max_dur=max_dur,
            default_dur=default_dur,
        )
    with tabs[1]:
        _safe_tab("Bibliothek", _tab_library, username, studio_type)
    with tabs[2]:
        _safe_tab("Veröffentlichen", _tab_publish_hub, username, user, plan)

    st.markdown("</div>", unsafe_allow_html=True)


def _tab_create(
    *,
    mode: str,
    studio_type: str,
    username: str,
    tokens: int,
    user: dict,
    plan: str,
    min_dur: int,
    max_dur: int,
    default_dur: int,
) -> None:
    ai_ready = ai_provider_available()
    can_ai = can_use_ai_video(plan)

    if is_free_plan(user) and studio_type == "reel":
        st.markdown(
            """
<div class="ve-upgrade">
    <div class="ve-upgrade-title">Grand erforderlich</div>
    <div class="ve-upgrade-sub">Reels & Shorts Creator ist ab Grand verfügbar.</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Zu Premium", key="ve_up_reels", type="primary"):
            st.session_state.page = "premium"
            st.rerun()
        return

    if studio_type == "video" and not user_has_feature(user, "video"):
        st.markdown(
            """
<div class="ve-upgrade">
    <div class="ve-upgrade-title">Grand erforderlich</div>
    <div class="ve-upgrade-sub">Voller Video Creator ist ab Grand verfügbar.</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Zu Premium", key="ve_up_pro", type="primary"):
            st.session_state.page = "premium"
            st.rerun()
        return

    st.markdown('<div class="ve-prompt-label">Dein Video-Konzept</div>', unsafe_allow_html=True)
    prompt = st.text_area(
        "Prompt",
        placeholder="Beschreibe Szene, Stimmung, Stil…",
        key="ve_prompt",
        height=100,
        label_visibility="collapsed",
    )

    c1, c2 = st.columns(2)
    with c1:
        platform = st.selectbox(
            "Plattform",
            list(PLATFORM_LABELS.keys()),
            format_func=lambda k: PLATFORM_LABELS[k],
            key="ve_platform",
        )
    with c2:
        duration = st.slider(
            "Länge (Sek.)",
            min_dur,
            max_dur,
            default_dur,
            key="ve_duration",
        )

    auto_meta = st.checkbox(
        "Titel, Caption & Hashtags automatisch",
        value=True,
        key="ve_auto_meta",
    )

    mode_options = [GEN_STUDIO, GEN_AI]
    if can_ai and ai_ready:
        mode_options.append(GEN_AI_HD)
    default_mode = GEN_AI if (can_ai and ai_ready) else GEN_STUDIO
    gen_mode = st.radio(
        "Qualität",
        mode_options,
        format_func=cost_label,
        index=mode_options.index(default_mode) if default_mode in mode_options else 0,
        key="ve_gen_mode",
        horizontal=True,
    )
    if gen_mode != GEN_STUDIO and not can_ai:
        st.info("KI-Video ab **Pro**. MaByte Studio ist günstiger und sofort verfügbar.")
    elif gen_mode != GEN_STUDIO and not ai_ready:
        st.warning(
            "KI-Video: Administrator muss `REPLICATE_API_TOKEN` in Railway setzen. "
            "Bis dahin: MaByte Studio wählen."
        )

    max_dur = max_duration_for_plan(plan, studio_type, mode=gen_mode) or max_dur
    cost = get_video_generation_cost(studio_type, duration, mode=gen_mode)

    st.caption(
        f"**{cost} Tokens** (~{cost / 100:.2f} €) · max. {max_dur}s · "
        f"{'echte KI-Szene' if gen_mode != GEN_STUDIO else 'MaByte Studio Export'}"
    )

    if st.button("In Queue stellen", type="primary", key="ve_generate", width="stretch"):
        if not (prompt or "").strip():
            st.warning("Bitte Konzept eingeben.")
            return
        if is_free_plan(user) and studio_type == "reel":
            st.error("Reels Creator ist ab Grand verfügbar.")
            return
        if tokens < cost:
            st.error(f"Nicht genug Tokens ({tokens} / {cost}).")
            return
        if gen_mode != GEN_STUDIO and not can_ai:
            st.error("KI-Video ab Pro-Plan.")
            return
        if gen_mode != GEN_STUDIO and not ai_ready:
            st.error("KI-API nicht konfiguriert (REPLICATE_API_TOKEN).")
            return

        charge_id = f"chg_{uuid.uuid4().hex}"
        if is_free_plan(user) and studio_type == "reel":
            st.error("Reels Creator ist ab Grand verfügbar.")
            return
        ok, msg = spend_tokens(username, cost)
        if not ok:
            st.error(msg)
            return
        save_usage(
            username=username,
            tool="reel_video" if studio_type == "reel" else "video",
            prompt=prompt[:1000],
            tokens_used=cost,
            cost_tokens=cost,
            api_provider="video_engine",
            status="charged",
        )
        _sync_user(username)

        job = enqueue_reel(
            username,
            prompt=prompt.strip(),
            platform=platform,
            duration_sec=int(st.session_state.get("ve_duration", duration)),
            mode=gen_mode,
            cost_tokens=cost,
            charge_id=charge_id,
            auto_metadata=auto_meta,
        ) if studio_type == "reel" else None

        if studio_type == "reel" and job:
            st.session_state.ve_active_job_id = job.get("id")
            st.success(
                "Reel in Queue gespeichert. "
                "Tab „Queue“ → „Queue jetzt abarbeiten“ startet das Rendering."
            )
            st.rerun()
        else:
            from services.video_engine import run_video_job

            bundle, err = run_video_job(
                username,
                studio_type=studio_type,
                prompt=prompt.strip(),
                platform=platform,
                duration_sec=duration,
                plan=plan,
                mode=gen_mode,
                auto_metadata=auto_meta,
            )
            if err:
                _refund(username, cost, studio_type, prompt)
                st.error(err)
            else:
                st.session_state.ve_active_job_id = (bundle or {}).get("id")
                st.success("Video fertig.")
                st.rerun()


def _tab_library(username: str, studio_type: str) -> None:
    """Preview + Verlauf in einem Tab."""
    sub = st.tabs(["Vorschau", "Verlauf"])
    with sub[0]:
        _tab_preview(username)
    with sub[1]:
        _tab_history(username, studio_type)


def _tab_publish_hub(username: str, user: dict, plan: str) -> None:
    """Queue, Planung, verbundene Accounts."""
    if is_free_plan(user):
        st.markdown(
            """
<div class="ve-upgrade">
    <div class="ve-upgrade-title">Veröffentlichen ab Pro</div>
    <div class="ve-upgrade-sub">Queue, Planung und Auto-Post sind ab Pro bzw. Grand verfügbar.</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Zu Premium", key="ve_up_publish", type="primary"):
            st.session_state.page = "premium"
            st.rerun()
        return

    sub = st.tabs(["Queue", "Planen", "Accounts"])
    with sub[0]:
        _tab_queue(username, user)
    with sub[1]:
        _tab_schedule(username, user, plan)
    with sub[2]:
        _tab_accounts(username)


def _tab_preview(username: str) -> None:
    job_id = st.session_state.get("ve_active_job_id")
    if not job_id:
        jobs = list_video_jobs(username, limit=1)
        if jobs:
            job_id = jobs[0]["id"]
    if not job_id:
        st.info("Noch kein Video. Erstelle eines unter Create.")
        return

    bundle = get_job_bundle(job_id)
    if not bundle:
        st.warning("Job nicht gefunden.")
        return

    st.markdown(_status_badge(bundle.get("status", "")), unsafe_allow_html=True)
    if bundle.get("title"):
        st.markdown(f"**{html.escape(bundle['title'])}**")
    if bundle.get("caption"):
        st.caption(bundle["caption"])
    if bundle.get("hashtags"):
        st.caption(bundle["hashtags"])

    out = bundle.get("output") or {}
    path = out.get("file_path") or ""
    if path and Path(path).exists() and path.endswith(".mp4"):
        st.video(path)
        with open(path, "rb") as f:
            st.download_button(
                "MP4 herunterladen",
                data=f.read(),
                file_name=f"mabyte_{job_id[:8]}.mp4",
                mime="video/mp4",
                key="ve_dl_mp4",
                width="stretch",
            )
    else:
        st.warning(
            "Keine abspielbare MP4. Prüfe FFmpeg auf dem Server oder setze "
            "REPLICATE_API_TOKEN für KI-generierte Clips."
        )

    if bundle.get("status") in ("ready", "ready_to_publish") and path:
        st.checkbox(
            "Ich möchte dieses Reel auf der gewählten Plattform veröffentlichen",
            key=f"ve_pub_consent_{job_id}",
        )
        plat = bundle.get("platform") or "youtube_shorts"
        if st.button("Auf Plattform posten", key=f"ve_pub_now_{job_id}", type="primary"):
            if not st.session_state.get(f"ve_pub_consent_{job_id}"):
                st.warning("Bitte Zustimmung bestätigen.")
            else:
                svc = SocialPublishService(username)
                with st.spinner("Wird veröffentlicht…"):
                    ok, msg = svc.publish_job(job_id, user_consent=True)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)


def _tab_queue(username: str, user: dict) -> None:
    if not can_access_plan_feature(user, "pro"):
        st.markdown(
            '<div class="ve-upgrade"><div class="ve-upgrade-title">Pro: Queue</div>'
            '<div class="ve-upgrade-sub">Queue & Download ab Pro.</div></div>',
            unsafe_allow_html=True,
        )
        return
    svc = SocialPublishService(username)
    jobs = svc.list_queue_jobs()
    st.markdown("**Reel Queue**")
    if st.button("Queue jetzt abarbeiten", key="ve_proc_queue"):
        with st.spinner("Rendering läuft — bitte warten (1–3 Min.)…"):
            try:
                results = process_reel_queue(
                    username, plan=str(user.get("plan") or "free"), max_jobs=1
                )
                try:
                    process_due_schedules(username, plan=str(user.get("plan") or "free"), limit=1)
                except Exception:
                    pass
                ok_n = sum(1 for r in results if r.get("ok"))
                fail_n = len(results) - ok_n
                if ok_n:
                    st.success(f"{ok_n} Reel(s) fertig — Preview öffnen.")
                if fail_n:
                    st.warning(f"{fail_n} Job(s) fehlgeschlagen — Details in der Liste.")
            except Exception:
                st.error("Queue-Abarbeitung fehlgeschlagen. Bitte erneut versuchen.")
        st.rerun()
    if not jobs:
        st.caption("Keine Jobs.")
        return
    publishable = [j for j in jobs if j.get("status") in ("ready", "ready_to_publish")]
    if publishable:
        st.caption(f"{len(publishable)} Reel(s) bereit zum Veröffentlichen")

    for job in jobs[:20]:
        jid = job["id"]
        plat = job.get("platform") or ""
        st.markdown(
            f"{_status_badge(job.get('status', ''))} "
            f"**{html.escape(str(plat))}** · "
            f"{html.escape(str(job.get('prompt', ''))[:55])}"
        )
        if job.get("error_message"):
            st.caption(f"⚠ {html.escape(str(job['error_message'])[:200])}")
        if job.get("posted_video_id"):
            vid = job["posted_video_id"]
            st.markdown(
                f"[YouTube Short ansehen](https://www.youtube.com/shorts/{html.escape(vid)})"
            )

        cols = st.columns(2)
        with cols[0]:
            if job.get("status") == "failed" and st.button("Retry", key=f"retry_{jid}"):
                from db.app import update_reel_job

                update_reel_job(jid, status="queued", error_message="")
                st.rerun()
        with cols[1]:
            if job.get("status") in ("ready", "ready_to_publish") and plat == "youtube_shorts":
                consent_key = f"ve_q_consent_{jid}"
                st.checkbox("Zustimmung", key=consent_key)
                if st.button("→ YouTube Shorts", key=f"pub_{jid}"):
                    if not st.session_state.get(consent_key):
                        st.warning("Bitte Zustimmung aktivieren.")
                    else:
                        with st.spinner("Upload zu YouTube…"):
                            ok, msg = svc.publish_job(jid, user_consent=True)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
                        st.rerun()


def _tab_schedule(username: str, user: dict, plan: str) -> None:
    unlocked = int(user.get("automation_unlocked") or 0) == 1
    if not can_use_automation(plan, bool(unlocked)):
        st.markdown(
            '<div class="ve-upgrade"><div class="ve-upgrade-title">Grand + Automation Unlock</div>'
            '<div class="ve-upgrade-sub">Scheduling & Auto-Publishing für Grand/Elite mit Unlock.</div></div>',
            unsafe_allow_html=True,
        )
        return

    platform = st.selectbox(
        "Plattform",
        list(SOCIAL_PLATFORMS.keys()),
        format_func=lambda i: SOCIAL_PLATFORMS[i]["label"],
        key="ve_sched_plat",
    )
    sched_at = st.text_input("Uhrzeit (ISO UTC)", placeholder="2026-05-25T18:00:00+00:00", key="ve_sched_at")
    freq = st.selectbox("Frequenz", ["once", "daily", "weekly"], key="ve_sched_freq")
    template = st.text_area("Prompt-Vorlage", key="ve_sched_tpl", height=80)
    tags = st.text_input("Hashtag-Set", key="ve_sched_tags")
    auto_cap = st.checkbox("Auto Caption", value=True, key="ve_sched_cap")
    auto_post = st.checkbox("Auto Post", value=False, key="ve_sched_post")
    consent = st.checkbox(
        "Ich erlaube Auto-Posts nur mit verbundenem Account",
        value=False,
        key="ve_sched_consent",
    )

    if st.button("Automation speichern", key="ve_sched_save"):
        post, err = create_automation_rule(
            username,
            plan=plan,
            automation_unlocked=bool(unlocked),
            platform=platform,
            scheduled_at=sched_at,
            frequency=freq,
            prompt_template=template,
            hashtag_set=tags,
            auto_caption=auto_cap,
            auto_post=auto_post,
            user_consent=consent,
        )
        if err:
            st.error(err)
        else:
            st.success(f"Geplant: {post.get('id', '')[:8]}")


def _tab_accounts(username: str) -> None:
    st.markdown("**Connected Accounts**")
    st.caption("Auto-Post nur mit OAuth + ausdrücklicher Zustimmung im Schedule-Tab.")
    try:
        render_connected_accounts(username)
    except Exception as exc:
        st.error("Accounts konnten nicht geladen werden.")
        with st.expander("Technische Details"):
            st.code(str(exc)[:500])


def _tab_history(username: str, studio_type: str) -> None:
    jobs = list_video_jobs(username, studio_type=studio_type, limit=20)
    if not jobs:
        st.caption("Noch keine Jobs.")
        return
    for job in jobs:
        cols = st.columns([3, 1, 1])
        with cols[0]:
            st.markdown(
                f"{_status_badge(job.get('status', ''))} "
                f"{html.escape((job.get('prompt') or '')[:60])}"
            )
        with cols[1]:
            st.caption(f"{job.get('duration_sec')}s")
        with cols[2]:
            if st.button("Öffnen", key=f"ve_open_{job['id']}"):
                st.session_state.ve_active_job_id = job["id"]
                st.rerun()


# ---------------------------------------------------------------------------
# Inline: services.reel_queue (single consumer)
# ---------------------------------------------------------------------------


def _reel_refund_tokens(username: str, cost: int, prompt: str) -> None:
    if cost <= 0:
        return
    user = get_user(username)
    if not user:
        return
    update_tokens(username, int(user.get("tokens") or 0) + int(cost))
    save_usage(
        username=username,
        tool="reel_video",
        prompt=str(prompt)[:1000],
        tokens_used=0,
        cost_tokens=-int(cost),
        api_provider="refund",
        status="refunded",
    )


def enqueue_reel(
    username: str,
    *,
    prompt: str,
    platform: str,
    duration_sec: int,
    mode: str,
    cost_tokens: int,
    charge_id: str,
    auto_metadata: bool = True,
) -> dict:
    return create_reel_job(
        username,
        prompt=prompt,
        platform=platform,
        duration_sec=duration_sec,
        cost_tokens=cost_tokens,
        charge_id=charge_id,
        generation_mode=mode,
        auto_metadata=auto_metadata,
    )


def process_reel_queue(
    username: str,
    *,
    plan: str,
    max_jobs: int = 1,
) -> list[dict]:
    processed: list[dict] = []
    queued = list_queued_reel_jobs(username, limit=max_jobs)
    for row in queued:
        job_id = row["id"]
        job = get_video_job(job_id)
        if not job or job.get("status") != "queued":
            continue
        mode = job.get("generation_mode") or GEN_AI
        try:
            bundle, err = run_video_job(
                username,
                studio_type="reel",
                prompt=job.get("prompt") or "",
                platform=job.get("platform") or "tiktok",
                duration_sec=int(job.get("duration_sec") or 5),
                plan=plan,
                mode=mode,
                quality="standard",
                auto_metadata=bool(job.get("auto_metadata")),
                existing_job_id=job_id,
            )
        except Exception as exc:
            err = "Rendering fehlgeschlagen. Bitte erneut versuchen."
            bundle = None
            update_reel_job(
                job_id,
                status="failed",
                error_message=str(exc)[:400],
            )
            processed.append({"id": job_id, "ok": False, "error": err})
            continue
        if err:
            retries = int(job.get("retry_count") or 0) + 1
            max_r = int(job.get("max_retries") or 2)
            if retries < max_r:
                update_reel_job(job_id, status="queued", retry_count=retries, error_message=err)
            else:
                update_reel_job(job_id, status="failed", retry_count=retries, error_message=err)
                _reel_refund_tokens(
                    username,
                    int(job.get("cost_tokens") or 0),
                    job.get("prompt") or "",
                )
            processed.append({"id": job_id, "ok": False, "error": err})
        else:
            update_reel_job(job_id, status="ready_to_publish")
            processed.append({"id": job_id, "ok": True, "bundle": bundle})
    return processed


def _parse_schedule_iso(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def process_due_schedules(username: str, *, plan: str, limit: int = 3) -> list[str]:
    logs: list[str] = []
    now = datetime.now(timezone.utc)
    svc = SocialPublishService(username)

    for post in list_scheduled_posts(username):
        if post.get("status") not in ("planned", "scheduled", "queued"):
            continue
        due = _parse_schedule_iso(str(post.get("scheduled_at") or ""))
        if due and due > now:
            continue

        post_id = post["id"]
        update_scheduled_post(post_id, status="creating")

        prompt = post.get("prompt_template") or "MaByte Reel"
        platform = post.get("platform") or "tiktok"
        job_id = post.get("job_id") or ""

        if not job_id:
            job = enqueue_reel(
                username,
                prompt=prompt,
                platform=platform,
                duration_sec=5,
                mode=GEN_AI,
                cost_tokens=0,
                charge_id=f"sched_{post_id}",
            )
            job_id = job["id"]
            update_scheduled_post(post_id, job_id=job_id, status="queued")

        auto_post = int(post.get("auto_post") or 0) == 1
        consent = int(post.get("user_consent") or 0) == 1

        if auto_post and consent and svc.is_connected(platform):
            try:
                ok, msg = svc.publish_job(job_id, dry_run=False, user_consent=True)
            except Exception:
                ok, msg = False, "Auto-Post fehlgeschlagen."
            update_scheduled_post(
                post_id,
                status="posted" if ok else "failed",
                error_message="" if ok else msg,
            )
            logs.append(f"{post_id}: {msg}")
        else:
            update_scheduled_post(post_id, status="scheduled")
            logs.append(f"{post_id}: wartet auf Rendering/Post")

    return logs
