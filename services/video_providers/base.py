"""Video provider interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class VideoGenRequest:
    prompt: str
    duration_sec: int
    aspect: str = "9:16"
    platform: str = "tiktok"


@dataclass
class VideoGenResult:
    ok: bool
    file_path: str = ""
    file_url: str = ""
    provider: str = ""
    message: str = ""
    error: str = ""


class BaseVideoProvider(ABC):
    name: str = "base"

    @abstractmethod
    def available(self) -> bool:
        ...

    @abstractmethod
    def generate(self, request: VideoGenRequest, *, out_path: str) -> VideoGenResult:
        ...
