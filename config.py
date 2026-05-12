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

APP_NAME = "MaByte"
APP_TAGLINE = "One AI system. Infinite workflows."
APP_POSITIONING = "The AI Operating System for creators, analysts and modern teams."

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

REPLICATE_VIDEO_MODEL = os.getenv("REPLICATE_VIDEO_MODEL", "")
REPLICATE_REELS_MODEL = os.getenv("REPLICATE_REELS_MODEL", REPLICATE_VIDEO_MODEL)
REPLICATE_MUSIC_MODEL = os.getenv("REPLICATE_MUSIC_MODEL", "")

# =========================================================
# FAL
# =========================================================

FAL_VIDEO_ENDPOINT = os.getenv("FAL_VIDEO_ENDPOINT", "")
FAL_MUSIC_ENDPOINT = os.getenv("FAL_MUSIC_ENDPOINT", "")

# =========================================================
# STRIPE
# =========================================================

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

STRIPE_PRICE_PRO = os.getenv("STRIPE_PRICE_PRO", "")
STRIPE_PRICE_GRAND = os.getenv("STRIPE_PRICE_GRAND", "")
STRIPE_PRICE_ELITE = os.getenv("STRIPE_PRICE_ELITE", "")

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
# WORKSPACES
# =========================================================

WORKSPACES = {
    "ai_assistant": {
        "label": "AI Assistant",
        "feature": "chat",
        "min_plan": "free",
    },

    "creative_workspace": {
        "label": "Creative Workspace",
        "feature": "image",
        "min_plan": "pro",
    },

    "content_engine": {
        "label": "Content Engine",
        "feature": "reels",
        "min_plan": "grand",
    },

    "developer_os": {
        "label": "Developer OS",
        "feature": "coding",
        "min_plan": "pro",
    },

    "media_studio": {
        "label": "Media Studio",
        "feature": "video",
        "min_plan": "grand",
    },

    "music_studio": {
        "label": "Music Studio",
        "feature": "music",
        "min_plan": "pro",
    },

    "football_intelligence": {
        "label": "Football Intelligence",
        "feature": "football",
        "min_plan": "elite",
    },

    "automation_lab": {
        "label": "Automation Lab",
        "feature": "automation",
        "min_plan": "grand",
    },
}

# =========================================================
# PLAN ORDER
# =========================================================

PLAN_ORDER = {
    "free": 0,
    "pro": 1,
    "grand": 2,
    "elite": 3,
}

# =========================================================
# TOKEN COST SYSTEM
# =========================================================

TOKEN_COSTS = {
    # CORE
    "chat": 1,

    # WORKSPACES
    "coding": 10,
    "image": 10,
    "music": 50,
    "reels": 20,
    "football_report": 80,
    "automation_job": 100,

    # VIDEO
    "video_base": 10,
    "video_second": 5,

    # QUALITY MULTIPLIERS
    "video_quality_high": 1.35,
    "video_quality_business": 1.75,

    # UNLOCKS
    "auto_posting_unlock": 1000,
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

DAILY_LIMITS = {
    "free": {
        "chat": 25,
        "coding": 0,
        "image": 0,
        "music": 0,
        "reels": 0,
        "video": 0,
        "football_report": 0,
        "automation_job": 0,
    },

    "pro": {
        "chat": 300,
        "coding": 50,
        "image": 40,
        "music": 10,
        "reels": 0,
        "video": 0,
        "football_report": 0,
        "automation_job": 0,
    },

    "grand": {
        "chat": 1000,
        "coding": 200,
        "image": 120,
        "music": 40,
        "reels": 30,
        "video": 10,
        "football_report": 3,
        "automation_job": 20,
    },

    "elite": {
        "chat": 5000,
        "coding": 1000,
        "image": 500,
        "music": 150,
        "reels": 150,
        "video": 30,
        "football_report": 50,
        "automation_job": 250,
    },
}

# Backwards compatibility
DAILY_VIDEO_LIMITS = {
    "free": DAILY_LIMITS["free"]["video"],
    "pro": DAILY_LIMITS["pro"]["video"],
    "grand": DAILY_LIMITS["grand"]["video"],
    "elite": DAILY_LIMITS["elite"]["video"],
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
    "free": {
        "label": "Free",
        "tier": 0,
        "price": "0€",
        "monthly_price": 0,
        "tokens": 25,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 1200,
        "stripe_price_env": "",
        "badge": "Starter",
        "description": "Für erste Tests und einfache AI-Chats.",

        "features": [
            "chat",
        ],

        "limits": DAILY_LIMITS["free"],

        "highlights": [
            "AI Assistant",
            "25 Start Tokens",
            "Basic Memory Chat",
        ],
    },

    "pro": {
        "label": "Pro",
        "tier": 1,
        "price": "9,99€ / Monat",
        "monthly_price": 9.99,
        "tokens": 1200,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 2200,
        "stripe_price_env": "STRIPE_PRICE_PRO",
        "badge": "Creator",
        "description": "Für Creator, Solo-Founder und Coding Workflows.",

        "features": [
            "chat",
            "coding",
            "image",
            "music",
            "developer_os",
            "creative_workspace",
            "music_studio",
        ],

        "limits": DAILY_LIMITS["pro"],

        "highlights": [
            "Developer OS",
            "Creative Workspace",
            "Music Studio",
            "1200 Tokens / Monat",
        ],
    },

    "grand": {
        "label": "Grand",
        "tier": 2,
        "price": "49,99€ / Monat",
        "monthly_price": 49.99,
        "tokens": 4000,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 3500,
        "stripe_price_env": "STRIPE_PRICE_GRAND",
        "badge": "Scale",
        "description": "Für Content Engines, Reels, Videos und Automationen.",

        "features": [
            "chat",
            "coding",
            "image",
            "music",
            "reels",
            "video",
            "automation",
            "content_engine",
            "media_studio",
            "automation_lab",
            "football",
        ],

        "limits": DAILY_LIMITS["grand"],

        "highlights": [
            "Content Engine",
            "Media Studio",
            "Automation Lab",
            "4000 Tokens / Monat",
            "Auto-Posting möglich",
        ],
    },

    "elite": {
        "label": "Elite",
        "tier": 3,
        "price": "199€ / Monat",
        "monthly_price": 199,
        "tokens": 14000,
        "model": OPENAI_CODING_MODEL,
        "max_output": 6000,
        "stripe_price_env": "STRIPE_PRICE_ELITE",
        "badge": "Operating System",
        "description": "Für Power-User, Agent Workflows und Football Intelligence.",

        "features": [
            "all",
        ],

        "limits": DAILY_LIMITS["elite"],

        "highlights": [
            "Football Intelligence",
            "Advanced Automation",
            "Business Level Video",
            "14000 Tokens / Monat",
            "Highest Limits",
        ],
    },
}

# =========================================================
# PREMIUM HELPERS
# =========================================================

def plan_rank(plan_key):
    return PLAN_ORDER.get(plan_key, 0)


def plan_allows(current_plan, required_plan):
    return plan_rank(current_plan) >= plan_rank(required_plan)


def get_plan(plan_key):
    return PLANS.get(plan_key, PLANS["free"])


def get_plan_features(plan_key):
    return get_plan(plan_key).get("features", [])


def has_feature(plan_key, feature):
    features = get_plan_features(plan_key)

    return "all" in features or feature in features


def workspace_allowed(plan_key, workspace_key):
    workspace = WORKSPACES.get(workspace_key)

    if not workspace:
        return False

    required_plan = workspace.get("min_plan", "free")
    feature = workspace.get("feature")

    return plan_allows(plan_key, required_plan) and has_feature(plan_key, feature)


def feature_daily_limit(plan_key, feature):
    plan = get_plan(plan_key)
    limits = plan.get("limits", {})

    return int(limits.get(feature, 0) or 0)

# =========================================================
# UI COLORS
# =========================================================

UI_COLORS = {
    "background": "#020617",
    "sidebar": "#071427",
    "card": "#0f172a",
    "card_alt": "#102342",

    "primary": "#38bdf8",
    "primary_dark": "#1d4ed8",
    "primary_light": "#7dd3fc",

    "text": "#ffffff",
    "muted": "#9bb0d1",

    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
}