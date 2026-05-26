"""Replicate video generation."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests

from config import REPLICATE_API_TOKEN, REPLICATE_REELS_MODEL, REPLICATE_VIDEO_MODEL
from services.video_providers.base import BaseVideoProvider, VideoGenRequest, VideoGenResult

try:
    import replicate
except Exception:
    replicate = None


def _normalize_output(output: Any) -> str:
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    if isinstance(output, (list, tuple)) and output:
        return _normalize_output(output[0])
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
            os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
            payload: dict[str, Any] = {"prompt": request.prompt[:900]}
            if "kling" in model.lower():
                payload["duration"] = min(max(int(request.duration_sec), 5), 10)
            output = replicate.run(model, input=payload)
            url = _normalize_output(output)
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
