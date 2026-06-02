"""Video provider registry — auto wählt günstigste verfügbare KI-API für dich."""
from __future__ import annotations

from config import VIDEO_PROVIDER

from services.video_providers.base import BaseVideoProvider, VideoGenRequest, VideoGenResult

# ---------------------------------------------------------
# Inline providers (single consumer: this registry)
# ---------------------------------------------------------

from pathlib import Path
from typing import Any

import requests

from config import (
    FAL_KEY,
    FAL_VIDEO_ENDPOINT,
    REPLICATE_API_TOKEN,
    REPLICATE_REELS_MODEL,
    REPLICATE_VIDEO_MODEL,
)
from services.mabyte_video_brand import render_mabyte_studio_mp4

try:
    import replicate  # type: ignore
except Exception:
    replicate = None


class FalVideoProvider(BaseVideoProvider):
    name = "fal"

    def available(self) -> bool:
        return bool((FAL_KEY or "").strip() and (FAL_VIDEO_ENDPOINT or "").strip())

    def generate(self, request: VideoGenRequest, *, out_path: str) -> VideoGenResult:
        if not self.available():
            return VideoGenResult(
                ok=False,
                provider=self.name,
                error="FAL_API_KEY oder FAL_VIDEO_ENDPOINT fehlt.",
            )
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            resp = requests.post(
                FAL_VIDEO_ENDPOINT,
                headers={
                    "Authorization": f"Key {FAL_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "prompt": request.prompt[:900],
                    "duration": min(max(int(request.duration_sec), 3), 15),
                    "aspect_ratio": "9:16" if request.aspect == "9:16" else "16:9",
                },
                timeout=300,
            )
            if resp.status_code >= 400:
                return VideoGenResult(
                    ok=False,
                    provider=self.name,
                    error=f"FAL HTTP {resp.status_code}: {resp.text[:300]}",
                )
            data = resp.json()
            video_url = (
                data.get("video", {}).get("url")
                or data.get("output", {}).get("url")
                or data.get("url")
                or ""
            )
            if not video_url:
                return VideoGenResult(ok=False, provider=self.name, error="FAL: keine Video-URL.")
            dl = requests.get(video_url, timeout=180)
            if dl.status_code >= 400:
                return VideoGenResult(ok=False, provider=self.name, error="FAL Download fehlgeschlagen.")
            path.write_bytes(dl.content)
            return VideoGenResult(
                ok=True,
                file_path=str(path),
                file_url=video_url,
                provider=self.name,
                message="MaByte Video — KI-Clip bereit",
            )
        except Exception as exc:
            return VideoGenResult(ok=False, provider=self.name, error=str(exc))


class MockVideoProvider(BaseVideoProvider):
    """Internal id: mock — user-facing: MaByte Studio."""

    name = "mabyte_studio"

    def available(self) -> bool:
        return True

    def generate(self, request: VideoGenRequest, *, out_path: str) -> VideoGenResult:
        path = Path(out_path)
        w = 1080 if request.aspect == "9:16" else 1920
        h = 1920 if request.aspect == "9:16" else 1080

        ok, msg = render_mabyte_studio_mp4(
            path,
            duration_sec=request.duration_sec,
            width=w,
            height=h,
        )
        if ok and path.exists():
            return VideoGenResult(
                ok=True,
                file_path=str(path),
                provider=self.name,
                message=msg,
            )

        return VideoGenResult(
            ok=False,
            provider=self.name,
            error=msg
            or "MaByte Studio Export fehlgeschlagen. Setze REPLICATE_API_TOKEN für KI-Clips.",
        )


def _replicate_normalize_output(output: Any) -> str:
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    if isinstance(output, (list, tuple)) and output:
        return _replicate_normalize_output(output[0])
    url = getattr(output, "url", None)
    if callable(url):
        try:
            return str(url())
        except Exception:
            pass
    return str(output)


class ReplicateVideoProvider(BaseVideoProvider):
    name = "replicate"

    def available(self) -> bool:
        return bool(
            replicate
            and (REPLICATE_API_TOKEN or "").strip()
            and (REPLICATE_REELS_MODEL or REPLICATE_VIDEO_MODEL or "").strip()
        )

    def generate(self, request: VideoGenRequest, *, out_path: str) -> VideoGenResult:
        if not self.available():
            return VideoGenResult(
                ok=False,
                provider=self.name,
                error="REPLICATE_API_TOKEN oder REPLICATE_VIDEO_MODEL fehlt.",
            )
        model = REPLICATE_REELS_MODEL or REPLICATE_VIDEO_MODEL
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            import os

            os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
            payload: dict[str, Any] = {"prompt": request.prompt[:900]}
            if "kling" in str(model).lower():
                payload["duration"] = min(max(int(request.duration_sec), 5), 10)
            output = replicate.run(model, input=payload)  # type: ignore[attr-defined]
            url = _replicate_normalize_output(output)
            if not url:
                return VideoGenResult(ok=False, provider=self.name, error="Kein Video von Replicate.")
            if url.startswith("http"):
                resp = requests.get(url, timeout=180)
                if resp.status_code >= 400:
                    return VideoGenResult(
                        ok=False,
                        provider=self.name,
                        error=f"Download HTTP {resp.status_code}",
                    )
                path.write_bytes(resp.content)
                return VideoGenResult(
                    ok=True,
                    file_path=str(path),
                    file_url=url,
                    provider=self.name,
                    message="MaByte Video — KI-Clip bereit",
                )
            return VideoGenResult(
                ok=True,
                file_path=url,
                provider=self.name,
                message="MaByte Video — KI-Clip bereit",
            )
        except Exception as exc:
            return VideoGenResult(ok=False, provider=self.name, error=str(exc))

_STUDIO = MockVideoProvider()
_PROVIDERS: dict[str, BaseVideoProvider] = {
    "mock": _STUDIO,
    "mabyte_studio": _STUDIO,
    "studio": _STUDIO,
    "replicate": ReplicateVideoProvider(),
    "fal": FalVideoProvider(),
}


def ai_provider_available() -> bool:
    return _PROVIDERS["replicate"].available() or _PROVIDERS["fal"].available()


def get_studio_provider() -> BaseVideoProvider:
    return _STUDIO


def get_ai_provider() -> tuple[BaseVideoProvider | None, str | None]:
    """Beste verfügbare KI-API (Replicate → FAL)."""
    for key in ("replicate", "fal"):
        p = _PROVIDERS[key]
        if p.available():
            return p, None
    return None, (
        "KI-Video ist auf dem Server noch nicht aktiv. "
        "Bitte REPLICATE_API_TOKEN + REPLICATE_VIDEO_MODEL in Railway setzen."
    )


def get_video_provider(preferred: str | None = None) -> BaseVideoProvider:
    key = (preferred or VIDEO_PROVIDER or "auto").strip().lower()
    if key in ("mock", "mabyte_studio", "studio"):
        return _STUDIO
    if key in ("replicate", "fal"):
        p = _PROVIDERS.get(key)
        if p and p.available():
            return p
    if key == "auto" or key == "ai":
        p, _ = get_ai_provider()
        if p:
            return p
        return _STUDIO
    provider = _PROVIDERS.get(key)
    if provider and provider.available():
        return provider
    p, _ = get_ai_provider()
    return p or _STUDIO


def provider_status() -> dict[str, bool]:
    from services.mabyte_video_brand import provider_display_name

    return {
        provider_display_name(name): p.available()
        for name, p in _PROVIDERS.items()
        if name not in ("mabyte_studio", "studio")
    }


__all__ = [
    "VideoGenRequest",
    "VideoGenResult",
    "BaseVideoProvider",
    "get_video_provider",
    "get_studio_provider",
    "get_ai_provider",
    "ai_provider_available",
    "provider_status",
]
