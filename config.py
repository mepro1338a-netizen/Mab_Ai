from pathlib import Path
import os
from dotenv import load_dotenv

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

# =========================================================
# BASE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

APP_NAME = "Mabyte"
APP_TAGLINE = "AI workspace for creators, coders and businesses."

# =========================================================
# STORAGE / DATABASE
# =========================================================

DATA_DIR = Path(
    os.getenv(
        "DATA_DIR",
        "/data" if Path("/data").exists() else BASE_DIR / "data"
    )
)

DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "mabai.db"

# =========================================================
# ASSETS
# =========================================================

LOGO_PATH = BASE_DIR / "logo1.png"
FAVICON_PATH = BASE_DIR / "Logo24mp.png"
HEADER_PATH = BASE_DIR / "neuerheader.png"

# =========================================================
# APP URL
# =========================================================

APP_BASE_URL = os.getenv(
    "APP_BASE_URL",
    "http://localhost:8501"
)

# =========================================================
# API KEYS
# =========================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")

FAL_KEY = os.getenv("FAL_KEY", "")

SUNO_API_URL = os.getenv("SUNO_API_URL", "")
SUNO_API_KEY = os.getenv("SUNO_API_KEY", "")

# =========================================================
# OPENAI MODELS
# =========================================================

OPENAI_TEXT_MODEL = os.getenv(
    "OPENAI_TEXT_MODEL",
    "gpt-4.1-mini"
)

OPENAI_CODING_MODEL = os.getenv(
    "OPENAI_CODING_MODEL",
    "gpt-4.1"
)

OPENAI_IMAGE_MODEL = os.getenv(
    "OPENAI_IMAGE_MODEL",
    "gpt-image-1"
)

# =========================================================
# PROVIDERS
# =========================================================

IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "openai")
VIDEO_PROVIDER = os.getenv("VIDEO_PROVIDER", "replicate")
MUSIC_PROVIDER = os.getenv("MUSIC_PROVIDER", "openai")

# =========================================================
# REPLICATE
# =========================================================

REPLICATE_VIDEO_MODEL = os.getenv(
    "REPLICATE_VIDEO_MODEL",
    ""
)

REPLICATE_REELS_MODEL = os.getenv(
    "REPLICATE_REELS_MODEL",
    REPLICATE_VIDEO_MODEL
)

REPLICATE_MUSIC_MODEL = os.getenv(
    "REPLICATE_MUSIC_MODEL",
    ""
)

# =========================================================
# FAL
# =========================================================

FAL_VIDEO_ENDPOINT = os.getenv(
    "FAL_VIDEO_ENDPOINT",
    ""
)

FAL_MUSIC_ENDPOINT = os.getenv(
    "FAL_MUSIC_ENDPOINT",
    ""
)

# =========================================================
# STRIPE
# =========================================================

STRIPE_SECRET_KEY = os.getenv(
    "STRIPE_SECRET_KEY",
    ""
)

STRIPE_WEBHOOK_SECRET = os.getenv(
    "STRIPE_WEBHOOK_SECRET",
    ""
)

STRIPE_PRICE_PRO = os.getenv(
    "STRIPE_PRICE_PRO",
    ""
)

STRIPE_PRICE_GRAND = os.getenv(
    "STRIPE_PRICE_GRAND",
    ""
)

STRIPE_PRICE_ELITE = os.getenv(
    "STRIPE_PRICE_ELITE",
    ""
)

# =========================================================
# USER ROLES
# =========================================================

ROLE_LABELS = {
    "user": "User",
    "supporter": "Supporter",
    "moderator": "Moderator",
    "admin": "Admin",
    "owner": "Owner",
}

# =========================================================
# TOKEN COST SYSTEM
# =========================================================

TOKEN_COSTS = {

    # BASIC
    "chat": 1,

    # AI TOOLS
    "coding": 4,
    "image": 15,
    "music": 10,
    "reels": 20,

    # VIDEO
    "video_base": 10,

    # COST PER SECOND
    "video_second": 5,

    # QUALITY MULTIPLIERS
    "video_quality_high": 1.35,
    "video_quality_business": 1.75,
}

# =========================================================
# TOKEN REAL VALUE
# =========================================================

TOKEN_REAL_VALUE = {
    "1_token_euro": 0.014,
}

# =========================================================
# DAILY LIMITS
# =========================================================

DAILY_VIDEO_LIMITS = {
    "free": 0,
    "pro": 0,
    "grand": 10,
    "elite": 30,
}

# =========================================================
# AUTOMATION FEATURES
# =========================================================

AUTOMATION_FEATURES = {
    "instagram_posting": ["grand", "elite"],
    "tiktok_posting": ["grand", "elite"],
    "youtube_posting": ["grand", "elite"],
    "scheduled_posting": ["grand", "elite"],
}

# =========================================================
# PLANS
# =========================================================

PLANS = {

    # =====================================================
    # FREE
    # =====================================================

    "free": {
        "label": "Free",
        "price": "0€",
        "tokens": 3,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 1200,

        "features": [
            "chat",
        ],
    },

    # =====================================================
    # PRO
    # =====================================================

    "pro": {
        "label": "Pro",
        "price": "9,99€ / Monat",
        "tokens": 1200,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 2000,

        "stripe_price_env": "STRIPE_PRICE_PRO",

        "features": [
            "chat",
            "coding",
            "image",
            "music",
        ],
    },

    # =====================================================
    # GRAND
    # =====================================================

    "grand": {
        "label": "Grand",
        "price": "49,99€ / Monat",
        "tokens": 4000,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 3500,

        "stripe_price_env": "STRIPE_PRICE_GRAND",

        "features": [
            "chat",
            "coding",
            "image",
            "music",
            "reels",
            "video",
            "automation",
        ],
    },

    # =====================================================
    # ELITE
    # =====================================================

    "elite": {
        "label": "Elite",
        "price": "199€ / Monat",
        "tokens": 14000,
        "model": OPENAI_CODING_MODEL,
        "max_output": 6000,

        "stripe_price_env": "STRIPE_PRICE_ELITE",

        "features": [
            "all",
        ],
    },
}

# =========================================================
# UI COLORS
# =========================================================

UI_COLORS = {
    "background": "#070b17",
    "sidebar": "#0d1324",
    "card": "#121b32",

    "primary": "#1d9bf0",
    "primary_light": "#53b8ff",

    "text": "#ffffff",
    "muted": "#9bb0d1",

    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
}