"""
Vertical reel rendering — FFmpeg / MoviePy when available, spec-only fallback otherwise.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from config import DATA_DIR


REELS_EXPORT_DIR = DATA_DIR / "reels" / "exports"
REELS_CLIPS_DIR = DATA_DIR / "reels" / "clips"


@dataclass
class RenderScene:
    label: str
    duration_sec: float = 2.5
    text_overlay: str = ""
    zoom: float = 1.08
    transition: str = "cut"  # cut | fade | zoom


@dataclass
class RenderSpec:
    title: str
    aspect: str = "9:16"
    width: int = 1080
    height: int = 1920
    fps: int = 30
    scenes: list[RenderScene] = field(default_factory=list)
    captions_srt: str = ""
    watermark: str = "MaByte"
    brand_color: str = "#a855f7"
    music_track: str = ""
    voiceover_path: str = ""


@dataclass
class RenderResult:
    ok: bool
    output_path: str = ""
    message: str = ""
    spec_json_path: str = ""
    used_ffmpeg: bool = False
    used_moviepy: bool = False


ProgressCallback = Callable[[float, str], None]


def ensure_reel_dirs(username: str) -> tuple[Path, Path]:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in (username or "anon"))
    export = REELS_EXPORT_DIR / safe
    clips = REELS_CLIPS_DIR / safe
    export.mkdir(parents=True, exist_ok=True)
    clips.mkdir(parents=True, exist_ok=True)
    return export, clips


def ffmpeg_available() -> bool:
    return bool(shutil.which("ffmpeg"))


def moviepy_available() -> bool:
    try:
        import moviepy  # noqa: F401

        return True
    except Exception:
        return False


def build_render_spec(
    *,
    title: str,
    script: str,
    captions: str = "",
    scenes: list[RenderScene] | None = None,
) -> RenderSpec:
    if not scenes:
        scenes = [
            RenderScene("Hook", 2.0, zoom=1.12),
            RenderScene("Story", 4.0, transition="fade"),
            RenderScene("Stat", 3.0, zoom=1.05),
            RenderScene("CTA", 2.5, transition="zoom"),
        ]
    return RenderSpec(
        title=title or "MaByte Reel",
        scenes=scenes,
        captions_srt=captions,
    )


def _write_spec_bundle(spec: RenderSpec, out_dir: Path) -> str:
    job_id = uuid.uuid4().hex[:10]
    spec_path = out_dir / f"render_spec_{job_id}.json"
    payload = {
        "title": spec.title,
        "aspect": spec.aspect,
        "width": spec.width,
        "height": spec.height,
        "fps": spec.fps,
        "watermark": spec.watermark,
        "brand_color": spec.brand_color,
        "music_track": spec.music_track,
        "voiceover_path": spec.voiceover_path,
        "captions_srt": spec.captions_srt,
        "scenes": [
            {
                "label": s.label,
                "duration_sec": s.duration_sec,
                "text_overlay": s.text_overlay,
                "zoom": s.zoom,
                "transition": s.transition,
            }
            for s in spec.scenes
        ],
    }
    spec_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(spec_path)


def _try_ffmpeg_slideshow(spec: RenderSpec, out_path: Path, progress: ProgressCallback | None) -> RenderResult:
    if not ffmpeg_available():
        return RenderResult(ok=False, message="FFmpeg nicht installiert")

    if progress:
        progress(0.1, "FFmpeg wird vorbereitet…")

    duration = max(3.0, sum(s.duration_sec for s in spec.scenes))
    from services.mabyte_video_brand import render_mabyte_studio_mp4

    ok, msg = render_mabyte_studio_mp4(
        out_path,
        duration_sec=duration,
        width=spec.width,
        height=spec.height,
    )
    if ok:
        if progress:
            progress(1.0, "MaByte Export fertig")
        return RenderResult(ok=True, output_path=str(out_path), message=msg, used_ffmpeg=True)

    # Fallback: einfaches Branding
    wm = (spec.watermark or "MaByte").replace("'", "\\'")
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=0x581c87:s={spec.width}x{spec.height}:d={duration}",
        "-vf",
        f"drawtext=text='{wm}':fontsize=52:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(out_path),
    ]
    try:
        if progress:
            progress(0.4, "Rendering 9:16…")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if proc.returncode != 0:
            return RenderResult(ok=False, message=proc.stderr[:500] or "FFmpeg Fehler")
        if progress:
            progress(1.0, "Export fertig")
        return RenderResult(ok=True, output_path=str(out_path), message="OK", used_ffmpeg=True)
    except subprocess.TimeoutExpired:
        return RenderResult(ok=False, message="FFmpeg Timeout")
    except Exception as exc:
        return RenderResult(ok=False, message=str(exc))


def _try_moviepy_placeholder(spec: RenderSpec, out_path: Path) -> RenderResult:
    if not moviepy_available():
        return RenderResult(ok=False, message="MoviePy nicht installiert")
    try:
        from moviepy.editor import ColorClip, CompositeVideoClip, TextClip

        duration = max(3.0, sum(s.duration_sec for s in spec.scenes))
        bg = ColorClip(size=(spec.width, spec.height), color=(26, 26, 46), duration=duration)
        try:
            txt = TextClip(
                spec.watermark,
                fontsize=48,
                color="white",
                size=(spec.width - 80, None),
            ).set_duration(duration).set_position(("center", "bottom"))
            final = CompositeVideoClip([bg, txt])
        except Exception:
            final = bg
        final.write_videofile(str(out_path), fps=spec.fps, logger=None)
        final.close()
        return RenderResult(ok=True, output_path=str(out_path), message="OK", used_moviepy=True)
    except Exception as exc:
        return RenderResult(ok=False, message=str(exc))


def render_vertical_reel(
    spec: RenderSpec,
    *,
    username: str = "",
    progress: ProgressCallback | None = None,
) -> RenderResult:
    """
    Renders 9:16 MP4 when FFmpeg/MoviePy exist; always writes render spec JSON.
    """
    export_dir, _ = ensure_reel_dirs(username)
    job_id = uuid.uuid4().hex[:8]
    out_mp4 = export_dir / f"reel_{job_id}.mp4"

    if progress:
        progress(0.05, "Render-Spezifikation…")

    spec_json = _write_spec_bundle(spec, export_dir)

    if progress:
        progress(0.15, "Prüfe FFmpeg / MoviePy…")

    if ffmpeg_available():
        res = _try_ffmpeg_slideshow(spec, out_mp4, progress)
        if res.ok:
            res.spec_json_path = spec_json
            return res

    if moviepy_available():
        if progress:
            progress(0.35, "MoviePy Render…")
        res = _try_moviepy_placeholder(spec, out_mp4)
        if res.ok:
            res.spec_json_path = spec_json
            return res

    if progress:
        progress(1.0, "Spec gespeichert (kein Video-Encoder)")

    return RenderResult(
        ok=True,
        output_path="",
        message=(
            "Render-Spezifikation gespeichert. FFmpeg oder MoviePy auf dem Server installieren "
            "für echten MP4-Export."
        ),
        spec_json_path=spec_json,
    )


def render_status_label() -> dict[str, str]:
    return {
        "ffmpeg": "verfügbar" if ffmpeg_available() else "nicht installiert",
        "moviepy": "verfügbar" if moviepy_available() else "nicht installiert",
    }
