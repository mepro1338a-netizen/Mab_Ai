from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

APP_NAME = "MaByte"
APP_TAGLINE = "One AI system. Infinite workflows."
APP_POSITIONING = "The AI Operating System for creators, analysts and modern teams."

DATA_DIR = Path(
    os.getenv(
        "DATA_DIR",
        "/data" if Path("/data").exists() else BASE_DIR / "data",
    )
)

DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "mabai.db"

LOGO_PATH = BASE_DIR / "logo1.png"
FAVICON_PATH = BASE_DIR / "Logo24mp.png"
HEADER_PATH = BASE_DIR / "neuerheader.png"

APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8501")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
META_APP_ID = os.getenv("META_APP_ID", "")
META_APP_SECRET = os.getenv("META_APP_SECRET", "")
TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY", "")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "")
OAUTH_STATE_SECRET = os.getenv("OAUTH_STATE_SECRET", "")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")
FAL_KEY = os.getenv("FAL_KEY", "")

SUNO_API_URL = os.getenv("SUNO_API_URL", "")
SUNO_API_KEY = os.getenv("SUNO_API_KEY", "")

OPENAI_TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-mini")
OPENAI_CODING_MODEL = os.getenv("OPENAI_CODING_MODEL", "gpt-4.1")
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "openai")
VIDEO_PROVIDER = os.getenv("VIDEO_PROVIDER", "replicate")
MUSIC_PROVIDER = os.getenv("MUSIC_PROVIDER", "openai")

REPLICATE_VIDEO_MODEL = os.getenv("REPLICATE_VIDEO_MODEL", "")
REPLICATE_REELS_MODEL = os.getenv("REPLICATE_REELS_MODEL", REPLICATE_VIDEO_MODEL)
REPLICATE_MUSIC_MODEL = os.getenv("REPLICATE_MUSIC_MODEL", "")

FAL_VIDEO_ENDPOINT = os.getenv("FAL_VIDEO_ENDPOINT", "")
FAL_MUSIC_ENDPOINT = os.getenv("FAL_MUSIC_ENDPOINT", "")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

STRIPE_PRICE_PRO = os.getenv("STRIPE_PRICE_PRO", "")
STRIPE_PRICE_GRAND = os.getenv("STRIPE_PRICE_GRAND", "")
STRIPE_PRICE_ELITE = os.getenv("STRIPE_PRICE_ELITE", "")

STRIPE_PRICE_FOOTBALL_STARTER = os.getenv("STRIPE_PRICE_FOOTBALL_STARTER", "")
STRIPE_PRICE_FOOTBALL_PRO = os.getenv("STRIPE_PRICE_FOOTBALL_PRO", "")
STRIPE_PRICE_FOOTBALL_ELITE = os.getenv("STRIPE_PRICE_FOOTBALL_ELITE", "")

# API-Football (api-sports.io) — Live-Daten für Football Intelligence
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY", "")
FOOTBALL_API_BASE_URL = os.getenv(
    "FOOTBALL_API_BASE_URL",
    "https://v3.football.api-sports.io",
)
FOOTBALL_API_CACHE_TTL = int(os.getenv("FOOTBALL_API_CACHE_TTL", "300") or 300)
FOOTBALL_API_LIVE_CACHE_TTL = int(os.getenv("FOOTBALL_API_LIVE_CACHE_TTL", "60") or 60)
FOOTBALL_API_TIMEOUT = int(os.getenv("FOOTBALL_API_TIMEOUT", "20") or 20)
FOOTBALL_DEFAULT_SEASON = int(os.getenv("FOOTBALL_DEFAULT_SEASON", "2025") or 2025)

ROLE_LABELS = {
    "user": "User",
    "supporter": "Supporter",
    "moderator": "Moderator",
    "admin": "Admin",
    "owner": "Owner",
}

PLAN_ORDER = {
    "free": 0,
    "pro": 1,
    "grand": 2,
    "elite": 3,
}

TOKEN_REAL_VALUE = {
    "1_euro_equals": 100,
    "1_token_euro": 0.01,
}

TOKEN_COSTS = {
    "chat": 1,
    "coding": 10,
    "image": 15,
    "music": 50,
    "reels": 120,
    "viral_hook": 40,
    "reel_script": 150,
    "ai_reel": 300,
    "football_report": 80,
    "match_stats": 30,
    "match_recap": 120,
    "matchday_package": 300,
    "viral_analysis": 80,
    "thumbnail_system": 100,
    "football_automation": 250,
    "automation_job": 150,
    "video_base": 50,
    "video_second": 10,
    "video_quality_high": 1.35,
    "video_quality_business": 1.75,
    "auto_posting_unlock": 1000,
}

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

DAILY_VIDEO_LIMITS = {
    "free": DAILY_LIMITS["free"]["video"],
    "pro": DAILY_LIMITS["pro"]["video"],
    "grand": DAILY_LIMITS["grand"]["video"],
    "elite": DAILY_LIMITS["elite"]["video"],
}

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
        "min_plan": "free",
    },

    "automation_lab": {
        "label": "Automation Lab",
        "feature": "automation",
        "min_plan": "grand",
    },
}

AUTOMATION_FEATURES = {
    "instagram_posting": ["grand", "elite"],
    "tiktok_posting": ["grand", "elite"],
    "youtube_posting": ["grand", "elite"],
    "scheduled_posting": ["grand", "elite"],
}

PLANS = {
    "free": {
        "label": "Free",
        "tier": 0,
        "price": "0â‚¬",
        "monthly_price": 0,
        "tokens": 25,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 1200,
        "stripe_price_env": "",
        "badge": "Starter",
        "description": "FÃ¼r erste Tests und einfache AI-Chats.",
        "features": ["chat"],
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
        "price": "9,99â‚¬ / Monat",
        "monthly_price": 9.99,
        "tokens": 1000,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 2200,
        "stripe_price_env": "STRIPE_PRICE_PRO",
        "badge": "Creator",
        "description": "FÃ¼r Creator, Solo-Founder und Coding Workflows.",
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
            "1.000 Tokens / Monat",
            "Developer OS",
            "Creative Workspace",
            "Music Studio",
        ],
    },

    "grand": {
        "label": "Grand",
        "tier": 2,
        "price": "49,99â‚¬ / Monat",
        "monthly_price": 49.99,
        "tokens": 5000,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 3500,
        "stripe_price_env": "STRIPE_PRICE_GRAND",
        "badge": "Scale",
        "description": "FÃ¼r Content Engines, Reels, Videos und Automationen.",
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
        ],
        "limits": DAILY_LIMITS["grand"],
        "highlights": [
            "5.000 Tokens / Monat",
            "Content Engine",
            "Media Studio",
            "Automation Lab",
            "Auto-Posting mÃ¶glich",
        ],
    },

    "elite": {
        "label": "Elite",
        "tier": 3,
        "price": "199,99â‚¬ / Monat",
        "monthly_price": 199.99,
        "tokens": 20000,
        "model": OPENAI_CODING_MODEL,
        "max_output": 6000,
        "stripe_price_env": "STRIPE_PRICE_ELITE",
        "badge": "Operating System",
        "description": "FÃ¼r Power-User, Agent Workflows und Premium Automation.",
        "features": ["all"],
        "limits": DAILY_LIMITS["elite"],
        "highlights": [
            "20.000 Tokens / Monat",
            "Advanced Automation",
            "Business Level Video",
            "Highest Limits",
            "Priority Access",
        ],
    },
}

TOKEN_PACKAGES = {
    "pro_tokens": {
        "label": "1.000 Tokens",
        "price": "9,99â‚¬",
        "amount": 9.99,
        "tokens": 1000,
    },

    "grand_tokens": {
        "label": "5.000 Tokens",
        "price": "49,99â‚¬",
        "amount": 49.99,
        "tokens": 5000,
    },

    "elite_tokens": {
        "label": "20.000 Tokens",
        "price": "199,99â‚¬",
        "amount": 199.99,
        "tokens": 20000,
    },
}

FOOTBALL_PLAN_ORDER = {
    "none": 0,
    "football_starter": 1,
    "football_pro": 2,
    "football_elite": 3,
    "football_b2b": 4,
}

FOOTBALL_ACTION_COSTS = {
    "basic_stats": 1,
    "basic_prediction": 1,
    "ai_caption": 1,
    "viral_hook": 1,
    "match_recap": 2,
    "thumbnail_system": 2,
    "viral_analysis": 2,
    "reel_script": 3,
    "matchday_package": 5,
    "optimized_package": 4,
    "auto_posting": 5,
    "deep_match_analysis": 6,
    "full_campaign": 10,
}

FOOTBALL_PLANS = {
    "football_starter": {
        "label": "Football Starter",
        "tier": 1,
        "price": "19,99â‚¬ / Monat",
        "monthly_price": 19.99,
        "ai_actions": 100,
        "api_requests": 0,
        "rate_limit_per_minute": 0,
        "stripe_price_env": "STRIPE_PRICE_FOOTBALL_STARTER",
        "badge": "Creator",
        "description": "FÃ¼r kleine Football Creator & Seiten.",
        "features": [
            "Basic Match Stats",
            "Basic Predictions",
            "AI Captions",
            "Match Recaps",
            "Reel Ideas",
        ],
        "highlights": [
            "100 Football AI Actions",
            "Basic Match Stats",
            "AI Captions",
            "Match Recaps",
            "Reel Ideen",
        ],
    },

    "football_pro": {
        "label": "Football Pro",
        "tier": 2,
        "price": "99,99â‚¬ / Monat",
        "monthly_price": 99.99,
        "ai_actions": 750,
        "api_requests": 25000,
        "rate_limit_per_minute": 60,
        "stripe_price_env": "STRIPE_PRICE_FOOTBALL_PRO",
        "badge": "Growth",
        "description": "FÃ¼r ernsthafte Football Creator & Content Systeme.",
        "features": [
            "Live Match Data",
            "AI Match Analysis",
            "Reel Generator",
            "Auto Hooks",
            "Auto Posting",
            "High Volume API Access",
        ],
        "highlights": [
            "750 Football AI Actions",
            "Live Match Data",
            "AI Match Analysis",
            "Auto Posting",
            "25k API Requests",
        ],
    },

    "football_elite": {
        "label": "Football Elite",
        "tier": 3,
        "price": "249,99â‚¬ / Monat",
        "monthly_price": 249.99,
        "ai_actions": 2500,
        "api_requests": 100000,
        "rate_limit_per_minute": 240,
        "stripe_price_env": "STRIPE_PRICE_FOOTBALL_ELITE",
        "badge": "Infrastructure",
        "description": "FÃ¼r automatisierte Football Content Systeme & Netzwerke.",
        "features": [
            "Everything in Football Pro",
            "Multi Account Support",
            "Webhooks",
            "Priority Processing",
            "Advanced Automation",
            "High Volume API Access",
        ],
        "highlights": [
            "2.500 Football AI Actions",
            "100k API Requests",
            "Multi Account Support",
            "Webhooks",
            "Priority Processing",
        ],
    },

    "football_b2b": {
        "label": "Football B2B",
        "tier": 4,
        "price": "Auf Anfrage",
        "monthly_price": None,
        "ai_actions": None,
        "api_requests": None,
        "rate_limit_per_minute": None,
        "stripe_price_env": "",
        "badge": "Enterprise",
        "description": "FÃ¼r Agenturen, Netzwerke und Football Apps.",
        "features": [
            "Custom API Limits",
            "White Label",
            "Dedicated Support",
            "Custom Automation",
            "Team Access",
        ],
        "highlights": [
            "Custom AI Actions",
            "Custom API Limits",
            "White Label",
            "Team Access",
            "Dedicated Support",
        ],
    },
}

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


def football_plan_rank(plan_key):
    return FOOTBALL_PLAN_ORDER.get(plan_key, 0)


def get_football_plan(plan_key):
    return FOOTBALL_PLANS.get(plan_key)


def football_plan_allows(current_plan, required_plan):
    return football_plan_rank(current_plan) >= football_plan_rank(required_plan)


def football_action_cost(action):
    return int(FOOTBALL_ACTION_COSTS.get(action, 1) or 1)


def football_actions_for_plan(plan_key):
    plan = get_football_plan(plan_key)
    if not plan:
        return 0
    return plan.get("ai_actions")


def football_api_limit(plan_key):
    plan = get_football_plan(plan_key)
    if not plan:
        return 0
    return plan.get("api_requests") or 0


def token_value_euro(tokens):
    return round(float(tokens or 0) / 100, 2)

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
