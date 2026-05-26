"""MaByte Studio render — always available when external APIs are off."""
from __future__ import annotations

from pathlib import Path

from services.mabyte_video_brand import render_mabyte_studio_mp4
from services.video_providers.base import BaseVideoProvider, VideoGenRequest, VideoGenResult


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
            error=msg or "MaByte Studio Export fehlgeschlagen. Setze REPLICATE_API_TOKEN für KI-Clips.",
        )
