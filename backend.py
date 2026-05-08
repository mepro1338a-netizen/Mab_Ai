import os
import time
import requests
from openai import OpenAI
from database import get_user, spend_tokens, increment_usage
from config import TOKEN_COSTS

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")

TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-mini")
CODING_MODEL = os.getenv("OPENAI_CODING_MODEL", "gpt-4.1")
IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

REPLICATE_VIDEO_MODEL = os.getenv("REPLICATE_VIDEO_MODEL", "")
REPLICATE_REELS_MODEL = os.getenv("REPLICATE_REELS_MODEL", REPLICATE_VIDEO_MODEL)
REPLICATE_MUSIC_MODEL = os.getenv("REPLICATE_MUSIC_MODEL", "")


def refresh_user(username):
    return get_user(username)


def _openai_client():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY fehlt in Railway Variables.")
    return OpenAI(api_key=OPENAI_API_KEY)


def _text_response(prompt, model=TEXT_MODEL, system="Du bist MAB.AI, ein hilfreicher KI-Assistent."):
    client = _openai_client()
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return getattr(response, "output_text", None) or str(response)


def process_chat(username, prompt, language="German", history=None):
    cost = TOKEN_COSTS["chat"]
    ok, msg = spend_tokens(username, cost)
    if not ok:
        return msg, cost, False
    try:
        answer = _text_response(
            prompt,
            TEXT_MODEL,
            f"Antworte auf {language}. Du bist MAB.AI. Hilf klar, direkt und praxisnah."
        )
        return answer, cost, True
    except Exception as e:
        return f"API Fehler: {e}", cost, False


def process_coding(username, task, language="German"):
    cost = TOKEN_COSTS["coding"]
    ok, msg = spend_tokens(username, cost)
    if not ok:
        return msg, cost, False
    try:
        answer = _text_response(
            task,
            CODING_MODEL,
            f"Antworte auf {language}. Du bist ein Senior Software Engineer. Gib copy-paste-ready Code."
        )
        return answer, cost, True
    except Exception as e:
        return f"API Fehler: {e}", cost, False


def process_image(username, prompt):
    cost = TOKEN_COSTS["image"]
    ok, msg = spend_tokens(username, cost)
    if not ok:
        return None, msg, cost, False
    try:
        client = _openai_client()
        img = client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt,
            size="1024x1024",
            n=1,
        )
        item = img.data[0]
        increment_usage(username, "images")
        if getattr(item, "b64_json", None):
            return f"data:image/png;base64,{item.b64_json}", None, cost, True
        if getattr(item, "url", None):
            return item.url, None, cost, True
        return None, "Kein Bild zurückgegeben.", cost, False
    except Exception as e:
        return None, f"API Fehler: {e}", cost, False


def _replicate_prediction(model, prompt):
    if not REPLICATE_API_TOKEN:
        raise RuntimeError("REPLICATE_API_TOKEN fehlt in Railway Variables.")
    if not model:
        raise RuntimeError("Replicate Model fehlt. Setze REPLICATE_VIDEO_MODEL / REPLICATE_REELS_MODEL / REPLICATE_MUSIC_MODEL.")

    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
        "Prefer": "wait",
    }

    # model format: owner/name
    url = f"https://api.replicate.com/v1/models/{model}/predictions"
    r = requests.post(url, headers=headers, json={"input": {"prompt": prompt}}, timeout=120)
    if r.status_code >= 400:
        raise RuntimeError(r.text)
    data = r.json()
    output = data.get("output")
    if isinstance(output, list) and output:
        return output[0]
    return output or data.get("urls", {}).get("get") or str(data)


def process_video(username, prompt, mode="video"):
    cost = TOKEN_COSTS["reels"] if mode == "reels" else TOKEN_COSTS["video"]
    ok, msg = spend_tokens(username, cost)
    if not ok:
        return None, msg, cost, False
    try:
        model = REPLICATE_REELS_MODEL if mode == "reels" else REPLICATE_VIDEO_MODEL
        result = _replicate_prediction(model, prompt)
        increment_usage(username, "videos")
        return result, None, cost, True
    except Exception as e:
        return None, f"API Fehler: {e}", cost, False


def process_music(username, prompt):
    cost = TOKEN_COSTS["music"]
    ok, msg = spend_tokens(username, cost)
    if not ok:
        return None, msg, cost, False
    try:
        result = _replicate_prediction(REPLICATE_MUSIC_MODEL, prompt)
        increment_usage(username, "music")
        return result, None, cost, True
    except Exception as e:
        return None, f"API Fehler: {e}", cost, False
