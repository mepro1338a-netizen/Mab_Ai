import os
import base64
import requests
from pathlib import Path
from datetime import datetime

from openai import OpenAI
import replicate

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

IMAGE_MODEL = os.getenv("IMAGE_MODEL", "gpt-image-1")
VIDEO_MODEL = os.getenv("VIDEO_MODEL", "kwaivgi/kling-v1.6-standard")


def make_filename(prefix: str, ext: str) -> Path:
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return OUTPUT_DIR / f"{prefix}_{stamp}.{ext}"


def generate_image(prompt: str, size: str = "1024x1024"):
    if not OPENAI_API_KEY:
        return False, "OPENAI_API_KEY fehlt."

    if not prompt.strip():
        return False, "Bitte Prompt eingeben."

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        result = client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt,
            size=size,
        )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        path = make_filename("image", "png")
        path.write_bytes(image_bytes)

        return True, str(path)

    except Exception as e:
        return False, f"Image Fehler: {e}"


def generate_video(prompt: str):
    if not REPLICATE_API_TOKEN:
        return False, "REPLICATE_API_TOKEN fehlt."

    if not prompt.strip():
        return False, "Bitte Prompt eingeben."

    try:
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

        output = replicate.run(
            VIDEO_MODEL,
            input={"prompt": prompt},
        )

        video_url = output[0] if isinstance(output, list) else output

        response = requests.get(str(video_url), timeout=180)
        response.raise_for_status()

        path = make_filename("video", "mp4")
        path.write_bytes(response.content)

        return True, str(path)

    except Exception as e:
        return False, f"Video Fehler: {e}"