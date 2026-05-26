"""FAL.ai video generation."""
from __future__ import annotations

from pathlib import Path

import requests

from config import FAL_KEY, FAL_VIDEO_ENDPOINT
from services.video_providers.base import BaseVideoProvider, VideoGenRequest, VideoGenResult


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
