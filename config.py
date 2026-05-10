from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

APP_NAME = "MaByte"
APP_TAGLINE = "Next Generation AI Platform"

# =========================
# DATA / DATABASE
# =========================

DATA_DIR = Path(
    os.getenv(
        "DATA_DIR",
        "/data" if Path("/data").exists() else BASE_DIR / "data",
    )
)

DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "mabai.db"

# =========================
# ASSETS
# =========================

LOGO_PATH = BASE_DIR / "logo1.png"
FAVICON_PATH = BASE_DIR / "Logo24mp.png"
HEADER_PATH = BASE_DIR / "neuerheader.png"

# =========================
# APP URL
# =========================

APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8501")

# =========================
# API KEYS
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")
FAL_KEY = os.getenv("FAL_KEY", "")

SUNO_API_KEY = os.getenv("SUNO_API_KEY", "")
SUNO_API_URL = os.getenv("SUNO_API_URL", "")

# =========================
# OPENAI MODELS
# =========================

OPENAI_TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-mini")
OPENAI_CODING_MODEL = os.getenv("OPENAI_CODING_MODEL", "gpt-4.1")
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

# =========================
# PROVIDERS
# =========================

IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "openai")
VIDEO_PROVIDER = os.getenv("VIDEO_PROVIDER", "replicate")
MUSIC_PROVIDER = os.getenv("MUSIC_PROVIDER", "openai")

# =========================
# STABILITY
# =========================

STABILITY_IMAGE_MODEL = os.getenv("STABILITY_IMAGE_MODEL", "core")

# =========================
# REPLICATE
# =========================

REPLICATE_VIDEO_MODEL = os.getenv("REPLICATE_VIDEO_MODEL", "")
REPLICATE_REELS_MODEL = os.getenv("REPLICATE_REELS_MODEL", REPLICATE_VIDEO_MODEL)
REPLICATE_MUSIC_MODEL = os.getenv("REPLICATE_MUSIC_MODEL", "")

# =========================
# FAL
# =========================

FAL_VIDEO_ENDPOINT = os.getenv("FAL_VIDEO_ENDPOINT", "")
FAL_MUSIC_ENDPOINT = os.getenv("FAL_MUSIC_ENDPOINT", "")

# =========================
# STRIPE
# =========================

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

STRIPE_PRICE_PRO = os.getenv("STRIPE_PRICE_PRO", "")
STRIPE_PRICE_GRAND = os.getenv("STRIPE_PRICE_GRAND", "")
STRIPE_PRICE_ELITE = os.getenv("STRIPE_PRICE_ELITE", "")

# =========================
# ROLES
# =========================

ROLE_LABELS = {
    "user": "User",
    "supporter": "Supporter",
    "moderator": "Moderator",
    "admin": "Admin",
    "owner": "Owner",
}

ROLE_LEVELS = {
    "user": 0,
    "supporter": 1,
    "moderator": 2,
    "admin": 3,
    "owner": 1337,
}

# =========================
# PLANS
# =========================

PLANS = {
    "free": {
        "label": "Free",
        "price": "0€",
        "tokens": 25,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 1000,
        "badge": "Starter",
        "color": "#5f6fff",
        "stripe_price_env": "",
        "features": [
            "chat",
            "dashboard",
            "support",
            "premium",
        ],
        "description": "Zum Testen von MaByte.",
    },

    "pro": {
        "label": "Pro",
        "price": "9,99€ / Monat",
        "tokens": 600,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 2200,
        "badge": "Creator",
        "color": "#2f7cf7",
        "stripe_price_env": "STRIPE_PRICE_PRO",
        "features": [
            "chat",
            "dashboard",
            "support",
            "premium",
            "coding",
            "image",
            "music",
        ],
        "description": "Für Creator: Coding, Image und Music AI.",
    },

    "grand": {
        "label": "Grand",
        "price": "49,99€ / Monat",
        "tokens": 2500,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 3500,
        "badge": "Growth",
        "color": "#875cff",
        "stripe_price_env": "STRIPE_PRICE_GRAND",
        "features": [
            "chat",
            "dashboard",
            "support",
            "premium",
            "coding",
            "image",
            "music",
            "video",
            "reels",
        ],
        "description": "Für Reels, Video AI, bessere APIs und besseren Support.",
    },

    "elite": {
        "label": "Elite",
        "price": "199,99€ / Monat",
        "tokens": 12000,
        "model": OPENAI_CODING_MODEL,
        "max_output": 7000,
        "badge": "Business",
        "color": "#ffcc4d",
        "stripe_price_env": "STRIPE_PRICE_ELITE",
        "features": ["all"],
        "description": "Alles freigeschaltet, Business-Level, beste Videoqualität.",
    },
}

# =========================
# TOKEN COST SYSTEM
# =========================

TOKEN_COSTS = {
    # BASIC
    "chat": 1,

    # AI TOOLS
    "coding": 4,
    "image": 15,
    "music": 10,

    # REELS
    "reels": 20,

    # VIDEO
    "video_base": 10,

    # VIDEO PRO SEKUNDE
    "video_second": 5,

    # QUALITY MULTIPLIER
    "video_quality_high": 1.35,
    "video_quality_business": 1.75,
}

# =========================
# DAILY LIMITS
# =========================

DAILY_VIDEO_LIMITS = {
    "free": 0,
    "pro": 0,
    "grand": 5,
    "elite": 25,
}

DAILY_REELS_LIMITS = {
    "free": 0,
    "pro": 0,
    "grand": 5,
    "elite": 25,
}

# =========================
# TOKEN VALUE SYSTEM
# =========================

TOKEN_REAL_VALUE = {
    "1_token_euro": 0.014,
}

# =========================
# VIDEO SETTINGS
# =========================

DEFAULT_VIDEO_SECONDS = 10
MIN_VIDEO_SECONDS = 3
MAX_VIDEO_SECONDS = 120

DEFAULT_REEL_SECONDS = 15
MIN_REEL_SECONDS = 5
MAX_REEL_SECONDS = 60

# =========================
# UI COLORS
# =========================

UI_COLORS = {
    "background": "#070b17",
    "sidebar": "#0d1324",
    "card": "#121b32",
    "card_light": "#182544",
    "border": "#22355e",
    "text": "#f4f7ff",
    "muted_text": "#9ca7c2",
    "primary": "#1f6ed4",
    "primary_hover": "#1859ad",
    "gold": "#ffcc4d",
    "danger": "#ff4d6d",
    "success": "#22c55e",
}

# =========================
# UI SETTINGS
# =========================

MAX_UPLOAD_MB = 100
MAX_IMAGE_PROMPTS = 4
MAX_REELS_PER_REQUEST = 3

# =========================
# FEATURE FLAGS
# =========================

ENABLE_VIDEO_AI = True
ENABLE_IMAGE_AI = True
ENABLE_MUSIC_AI = True
ENABLE_REELS_AI = True
ENABLE_CODING_AI = True

ENABLE_PAYMENTS = True
ENABLE_ADMIN_PANEL = True

# =========================
# SECURITY
# =========================

PASSWORD_MIN_LENGTH = 6
SESSION_TIMEOUT_MINUTES = 1440
MAX_LOGIN_ATTEMPTS = 10

# =========================
# OWNER
# =========================

OWNER_USERNAME = "mepro1337"

# =========================
# DEFAULTS
# =========================

DEFAULT_ROLE = "user"
DEFAULT_PLAN = "free"
DEFAULT_TOKENS = PLANS["free"]["tokens"]