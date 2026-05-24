import base64
import time
import requests
from typing import Any

from openai import OpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_IMAGE_MODEL,
    IMAGE_PROVIDER,
    STABILITY_API_KEY,
    STABILITY_IMAGE_MODEL,
    VIDEO_PROVIDER,
    MUSIC_PROVIDER,
    REPLICATE_API_TOKEN,
    REPLICATE_VIDEO_MODEL,
    REPLICATE_MUSIC_MODEL,
    FAL_KEY,
    FAL_VIDEO_ENDPOINT,
    FAL_MUSIC_ENDPOINT,
    SUNO_API_URL,
    SUNO_API_KEY,
)


def openai_client():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing in .env")
    return OpenAI(api_key=OPENAI_API_KEY)


def generate_openai_image(prompt: str):
    client = openai_client()
    result = client.images.generate(
        model=OPENAI_IMAGE_MODEL,
        prompt=prompt,
        size="1024x1024",
        quality="low",
        n=1,
    )
    img = result.data[0]
    if getattr(img, "b64_json", None):
        return base64.b64decode(img.b64_json), None
    if getattr(img, "url", None):
        return img.url, None
    return None, "OpenAI image returned no data."


def generate_stability_image(prompt: str):
    if not STABILITY_API_KEY:
        return None, "STABILITY_API_KEY missing in .env"

    url = f"https://api.stability.ai/v2beta/stable-image/generate/{STABILITY_IMAGE_MODEL}"
    headers = {
        "authorization": f"Bearer {STABILITY_API_KEY}",
        "accept": "image/*",
    }
    files = {"none": ""}
    data = {
        "prompt": prompt,
        "output_format": "png",
    }

    response = requests.post(url, headers=headers, files=files, data=data, timeout=120)
    if response.status_code >= 400:
        return None, response.text

    return response.content, None


def generate_image_provider(prompt: str):
    if IMAGE_PROVIDER == "stability":
        return generate_stability_image(prompt)
    return generate_openai_image(prompt)


def replicate_create_prediction(model: str, input_payload: dict[str, Any]):
    if not REPLICATE_API_TOKEN:
        return None, "REPLICATE_API_TOKEN missing in .env"
    if not model:
        return None, "Replicate model missing in .env"

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "version": model if ":" in model else None,
        "input": input_payload,
    }

    # If user gave owner/name instead of version hash, use models endpoint.
    if ":" not in model and "/" in model:
        owner, name = model.split("/", 1)
        url = f"https://api.replicate.com/v1/models/{owner}/{name}/predictions"
        payload = {"input": input_payload}
    else:
        url = "https://api.replicate.com/v1/predictions"

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    if response.status_code >= 400:
        return None, response.text

    pred = response.json()
    get_url = pred.get("urls", {}).get("get")
    if not get_url:
        return pred, None

    for _ in range(90):
        time.sleep(2)
        r = requests.get(get_url, headers=headers, timeout=60)
        if r.status_code >= 400:
            return None, r.text
        data = r.json()
        status = data.get("status")
        if status == "succeeded":
            return data.get("output"), None
        if status in ("failed", "canceled"):
            return None, str(data)

    return None, "Replicate timeout."


def fal_run(endpoint: str, input_payload: dict[str, Any]):
    if not FAL_KEY:
        return None, "FAL_KEY missing in .env"
    if not endpoint:
        return None, "FAL endpoint missing in .env"

    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(endpoint, headers=headers, json=input_payload, timeout=180)
    if response.status_code >= 400:
        return None, response.text

    data = response.json()
    return data.get("video", data.get("audio", data.get("url", data.get("output", data)))), None


def normalize_media_output(output):
    if isinstance(output, list) and output:
        first = output[0]
        if isinstance(first, dict):
            return first.get("url") or first.get("audio") or first.get("video") or str(first)
        return first
    if isinstance(output, dict):
        return output.get("url") or output.get("audio") or output.get("video") or output.get("output") or str(output)
    return output


def generate_video_provider(prompt: str, mode: str = "Fast"):
    payload = {
        "prompt": prompt,
        "duration": "5" if mode == "Fast" else "8",
        "aspect_ratio": "9:16",
    }

    if VIDEO_PROVIDER == "fal":
        output, error = fal_run(FAL_VIDEO_ENDPOINT, payload)
    else:
        output, error = replicate_create_prediction(REPLICATE_VIDEO_MODEL, payload)

    if error:
        return None, error
    return normalize_media_output(output), None


def generate_music_provider(prompt: str):
    payload = {
        "prompt": prompt,
        "duration": 30,
        "model_version": "large",
        "output_format": "mp3",
    }

    if MUSIC_PROVIDER == "fal":
        output, error = fal_run(FAL_MUSIC_ENDPOINT, payload)
    elif MUSIC_PROVIDER == "replicate":
        output, error = replicate_create_prediction(REPLICATE_MUSIC_MODEL, payload)
    elif MUSIC_PROVIDER == "suno":
        if not SUNO_API_URL or not SUNO_API_KEY:
            return None, "SUNO_API_URL or SUNO_API_KEY missing in .env"
        try:
            response = requests.post(
                SUNO_API_URL,
                headers={"Authorization": f"Bearer {SUNO_API_KEY}", "Content-Type": "application/json"},
                json={"prompt": prompt},
                timeout=180,
            )
            if response.status_code >= 400:
                return None, response.text
            data = response.json()
            return data.get("audio_url") or data.get("url") or data.get("output") or str(data), None
        except Exception as e:
            return None, str(e)
    else:
        return None, "openai_prompt"

    if error:
        return None, error
    return normalize_media_output(output), None

