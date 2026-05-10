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
        "/data" if Path("/data").exists() else BASE_DIR / "data"
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
# APP
# =========================

APP_BASE_URL = os.getenv(
    "APP_BASE_URL",
    "http://localhost:8501"
)

# =========================
# API KEYS
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

REPLICATE_API_TOKEN = os.getenv(
    "REPLICATE_API_TOKEN",
    ""
)

STABILITY_API_KEY = os.getenv(
    "STABILITY_API_KEY",
    ""
)

FAL_KEY = os.getenv("FAL_KEY", "")

SUNO_API_KEY = os.getenv("SUNO_API_KEY", "")
SUNO_API_URL = os.getenv("SUNO_API_URL", "")

# =========================
# OPENAI MODELS
# =========================

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

# =========================
# PROVIDERS
# =========================

IMAGE_PROVIDER = os.getenv(
    "IMAGE_PROVIDER",
    "openai"
)

VIDEO_PROVIDER = os.getenv(
    "VIDEO_PROVIDER",
    "replicate"
)

MUSIC_PROVIDER = os.getenv(
    "MUSIC_PROVIDER",
    "openai"
)

# =========================
# STABILITY
# =========================

STABILITY_IMAGE_MODEL = os.getenv(
    "STABILITY_IMAGE_MODEL",
    "core"
)

# =========================
# REPLICATE
# =========================

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

# =========================
# FAL
# =========================

FAL_VIDEO_ENDPOINT = os.getenv(
    "FAL_VIDEO_ENDPOINT",
    ""
)

FAL_MUSIC_ENDPOINT = os.getenv(
    "FAL_MUSIC_ENDPOINT",
    ""
)

# =========================
# STRIPE
# =========================

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

# =========================
# ROLE SYSTEM
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
    "owner": 999,
}

# =========================
# PLAN SYSTEM
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

        "features": [
            "chat",
            "dashboard",
            "support",
        ],

        "description": """
        Perfekt zum Testen der Plattform.
        """,
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

        "description": """
        Für Creator und normale AI Nutzung.
        """,
    },

    "grand": {
        "label": "Grand",
        "price": "49,99€ / Monat",
        "tokens": 2500,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 3500,
        "badge": "Business",
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

        "description": """
        Für Agenturen, Reels Creator und Businesses.
        """,
    },

    "elite": {
        "label": "Elite",
        "price": "199,99€ / Monat",
        "tokens": 12000,
        "model": OPENAI_CODING_MODEL,
        "max_output": 7000,
        "badge": "Enterprise",
        "color": "#ffcc4d",

        "stripe_price_env": "STRIPE_PRICE_ELITE",

        "features": [
            "all"
        ],

        "description": """
        Maximale Leistung.
        Business-Level APIs.
        Beste Qualität.
        Alles freigeschaltet.
        """,
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
    "image": 12,
    "music": 10,
    "reels": 18,

    # VIDEO
    "video_base": 5,

    # PRO SEKUNDE
    "video_second": 1,

    # QUALITY MULTIPLIER
    "video_quality_high": 1.35,
    "video_quality_business": 1.75,
}

# =========================
# TOKEN VALUE SYSTEM
# =========================

TOKEN_REAL_VALUE = {
    "1_token_euro": 0.014,
}

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

    "primary": "#2f7cf7",

    "primary_hover": "#2468d4",

    "gold": "#ffcc4d",

    "danger": "#ff4d6d",

    "success": "#22c55e",
}

# =========================
# UI SETTINGS
# =========================

MAX_UPLOAD_MB = 100

DEFAULT_VIDEO_SECONDS = 15

MAX_VIDEO_SECONDS = 120

MAX_IMAGE_PROMPTS = 4

MAX_REELS_PER_REQUEST = 3

# =========================
# APP FEATURES
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