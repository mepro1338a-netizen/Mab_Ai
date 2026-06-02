"""
MaByte-branded video render — Studio-Look (kein generischer Agent-/Mock-Trailer).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

def ffmpeg_available() -> bool:
    import shutil

    return bool(shutil.which("ffmpeg"))

BRAND_NAME = "MaByte"
TAGLINE = "One system. Infinite intelligence."
STUDIO_LABEL = "MaByte Studio"


def _esc(text: str) -> str:
    return (text or "").replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def render_mabyte_studio_mp4(
    out_path: str | Path,
    *,
    duration_sec: float = 5.0,
    width: int = 1080,
    height: int = 1920,
) -> tuple[bool, str]:
    """
    Vertical MaByte-branded MP4 (purple gradient, logo text).
    Returns (ok, message).
    """
    if not ffmpeg_available():
        return False, "FFmpeg nicht auf dem Server — bitte Replicate/FAL Keys setzen."

    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    duration = max(3.0, min(float(duration_sec), 120.0))

    brand = _esc(BRAND_NAME)
    tag = _esc(TAGLINE)

    # Lila MaByte-Gradient + weiße Typo (kein generischer Farbbalken-Trailer)
    vf = (
        f"drawtext=text='{brand}':fontsize=76:fontcolor=white:"
        f"borderw=2:bordercolor=0x581c87:x=(w-text_w)/2:y=(h-text_h)/2-48,"
        f"drawtext=text='{tag}':fontsize=26:fontcolor=0xe9d5ff:"
        f"x=(w-text_w)/2:y=(h-text_h)/2+42"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=0x581c87:s={width}x{height}:d={duration}",
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(path),
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "FFmpeg Fehler")[:400]
            return False, err
        if not path.exists() or path.stat().st_size < 500:
            return False, "MaByte Export konnte nicht geschrieben werden."
        return True, f"{STUDIO_LABEL} — Video exportiert."
    except subprocess.TimeoutExpired:
        return False, "Rendering Timeout — bitte kürzere Länge wählen."
    except Exception as exc:
        return False, str(exc)


def provider_display_name(provider_key: str) -> str:
    names = {
        "mock": STUDIO_LABEL,
        "mabyte": STUDIO_LABEL,
        "replicate": "MaByte × Replicate",
        "fal": "MaByte × FAL",
    }
    return names.get((provider_key or "").lower(), STUDIO_LABEL)
