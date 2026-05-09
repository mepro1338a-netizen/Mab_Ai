import os
import base64
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Any

from openai import OpenAI

try:
    import replicate
except Exception:
    replicate = None


# =========================================================
# OUTPUT STORAGE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "outputs"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# ENV CONFIG
# =========================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")

IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
VIDEO_MODEL = os.getenv("REPLICATE_VIDEO_MODEL", "kwaivgi/kling-v1.6-standard")


# =========================================================
# HELPERS
# =========================================================

def utc_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")


def make_output_path(prefix: str, ext: str) -> Path:
    return OUTPUT_DIR / f"{prefix}_{utc_stamp()}.{ext}"


def safe_prompt(prompt: str) -> str:
    return (prompt or "").strip()


def download_file(url: str, ext: str = "mp4") -> Tuple[bool, str]:
    try:
        response = requests.get(url, timeout=300)
        response.raise_for_status()

        path = make_output_path("video", ext)
        path.write_bytes(response.content)

        return True, str(path)

    except Exception as e:
        return False, f"Download Fehler: {e}"


def normalize_replicate_output(output: Any) -> Optional[str]:
    if output is None:
        return None

    if isinstance(output, str):
        return output

    if isinstance(output, list) and output:
        first = output[0]

        if isinstance(first, str):
            return first

        if isinstance(first, dict):
            return (
                first.get("url")
                or first.get("video")
                or first.get("output")
                or first.get("file")
                or str(first)
            )

    if isinstance(output, dict):
        return (
            output.get("url")
            or output.get("video")
            or output.get("output")
            or output.get("file")
            or str(output)
        )

    return str(output)


# =========================================================
# OPENAI IMAGE GENERATION
# =========================================================

def generate_image(prompt: str, size: str = "1024x1024") -> Tuple[bool, str]:
    """
    Returns:
        (True, file_path) on success
        (False, error_message) on failure
    """

    prompt = safe_prompt(prompt)

    if not prompt:
        return False, "Bitte Prompt eingeben."

    if not OPENAI_API_KEY:
        return False, "OPENAI_API_KEY fehlt in Railway Variables."

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        result = client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt,
            size=size,
            n=1,
        )

        item = result.data[0]

        if getattr(item, "b64_json", None):
            image_bytes = base64.b64decode(item.b64_json)
            path = make_output_path("image", "png")
            path.write_bytes(image_bytes)
            return True, str(path)

        if getattr(item, "url", None):
            response = requests.get(item.url, timeout=180)
            response.raise_for_status()

            path = make_output_path("image", "png")
            path.write_bytes(response.content)
            return True, str(path)

        return False, "OpenAI hat kein Bild zurückgegeben."

    except Exception as e:
        return False, f"Image Fehler: {e}"


# =========================================================
# REPLICATE VIDEO GENERATION
# =========================================================

def generate_video(prompt: str) -> Tuple[bool, str]:
    """
    Returns:
        (True, file_path_or_url) on success
        (False, error_message) on failure
    """

    prompt = safe_prompt(prompt)

    if not prompt:
        return False, "Bitte Prompt eingeben."

    if not REPLICATE_API_TOKEN:
        return False, "REPLICATE_API_TOKEN fehlt in Railway Variables."

    if not VIDEO_MODEL:
        return False, "REPLICATE_VIDEO_MODEL fehlt in Railway Variables."

    if replicate is None:
        return False, "replicate Package ist nicht installiert."

    try:
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

        output = replicate.run(
            VIDEO_MODEL,
            input={
                "prompt": prompt,
            },
        )

        video_url = normalize_replicate_output(output)

        if not video_url:
            return False, "Replicate hat kein Video zurückgegeben."

        if isinstance(video_url, str) and video_url.startswith("http"):
            ok, result = download_file(video_url, "mp4")
            if ok:
                return True, result

            return True, video_url

        return True, str(video_url)

    except Exception as e:
        return False, f"Video Fehler: {e}"


# =========================================================
# ADVANCED IMAGE GENERATION FOR LATER UI
# =========================================================

def generate_image_bytes(prompt: str, size: str = "1024x1024") -> Tuple[Optional[bytes], Optional[str]]:
    ok, result = generate_image(prompt, size)

    if not ok:
        return None, result

    try:
        path = Path(result)
        return path.read_bytes(), None
    except Exception as e:
        return None, f"Bild konnte nicht gelesen werden: {e}"


# =========================================================
# HEALTH CHECK
# =========================================================

def ai_health_check() -> dict:
    return {
        "openai_ready": bool(OPENAI_API_KEY),
        "replicate_ready": bool(REPLICATE_API_TOKEN),
        "image_model": IMAGE_MODEL,
        "video_model": VIDEO_MODEL,
        "output_dir": str(OUTPUT_DIR),
    }


# =========================================================
# TEST MODE
# =========================================================

if __name__ == "__main__":
    print(ai_health_check())
