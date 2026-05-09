from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

APP_NAME = "Mabyte"
APP_TAGLINE = "AI workspace for creators, coders and businesses."

# Railway Volume Support
DATA_DIR = Path(os.getenv("DATA_DIR", "/data" if Path("/data").exists() else BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "mabai.db"

# Assets
LOGO_PATH = BASE_DIR / "logo1.png"
FAVICON_PATH = BASE_DIR / "Logo24mp.png"
HEADER_PATH = BASE_DIR / "neuerheader.png"

# App URL
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8501")

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")

# OpenAI
OPENAI_TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-mini")
OPENAI_CODING_MODEL = os.getenv("OPENAI_CODING_MODEL", "gpt-4.1")
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

# Providers
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "openai")
VIDEO_PROVIDER = os.getenv("VIDEO_PROVIDER", "replicate")
MUSIC_PROVIDER = os.getenv("MUSIC_PROVIDER", "openai")

# Stability optional
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")
STABILITY_IMAGE_MODEL = os.getenv("STABILITY_IMAGE_MODEL", "core")

# Replicate
REPLICATE_VIDEO_MODEL = os.getenv("REPLICATE_VIDEO_MODEL", "")
REPLICATE_REELS_MODEL = os.getenv("REPLICATE_REELS_MODEL", REPLICATE_VIDEO_MODEL)
REPLICATE_MUSIC_MODEL = os.getenv("REPLICATE_MUSIC_MODEL", "")

# FAL optional
FAL_KEY = os.getenv("FAL_KEY", "")
FAL_VIDEO_ENDPOINT = os.getenv("FAL_VIDEO_ENDPOINT", "")
FAL_MUSIC_ENDPOINT = os.getenv("FAL_MUSIC_ENDPOINT", "")

# Suno optional
SUNO_API_URL = os.getenv("SUNO_API_URL", "")
SUNO_API_KEY = os.getenv("SUNO_API_KEY", "")

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

STRIPE_PRICE_PRO = os.getenv("STRIPE_PRICE_PRO", "")
STRIPE_PRICE_GRAND = os.getenv("STRIPE_PRICE_GRAND", "")
STRIPE_PRICE_ELITE = os.getenv("STRIPE_PRICE_ELITE", "")

ROLE_LABELS = {
    "user": "User",
    "supporter": "Supporter",
    "moderator": "Moderator",
    "admin": "Admin",
    "owner": "Owner",
}

PLANS = {
    "free": {
        "label": "Free",
        "price": "0€",
        "tokens": 3,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 1200,
        "features": ["chat", "dashboard", "support", "premium"],
    },
    "pro": {
        "label": "Pro",
        "price": "9,99€ / Monat",
        "tokens": 1200,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 2000,
        "stripe_price_env": "STRIPE_PRICE_PRO",
        "features": ["chat", "dashboard", "support", "premium", "coding", "image", "music", "reels"],
    },
    "grand": {
        "label": "Grand",
        "price": "49,99€ / Monat",
        "tokens": 4000,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 3000,
        "stripe_price_env": "STRIPE_PRICE_GRAND",
        "features": ["chat", "dashboard", "support", "premium", "coding", "image", "music", "reels", "video"],
    },
    "elite": {
        "label": "Elite",
        "price": "199€ / Monat",
        "tokens": 999999,
        "model": OPENAI_CODING_MODEL,
        "max_output": 6000,
        "stripe_price_env": "STRIPE_PRICE_ELITE",
        "features": ["all"],
    },
}

TOKEN_COSTS = {
    "chat": 1,
    "coding": 5,
    "image": 25,
    "music": 30,
    "reels": 80,
    "video": 150,
}
