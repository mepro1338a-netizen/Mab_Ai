"""Video provider registry — auto wählt günstigste verfügbare KI-API für dich."""
from __future__ import annotations

from config import VIDEO_PROVIDER

from services.video_providers.base import BaseVideoProvider, VideoGenRequest, VideoGenResult
from services.video_providers.fal_provider import FalVideoProvider
from services.video_providers.mock_provider import MockVideoProvider
from services.video_providers.replicate_provider import ReplicateVideoProvider

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
    "get_video_provider",
    "get_studio_provider",
    "get_ai_provider",
    "ai_provider_available",
    "provider_status",
]
