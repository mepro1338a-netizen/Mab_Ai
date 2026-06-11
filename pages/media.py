import uuid
import sqlite3

import streamlit as st
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_IMAGE_MODEL, OPENAI_TEXT_MODEL, DB_PATH
from database import spend_tokens, save_usage, get_user, update_tokens
from ui_core import sync_session_user
def render_image_studio(
    *,
    tokens_available: int,
    on_generate,
) -> None:
    from pricing import get_image_cost
    from ui.styles import inject_css

    DEFAULT_PRESET: dict[str, str] = {
        "id": "auto",
        "size": "1024",
        "aspect": "1:1",
        "format_name": "Auto",
        "tier": "Standard",
        "pixels": "auto",
    }

    IMAGE_STUDIO_CSS = """
.stApp:has(.img-studio) section.main .block-container {
    padding-top: 20px !important;
    padding-bottom: 32px !important;
    max-width: 720px !important;
}
.stApp:has(.img-studio) section.main .block-container > div {
    gap: 0.35rem !important;
}
.img-studio { margin: 0; }
.img-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 10px;
}
.img-head-title {
    color: #fafafa !important;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -.35px;
}
.img-head-meta {
    color: #a1a1aa !important;
    font-size: 12px;
    font-weight: 600;
}
.img-head-meta strong { color: #e4e4e7 !important; }
.img-prompt-label {
    color: #a1a1aa !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
    margin: 0 0 8px 2px;
}
.st-key-image_prompt [data-testid="stTextArea"] > label,
.st-key-image_prompt [data-testid="stTextArea"] > label p {
    display: none !important;
}
.st-key-image_prompt [data-testid="stTextArea"] > div,
.st-key-image_prompt [data-testid="stTextArea"] div[data-baseweb="textarea"],
.st-key-image_prompt [data-testid="stTextArea"] div[data-baseweb="base-input"] {
    background: #27272a !important;
    background-color: #27272a !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 14px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, .04) !important;
    overflow: hidden !important;
}
.st-key-image_prompt [data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within,
.st-key-image_prompt [data-testid="stTextArea"] div[data-baseweb="base-input"]:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, .25) !important;
}
.st-key-image_prompt textarea {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    line-height: 1.5 !important;
    caret-color: #a78bfa !important;
    padding: 16px 18px !important;
    min-height: 92px !important;
}
.st-key-image_prompt textarea::placeholder {
    color: rgba(255,255,255,.48) !important;
    -webkit-text-fill-color: rgba(255,255,255,.48) !important;
    font-weight: 500 !important;
}
.st-key-btn_image .stButton > button {
    min-height: 48px !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    background: #7c3aed !important;
    border: 1px solid #6d28d9 !important;
    color: #ffffff !important;
    box-shadow: none !important;
}
.st-key-btn_image .stButton > button:hover {
    background: #6d28d9 !important;
    border-color: #5b21b6 !important;
}
.img-result {
    margin-top: 14px;
    padding: 12px;
    border-radius: 16px;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(168,85,247,.2);
}
.img-result-title {
    color: #ffffff !important;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 8px;
}
.img-result-prompt {
    color: #94a3b8 !important;
    font-size: 12px;
    margin-bottom: 10px;
    line-height: 1.4;
}
"""
    inject_css(IMAGE_STUDIO_CSS)

    preset = DEFAULT_PRESET
    quality = "hd" if st.session_state.get("image_hd") else "standard"
    cost = get_image_cost(quality=quality, size=preset["size"])
    tokens_fmt = f"{tokens_available:,}".replace(",", ".")

    st.markdown('<div class="img-studio">', unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="img-head">
    <div class="img-head-title">Image Studio</div>
    <div class="img-head-meta"><strong>{tokens_fmt}</strong> Tokens · <strong>{cost}</strong> pro Bild</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="img-prompt-label">Prompt</div>', unsafe_allow_html=True)
    prompt = st.text_area(
        "Prompt",
        placeholder="Beschreibe dein Bild — Stil, Farben, Stimmung…",
        key="image_prompt",
        height=100,
        label_visibility="collapsed",
    )

    hd = st.checkbox("HD (mehr Details)", key="image_hd", value=False)

    gen_clicked = st.button(
        "Bild generieren",
        type="primary",
        key="btn_image",
        width="stretch",
    )
    if gen_clicked:
        if not (prompt or "").strip():
            st.warning("Bitte kurz beschreiben, was du sehen willst.")
        elif tokens_available < cost:
            st.error(f"Nicht genug Tokens ({tokens_available} / {cost}).")
        else:
            on_generate(
                prompt.strip(),
                cost,
                preset=preset,
                quality="hd" if hd else "standard",
                style="",
                use_case="",
            )

    image_bytes = st.session_state.get("image_last_bytes")
    if image_bytes:
        meta = st.session_state.get("image_last_meta") or {}
        user_prompt = html.escape(str(meta.get("prompt", "")))
        st.markdown(
            f"""
<div class="img-result">
    <div class="img-result-title">Dein Bild</div>
    <div class="img-result-prompt">{user_prompt}</div>
</div>
            """,
            unsafe_allow_html=True,
        )
        st.image(image_bytes, width="stretch")
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "PNG herunterladen",
                data=image_bytes,
                file_name=f"mabyte_{uuid.uuid4().hex[:8]}.png",
                mime="image/png",
                width="stretch",
                key="img_dl_png",
            )
        with c2:
            if st.button("Neu", key="img_clear_result", width="stretch"):
                st.session_state.pop("image_last_bytes", None)
                st.session_state.pop("image_last_meta", None)
                st.rerun()
def inject_workspace_css() -> None:
    from ui.styles import inject_css, page_layout_css

    WORKSPACE_CSS = """
.stApp:has(.mb-workspace) section.main .block-container {
    max-width: 920px !important;
    padding-top: 20px !important;
    padding-bottom: 40px !important;
}
.stApp:has(.mb-workspace) section.main div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #18181b !important;
    border: 1px solid #3f3f46 !important;
    border-radius: 16px !important;
    box-shadow: none !important;
    backdrop-filter: blur(10px);
}
.stApp:has(.mb-workspace) .stTextInput input,
.stApp:has(.mb-workspace) .stTextArea textarea,
.stApp:has(.mb-workspace) div[data-baseweb="select"] > div {
    background: #27272a !important;
    color: #fafafa !important;
    border-color: #3f3f46 !important;
    border-radius: 12px !important;
}
.stApp:has(.mb-workspace) label[data-testid="stWidgetLabel"] p,
.stApp:has(.mb-workspace) label p {
    color: rgba(203, 213, 225, .95) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}
.stApp:has(.mb-workspace) .mb-ws-kicker {
    color: #71717a !important;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .16em;
    text-transform: uppercase;
}
.stApp:has(.mb-workspace) .mb-ws-title {
    color: #fafafa !important;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.03em;
    margin: 6px 0 4px 0;
}
.stApp:has(.mb-workspace) .mb-ws-sub {
    color: #a1a1aa !important;
    font-size: 14px;
    line-height: 1.45;
}
.stApp:has(.mb-workspace) .stButton > button[kind="primary"],
.stApp:has(.mb-workspace) button[data-testid="stBaseButton-primary"] {
    background: #7c3aed !important;
    background-color: #7c3aed !important;
    border: 1px solid #6d28d9 !important;
    color: #ffffff !important;
    box-shadow: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
.stApp:has(.mb-workspace) .stButton > button[kind="primary"]:hover,
.stApp:has(.mb-workspace) button[data-testid="stBaseButton-primary"]:hover {
    background: #6d28d9 !important;
    background-color: #6d28d9 !important;
}
.stApp:has(.mb-workspace) .stButton > button[kind="primary"] p,
.stApp:has(.mb-workspace) button[data-testid="stBaseButton-primary"] p {
    color: #ffffff !important;
}
.mb-ws-head {
    margin-bottom: 18px;
}
.mb-ws-kicker {
    color: #71717a !important;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .18em;
    text-transform: uppercase;
}
.mb-ws-title {
    color: #f8fafc !important;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 6px 0 4px 0;
}
.mb-ws-sub {
    color: rgba(148, 163, 184, .95) !important;
    font-size: 14px;
    line-height: 1.45;
}
"""
    inject_css(page_layout_css(920, 20, 40) + WORKSPACE_CSS)


def workspace_marker() -> None:
    st.markdown('<div class="mb-workspace" aria-hidden="true"></div>', unsafe_allow_html=True)


def workspace_header(title: str, subtitle: str = "") -> None:
    sub = f'<p class="mb-ws-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f"""
<div class="mb-ws-head">
  <div class="mb-ws-kicker">Workspace</div>
  <div class="mb-ws-title">{html.escape(title)}</div>
  {sub}
</div>
        """,
        unsafe_allow_html=True,
    )
from ui.styles import inject_css, page_layout_css, gradient_title_css

try:
    from database import unlock_automation, has_automation_access
except Exception:
    unlock_automation = None
    has_automation_access = None

from pricing import (
    get_reel_script_cost,
    get_reel_video_cost,
    get_automation_unlock_cost,
    get_music_cost,
    get_coding_cost,
)


client = OpenAI(api_key=OPENAI_API_KEY)


# =========================================================
# INLINE: services.image_generate (single consumer: pages/media.py)
# =========================================================

def _image_map_preset_to_api_size(preset: dict) -> str:
    if str((preset or {}).get("id") or "") == "auto":
        return "auto"
    aspect = str((preset or {}).get("aspect") or "1:1")
    if aspect == "9:16":
        return "1024x1536"
    if aspect == "16:9":
        return "1536x1024"
    if aspect == "4:5":
        return "1024x1536"
    return "1024x1024"


def _image_map_quality(quality: str) -> str:
    return "high" if quality == "hd" else "medium"


def _image_build_visual_prompt(user_prompt: str, *, style: str = "", use_case: str = "") -> str:
    style_bit = f", {style} style" if style else ""
    case_bit = f", {use_case} composition" if use_case else ""
    return (
        f"{(user_prompt or '').strip()}{style_bit}{case_bit}. "
        "High quality digital artwork, sharp focus, professional lighting. "
        "No watermark, no blurry artifacts."
    )[:3900]


def _image_generate_openai(prompt: str, *, size: str, quality: str) -> tuple[bytes | None, str | None]:
    from config import OPENAI_API_KEY, OPENAI_IMAGE_MODEL

    if not (OPENAI_API_KEY or "").strip():
        return None, "OPENAI_API_KEY fehlt — Bildgenerierung nicht verfuegbar."

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        result = client.images.generate(
            model=OPENAI_IMAGE_MODEL,
            prompt=prompt[:4000],
            size=size,
            quality=quality,
            n=1,
        )
        if not result.data:
            return None, "Keine Bilddaten von OpenAI erhalten."

        item = result.data[0]
        if getattr(item, "b64_json", None):
            import base64

            return base64.b64decode(item.b64_json), None

        url = getattr(item, "url", None)
        if url:
            resp = requests.get(url, timeout=120)
            if resp.status_code >= 400:
                return None, f"Bild-Download fehlgeschlagen (HTTP {resp.status_code})"
            return resp.content, None

        return None, "OpenAI lieferte weder Bild noch URL."
    except Exception as exc:
        return None, str(exc)[:500]


def _image_generate_stability(prompt: str) -> tuple[bytes | None, str | None]:
    from config import STABILITY_API_KEY, STABILITY_IMAGE_MODEL

    if not (STABILITY_API_KEY or "").strip():
        return None, "STABILITY_API_KEY fehlt."

    url = f"https://api.stability.ai/v2beta/stable-image/generate/{STABILITY_IMAGE_MODEL}"
    headers = {
        "authorization": f"Bearer {STABILITY_API_KEY}",
        "accept": "image/*",
    }
    data = {"prompt": prompt[:4000], "output_format": "png"}

    try:
        response = requests.post(
            url,
            headers=headers,
            files={"none": ""},
            data=data,
            timeout=120,
        )
        if response.status_code >= 400:
            return None, (response.text or f"Stability HTTP {response.status_code}")[:500]
        return response.content, None
    except Exception as exc:
        return None, str(exc)[:500]


def _image_generate_bytes(prompt: str, *, size: str, quality: str) -> tuple[bytes | None, str | None]:
    from config import IMAGE_PROVIDER

    provider = (IMAGE_PROVIDER or "openai").strip().lower()
    if provider == "stability":
        return _image_generate_stability(prompt)
    return _image_generate_openai(prompt, size=size, quality=quality)


def _image_generate_from_studio_options(
    user_prompt: str,
    *,
    preset: dict,
    quality: str = "standard",
    style: str = "",
    use_case: str = "",
) -> tuple[bytes | None, str | None, str]:
    visual = _image_build_visual_prompt(user_prompt, style=style, use_case=use_case)
    api_size = _image_map_preset_to_api_size(preset)
    api_quality = _image_map_quality(quality)
    data, err = _image_generate_bytes(visual, size=api_size, quality=api_quality)
    return data, err, visual


# =========================================================
# INLINE: services.video_studio (single consumer: pages/media.py)
# =========================================================

try:
    import replicate as _replicate  # type: ignore
except Exception:
    _replicate = None


def _video_build_en_clip_prompt(user_prompt: str, *, style: str, platform: str) -> str:
    return (
        f"{(user_prompt or '').strip()}. "
        f"Style: {style}. Platform: {platform}. "
        "Cinematic vertical video, smooth motion, professional lighting, no text overlay."
    )[:900]


def _video_generate_production_package(
    user_prompt: str,
    *,
    seconds: int,
    platform: str,
    style: str,
) -> tuple[str | None, str | None]:
    from config import OPENAI_API_KEY, OPENAI_TEXT_MODEL

    if not (OPENAI_API_KEY or "").strip():
        return None, "OPENAI_API_KEY fehlt — bitte in Railway Variables setzen."

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        system = (
            "Du bist MaByte Video Studio. Erstelle professionelle, umsetzbare "
            "Video-Produktionspakete auf Deutsch. Strukturiert, konkret, creator-ready."
        )
        user = f"""
Erstelle ein vollständiges VIDEO-PRODUKTIONSPAKET.

Konzept: {user_prompt}
Ziel-Länge: {seconds} Sekunden
Plattform: {platform}
Stil: {style}

Liefere exakt diese Abschnitte (Markdown):

## Storyboard
(Shot-für-Shot, Zeitcodes)

## Kamera & Bewegung
## Voiceover-Skript
## On-Screen Text / Captions
## Thumbnail-Konzept
## Export & Upload-Checkliste
## KI-Video-Prompt (EN)
(Ein optimierter Prompt für Kling/Runway/Replicate, copy-paste)

## Hashtags & Titelvorschläge
"""
        response = client.chat.completions.create(
            model=OPENAI_TEXT_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.65,
        )
        text = (response.choices[0].message.content or "").strip()
        if not text:
            return None, "Leere Antwort von OpenAI."
        return text, None
    except Exception as exc:
        return None, f"OpenAI Fehler: {exc}"


def _video_normalize_replicate_output(output) -> str:
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    if isinstance(output, (list, tuple)) and output:
        return _video_normalize_replicate_output(output[0])
    url = getattr(output, "url", None)
    if callable(url):
        try:
            return str(url())
        except Exception:
            pass
    return str(output)


def _video_generate_replicate_clip(en_prompt: str, *, seconds: int = 5) -> tuple[str | None, str | None]:
    from config import REPLICATE_API_TOKEN, REPLICATE_VIDEO_MODEL
    import os

    if not _replicate:
        return None, "Replicate-Paket nicht installiert."
    if not (REPLICATE_API_TOKEN or "").strip():
        return None, "REPLICATE_API_TOKEN fehlt in Railway Variables."
    if not (REPLICATE_VIDEO_MODEL or "").strip():
        return None, "REPLICATE_VIDEO_MODEL fehlt in Railway Variables."

    try:
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
        payload = {"prompt": en_prompt[:900]}
        if "kling" in REPLICATE_VIDEO_MODEL.lower():
            payload.setdefault("duration", min(max(seconds, 5), 10))
        output = _replicate.run(REPLICATE_VIDEO_MODEL, input=payload)
        url = _video_normalize_replicate_output(output)
        if not url:
            return None, "Replicate hat kein Video zurückgegeben."
        return url, None
    except Exception as exc:
        return None, f"Replicate Fehler: {exc}"


def _video_download_video_url(url: str) -> tuple[bytes | None, str | None]:
    try:
        resp = requests.get(url, timeout=180)
        if resp.status_code >= 400:
            return None, f"Video-Download fehlgeschlagen (HTTP {resp.status_code})"
        return resp.content, None
    except Exception as exc:
        return None, f"Download Fehler: {exc}"


def ensure_logged_in():
    if not st.session_state.get("logged_in"):
        st.session_state.page = "auth"
        st.rerun()


def username():
    return str(st.session_state.get("user") or "")


def get_tokens():
    return int(st.session_state.get("tokens", 0) or 0)


def sync_user():
    user = get_user(username())
    if user:
        sync_session_user(user)


def fallback_unlock_automation():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    cur = conn.cursor()

    try:
        cur.execute("ALTER TABLE users ADD COLUMN automation_unlocked INTEGER DEFAULT 0")
    except Exception:
        pass

    cur.execute(
        "UPDATE users SET automation_unlocked = 1 WHERE username = ?",
        (username().strip().lower(),),
    )

    conn.commit()
    conn.close()


def fallback_has_automation_access():
    user = get_user(username())
    if not user:
        return False
    return int(user.get("automation_unlocked") or 0) == 1


def automation_unlocked():
    if has_automation_access:
        try:
            return bool(has_automation_access(username()))
        except Exception:
            return fallback_has_automation_access()
    return fallback_has_automation_access()


def unlock_user_automation():
    if unlock_automation:
        try:
            unlock_automation(username())
            return
        except Exception:
            pass
    fallback_unlock_automation()


def charge_tokens(tool, prompt, cost):
    cost = int(cost)

    if get_tokens() < cost:
        st.error(f"Nicht genug Tokens. Benötigt: {cost}, verfügbar: {get_tokens()}")
        st.stop()

    ok, msg = spend_tokens(username(), cost)

    if not ok:
        st.error(msg)
        st.stop()

    save_usage(
        username=username(),
        tool=tool,
        prompt=str(prompt)[:1000],
        tokens_used=cost,
        cost_tokens=cost,
        api_provider="openai",
        status="charged",
    )

    sync_user()


def refund_tokens(cost, tool, prompt):
    user = get_user(username())
    if not user:
        return

    current = int(user.get("tokens") or 0)
    update_tokens(username(), current + int(cost))

    save_usage(
        username=username(),
        tool=tool,
        prompt=str(prompt)[:1000],
        tokens_used=0,
        cost_tokens=-int(cost),
        api_provider="refund",
        status="refunded",
    )

    sync_user()


_TOOL_SYSTEM = {
    "coding": (
        "Du bist MaByte Code Assistant. Antworte ausschließlich zu Programmierung: "
        "Code schreiben, debuggen, refactoren, APIs, Architektur. "
        "Liefere sauberen, produktionsnahen Code mit kurzen Erklärungen."
    ),
    "music": (
        "Du bist MaByte Music Studio. Erstelle Song-Konzepte, Struktur, Lyrics "
        "und Arrangement-Hinweise — kreativ und professionell."
    ),
}


def ai_generate(prompt: str, *, tool: str = "media") -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY fehlt.")

    system = _TOOL_SYSTEM.get(
        tool,
        "Du bist MaByte Creator Studio. Erstelle professionelle, direkt nutzbare Outputs.",
    )

    response = client.chat.completions.create(
        model=OPENAI_TEXT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content


def render_download(result, prefix):
    filename = f"{prefix}_{uuid.uuid4().hex[:6]}.txt"

    st.download_button(
        "Download",
        data=result.encode("utf-8"),
        file_name=filename,
        mime="text/plain",
        width="stretch",
    )


def run_paid_ai(tool, prompt, cost, filename_prefix):
    charge_tokens(tool, prompt, cost)

    try:
        with st.spinner("MaByte generiert..."):
            result = ai_generate(prompt)

        save_usage(
            username=username(),
            tool=tool,
            prompt=str(prompt)[:1000],
            tokens_used=0,
            cost_tokens=0,
            api_provider="openai",
            status="success",
        )

        st.success("Fertig generiert.")

        with st.container(border=True):
            st.markdown(result)

        render_download(result, filename_prefix)

    except Exception as e:
        refund_tokens(cost, tool, prompt)
        st.error(f"Fehler: {e}")


def media_css():
    inject_css(page_layout_css(1180, 20, 100) + gradient_title_css("mb-title") + """
.mb-sub {
    text-align: center;
    color: #cbd5e1 !important;
    margin-top: 10px;
    margin-bottom: 26px;
    font-size: 16px;
    font-weight: 800;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        radial-gradient(circle at top left, rgba(168,85,247,.12), transparent 32%),
        linear-gradient(145deg, rgba(12,13,32,.92), rgba(6,7,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.16) !important;
    border-radius: 24px !important;
    box-shadow: 0 16px 40px rgba(0,0,0,.22) !important;
}

.stTextArea textarea,
.stTextInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(14,10,28,.96) !important;
    border: 1px solid rgba(168,85,247,.26) !important;
    border-radius: 18px !important;
    color: #ffe7a3 !important;
    min-height: 54px !important;
}

.stTextArea textarea {
    padding-top: 14px !important;
}

[data-testid="metric-container"] {
    background:
        linear-gradient(145deg, rgba(18,14,34,.88), rgba(8,7,18,.98)) !important;
    border: 1px solid rgba(168,85,247,.18) !important;
    border-radius: 22px !important;
    padding: 18px !important;
}

[data-testid="metric-container"] label {
    color: #c084fc !important;
    font-size: 11px !important;
    font-weight: 1000 !important;
    text-transform: uppercase !important;
}

[data-testid="metric-container"] div {
    color: #ffe7a3 !important;
    font-weight: 1000 !important;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(168,85,247,.10) !important;
    border-radius: 16px !important;
    color: #ffe7a3 !important;
    font-weight: 900 !important;
    padding: 12px 18px !important;
}

div[data-testid="stAlert"] {
    background: rgba(30,20,70,.72) !important;
    border: 1px solid rgba(168,85,247,.26) !important;
    border-radius: 16px !important;
}
"""
    )


def render_automation():
    unlock_cost = get_automation_unlock_cost()
    unlocked = automation_unlocked()

    if not unlocked:
        st.warning("Automation System ist gesperrt.")

        c1, c2 = st.columns(2)

        with c1:
            st.metric("Einmaliger Unlock", f"{unlock_cost} Tokens")

        with c2:
            st.metric("Tokens", get_tokens())

        with st.container(border=True):
            st.markdown(
                """
### Automation Unlock

Einmalig freischalten. Danach kannst du Reel-Workflows vorbereiten:

- Auto Caption Flow
- Posting Vorbereitung
- Scheduling Struktur
- Creator Pipeline
- Retry Regeln
- Quality Check
"""
            )

        if st.button("Automation für 1000 Tokens freischalten", width="stretch", key="btn_unlock_auto"):
            charge_tokens("automation_unlock", "Automation Unlock", unlock_cost)
            unlock_user_automation()
            sync_user()

            save_usage(
                username=username(),
                tool="automation_unlock",
                prompt="Automation unlocked",
                tokens_used=0,
                cost_tokens=0,
                api_provider="internal",
                status="success",
            )

            st.success("Automation freigeschaltet.")
            st.rerun()

        return

    st.success("Automation System ist aktiv.")

    with st.container(border=True):
        idea = st.text_area(
            "Automation",
            placeholder="Trigger und Ablauf beschreiben…",
            key="auto_idea",
            height=150,
        )

        platform = st.selectbox(
            "Plattform",
            ["TikTok", "Instagram Reels", "YouTube Shorts"],
            key="auto_platform",
        )

        frequency = st.selectbox(
            "Frequenz",
            ["Täglich", "3x pro Woche", "Wöchentlich"],
            key="auto_frequency",
        )

    if st.button("Automation Flow erstellen", width="stretch", key="btn_auto_flow", type="primary"):
        if not idea:
            st.warning("Bitte Idee eingeben.")
            return

        prompt = f"""
Erstelle einen professionellen Reel Automation Workflow.

Idee:
{idea}

Plattform:
{platform}

Frequenz:
{frequency}

Erstelle exakt:

# Automation Name
# Trigger
# Workflow Steps
# Reel Script Step
# Video Step
# Caption Step
# Posting Step
# Quality Check
# Retry Rules
# User Output
"""

        run_paid_ai("automation_flow", prompt, 40, "mabyte_automation")


def run_image_generation(
    user_prompt: str,
    cost: int,
    *,
    preset: dict,
    quality: str,
    style: str,
    use_case: str,
) -> None:
    charge_tokens("image", user_prompt, cost)

    try:
        with st.spinner("MaByte generiert dein Bild…"):
            image_bytes, err, visual_prompt = _image_generate_from_studio_options(
                user_prompt,
                preset=preset,
                quality=quality,
                style=style,
                use_case=use_case,
            )

        if err or not image_bytes:
            refund_tokens(cost, "image", user_prompt)
            st.error(err or "Bild konnte nicht erstellt werden.")
            return

        save_usage(
            username=username(),
            tool="image",
            prompt=str(user_prompt)[:1000],
            tokens_used=0,
            cost_tokens=0,
            api_provider=OPENAI_IMAGE_MODEL if OPENAI_API_KEY else "image",
            status="success",
        )

        st.session_state.image_last_bytes = image_bytes
        st.session_state.image_last_meta = {
            "prompt": user_prompt,
            "visual_prompt": visual_prompt,
            "preset": preset,
            "quality": quality,
        }
        st.success("Bild fertig generiert.")
        st.rerun()

    except Exception as exc:
        refund_tokens(cost, "image", user_prompt)
        st.error(f"Fehler: {exc}")


def render_image_ai():
    from config import OPENAI_API_KEY

    if not OPENAI_API_KEY:
        st.warning(
            "Bildgenerierung: OPENAI_API_KEY fehlt auf dem Server. "
            "Bitte in Railway/.env setzen."
        )

    def _generate(user_prompt: str, cost: int, **opts) -> None:
        run_image_generation(
            user_prompt,
            cost,
            preset=opts.get("preset") or {},
            quality=opts.get("quality") or "standard",
            style=opts.get("style") or "",
            use_case=opts.get("use_case") or "",
        )

    render_image_studio(
        tokens_available=get_tokens(),
        on_generate=_generate,
    )


def render_music_ai():
    workspace_header("Music Studio", "Song-Konzept und Lyrics-Package generieren.")

    with st.container(border=True):
        topic = st.text_input(
            "Thema",
            placeholder="z.B. Melancholisches Piano, 90 BPM, ruhige Atmosphäre",
            key="music_topic",
        )
        genre = st.selectbox("Genre", ["Rap", "Trap", "Pop", "EDM", "Phonk", "Afro", "Rock"], key="music_genre")
        length = st.selectbox("Länge", ["short", "medium", "long"], key="music_length")
        cost = get_music_cost(length=length)
        st.metric("Kosten", f"{cost} Tokens")

    if st.button("Song Package generieren", width="stretch", key="btn_music", type="primary"):
        if not topic:
            st.warning("Bitte Thema eingeben.")
            return
        run_paid_ai("music", topic, cost, "mabyte_music")


def render_coding_ai():
    workspace_header("Code Studio", "Code schreiben, debuggen und erklären lassen.")

    with st.container(border=True):
        task = st.text_area(
            "Aufgabe",
            placeholder="z.B. Python-Funktion für API-Validierung, React-Komponente refactoren, SQL-Query optimieren…",
            key="coding_task",
            height=140,
        )
        complexity = st.selectbox(
            "Komplexität",
            ["normal", "advanced", "fullstack"],
            key="coding_complexity",
            format_func=lambda x: {
                "normal": "Normal — Snippet / Einzelfunktion",
                "advanced": "Advanced — Modul / mehrere Dateien",
                "fullstack": "Fullstack — Architektur & Integration",
            }.get(x, x),
        )
        cost = get_coding_cost(complexity=complexity)
        st.metric("Kosten", f"{cost} Tokens")

    if st.button("Code Assistant starten", width="stretch", key="btn_coding", type="primary"):
        if not task:
            st.warning("Bitte Aufgabe eingeben.")
            return
        run_paid_ai("coding", task, cost, "mabyte_code")


def run_video_generation(
    user_prompt: str,
    cost: int,
    *,
    seconds: int,
    platform: str,
    style: str,
    quality: str,
    generate_clip: bool,
) -> None:
    charge_tokens("video", user_prompt, cost)

    try:
        with st.spinner("MaByte erstellt dein Video-Paket…"):
            package, err = _video_generate_production_package(
                user_prompt,
                seconds=seconds,
                platform=platform,
                style=style,
            )

        if err or not package:
            refund_tokens(cost, "video", user_prompt)
            st.error(err or "Paket konnte nicht erstellt werden.")
            return

        clip_url = ""
        clip_bytes = None
        if generate_clip:
            with st.spinner("Optional: KI-Clip wird generiert (Replicate)…"):
                en = _video_build_en_clip_prompt(user_prompt, style=style, platform=platform)
                clip_url, clip_err = _video_generate_replicate_clip(
                    en, seconds=min(seconds, 10)
                )
                if clip_err:
                    st.warning(f"Clip: {clip_err}")
                elif clip_url and clip_url.startswith("http"):
                    clip_bytes, dl_err = _video_download_video_url(clip_url)
                    if dl_err:
                        st.warning(f"Clip-Download: {dl_err}")

        save_usage(
            username=username(),
            tool="video",
            prompt=str(user_prompt)[:1000],
            tokens_used=0,
            cost_tokens=0,
            api_provider="openai+replicate" if generate_clip else "openai",
            status="success",
        )

        st.session_state.video_last_package = package
        st.session_state.video_last_meta = {
            "prompt": user_prompt,
            "seconds": seconds,
            "platform": platform,
            "style": style,
            "quality": quality,
            "clip_url": clip_url,
        }
        if clip_bytes:
            st.session_state.video_last_clip_bytes = clip_bytes
        else:
            st.session_state.pop("video_last_clip_bytes", None)

        st.success("Video-Paket fertig.")
        st.rerun()

    except Exception as exc:
        refund_tokens(cost, "video", user_prompt)
        st.error(f"Fehler: {exc}")


def render_creator_studio():
    from ui.video_engine_ui import render_video_engine_studio

    fmt = str(st.session_state.get("creator_format") or "Shorts").strip().lower()
    mode = "video" if fmt == "video" else "reel"
    user = get_user(username()) or {}
    render_video_engine_studio(
        mode=mode,
        username=username(),
        tokens=get_tokens(),
        user=user,
    )


def render_media(active_tool="reels"):
    ensure_logged_in()

    if active_tool == "image":
        workspace_marker()
        inject_workspace_css()
        render_image_ai()
    elif active_tool == "music":
        workspace_marker()
        inject_workspace_css()
        render_music_ai()
    elif active_tool == "coding":
        workspace_marker()
        inject_workspace_css()
        render_coding_ai()
    elif active_tool == "video":
        st.session_state.creator_format = "Video"
        render_creator_studio()
    elif active_tool == "creator":
        render_creator_studio()
    else:
        st.session_state.creator_format = "Shorts"
        render_creator_studio()