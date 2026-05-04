import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "MAB.AI"
APP_TAGLINE = "Was kann MAB.AI für dich tun?"

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "mab_ai_v13.db"
LOGO_PATH = Path(__file__).parent / "logo.png"

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_FREE_MODEL = os.getenv("OPENAI_FREE_MODEL", "gpt-4o-mini")
OPENAI_PRO_MODEL = os.getenv("OPENAI_PRO_MODEL", "gpt-4o-mini")
OPENAI_GRAND_MODEL = os.getenv("OPENAI_GRAND_MODEL", "gpt-4.1-mini")
OPENAI_ELITE_MODEL = os.getenv("OPENAI_ELITE_MODEL", "gpt-4.1-mini")
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

# Image providers
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "openai").lower()
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")
STABILITY_IMAGE_MODEL = os.getenv("STABILITY_IMAGE_MODEL", "stable-image-core")

# Video/Music providers
VIDEO_PROVIDER = os.getenv("VIDEO_PROVIDER", "replicate").lower()
MUSIC_PROVIDER = os.getenv("MUSIC_PROVIDER", "replicate").lower()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
REPLICATE_VIDEO_MODEL = os.getenv("REPLICATE_VIDEO_MODEL", "")
REPLICATE_MUSIC_MODEL = os.getenv("REPLICATE_MUSIC_MODEL", "")

FAL_KEY = os.getenv("FAL_KEY", "")
FAL_VIDEO_ENDPOINT = os.getenv("FAL_VIDEO_ENDPOINT", "")
FAL_MUSIC_ENDPOINT = os.getenv("FAL_MUSIC_ENDPOINT", "")

# Optional custom song provider, e.g. Suno-compatible API wrapper
SUNO_API_URL = os.getenv("SUNO_API_URL", "")
SUNO_API_KEY = os.getenv("SUNO_API_KEY", "")

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PRICE_PRO = os.getenv("STRIPE_PRICE_PRO", "")
STRIPE_PRICE_GRAND = os.getenv("STRIPE_PRICE_GRAND", "")
STRIPE_PRICE_ELITE = os.getenv("STRIPE_PRICE_ELITE", "")
STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", "http://localhost:8501")
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", "http://localhost:8501")

# Email
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "verify@mab.ai")

PLANS = {
    "free": {
        "label": "Free",
        "price": "0€",
        "tokens": 5,
        "model": OPENAI_FREE_MODEL,
        "features": ["chat"],
        "max_output": 500,
        "description": "Memory Chat inklusive. Perfekt zum Starten.",
    },
    "pro": {
        "label": "Pro",
        "price": "25€",
        "tokens": 800,
        "model": OPENAI_PRO_MODEL,
        "features": ["chat", "coding", "image", "music", "reels"],
        "max_output": 900,
        "description": "Coding, Bilder, Musik, TikTok/Instagram, Scripts und Short Reels.",
    },
    "grand": {
        "label": "Grand",
        "price": "50€",
        "tokens": 3000,
        "model": OPENAI_GRAND_MODEL,
        "features": ["chat", "coding", "image", "music", "reels", "video", "connect"],
        "max_output": 1200,
        "description": "Alles aus Pro plus AI Video Generator und Integrationen.",
    },
    "elite": {
        "label": "Elite",
        "price": "100€",
        "tokens": 6000,
        "model": OPENAI_ELITE_MODEL,
        "features": ["all"],
        "max_output": 1600,
        "description": "Alles freigeschaltet. Best API runs.",
    },
}

TOKEN_COSTS = {
    "chat": 1,
    "reels": 220,
    "coding": 5,
    "image": 15,
    "music": 18,
    "video_fast": 250,
    "video_quality": 500,
    "video_premium": 900,
}

TOKEN_PACKS = {
    "small": {"label": "Small Token Pack", "price": "4.99€", "tokens": 100, "description": "Extra tokens for short requests."},
    "creator": {"label": "Creator Token Pack", "price": "14.99€", "tokens": 400, "description": "Good for content, scripts, images and music."},
    "video": {"label": "Video Token Pack", "price": "29.99€", "tokens": 1000, "description": "Extra tokens for AI video generation."},
}

VIDEO_MODES = {
    "Fast": {"cost": 250, "seconds": "5-6s", "quality": "Fast / low cost", "margin_note": "Best margin. Recommended default."},
    "Quality": {"cost": 500, "seconds": "5-8s", "quality": "Better quality", "margin_note": "Balanced quality and profit."},
    "Premium": {"cost": 900, "seconds": "8-10s", "quality": "Best available model", "margin_note": "For Elite or high-value users."},
}

ROLE_LABELS = {"admin": "Admin", "moderator": "Moderator", "user": "User"}
