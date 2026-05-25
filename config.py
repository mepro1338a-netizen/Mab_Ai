from pathlib import Path
import os
import re
from urllib.parse import urlparse

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

try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except OSError as _data_dir_err:
    import sys
    print(
        f"[MaByte] WARN: DATA_DIR not writable ({DATA_DIR}): {_data_dir_err}",
        file=sys.stderr,
    )
DB_PATH = DATA_DIR / "mabai.db"

LOGO_PATH = BASE_DIR / "logo1.png"
FAVICON_PATH = BASE_DIR / "Logo24mp.png"
HEADER_PATH = BASE_DIR / "neuerheader.png"

_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)", re.IGNORECASE)
_HTTP_URL_RE = re.compile(r"https?://[^\s\]\)\(<>\"']+", re.IGNORECASE)


def normalize_app_base_url(raw: str | None, *, default: str = "http://localhost:8501") -> str:
    """
    Plain HTTPS/HTTP origin only — strips accidental markdown from Railway ENV.
    e.g. https://app.railway.app](https://app.railway.app) -> https://app.railway.app
    """
    s = (raw or "").strip().strip("\"'")
    if not s:
        return default.rstrip("/")

    md = _MARKDOWN_LINK_RE.search(s)
    if md:
        s = md.group(1).strip()
    elif "](" in s:
        _, tail = s.split("](", 1)
        s = tail.split(")", 1)[0].strip()
    elif s.startswith("[") and "]" in s:
        s = s.split("]", 1)[-1].lstrip("(").strip()

    found = _HTTP_URL_RE.search(s)
    if found:
        s = found.group(0)

    s = s.strip("[]()\"'<> ")

    while True:
        low = s.lower()
        if low.startswith("https://https://"):
            s = "https://" + s[16:]
        elif low.startswith("http://http://"):
            s = "http://" + s[14:]
        elif low.startswith("https://http://"):
            s = "https://" + s[13:]
        else:
            break

    if not re.match(r"^https?://", s, re.IGNORECASE):
        s = f"https://{s.lstrip('/')}"

    s = s.rstrip("/")
    parsed = urlparse(s)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return default.rstrip("/")
    return s


APP_BASE_URL = normalize_app_base_url(os.getenv("APP_BASE_URL"))

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
# Volle Redirect-URL (Priorität) — muss 1:1 in Google Console stehen
GOOGLE_OAUTH_REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "").strip()
# Pfad an öffentlicher Domain, Default "/" (Streamlit). Alternative: /oauth/google/callback
GOOGLE_OAUTH_REDIRECT_PATH = os.getenv("GOOGLE_OAUTH_REDIRECT_PATH", "/").strip() or "/"
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

OPENAI_TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o-mini")
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
        "price": "0€",
        "monthly_price": 0,
        "tokens": 25,
        "model": OPENAI_TEXT_MODEL,
        "max_output": 1200,
        "stripe_price_env": "",
        "badge": "Starter",
        "description": "Für erste Tests und einfache AI-Chats.",
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
        "price": "9,99€ / Monat",
        "monthly_price": 9.99,
        "tokens": 1000,
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
            "1.000 Tokens / Monat",
            "Developer OS",
            "Creative Workspace",
            "Music Studio",
        ],
    },

    "grand": {
        "label": "Grand",
        "tier": 2,
        "price": "49,99€ / Monat",
        "monthly_price": 49.99,
        "tokens": 5000,
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
        ],
        "limits": DAILY_LIMITS["grand"],
        "highlights": [
            "5.000 Tokens / Monat",
            "Content Engine",
            "Media Studio",
            "Automation Lab",
            "Auto-Posting möglich",
        ],
    },

    "elite": {
        "label": "Elite",
        "tier": 3,
        "price": "199,99€ / Monat",
        "monthly_price": 199.99,
        "tokens": 20000,
        "model": OPENAI_CODING_MODEL,
        "max_output": 6000,
        "stripe_price_env": "STRIPE_PRICE_ELITE",
        "badge": "Operating System",
        "description": "Für Power-User, Agent Workflows und Premium Automation.",
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
        "price": "9,99€",
        "amount": 9.99,
        "tokens": 1000,
    },

    "grand_tokens": {
        "label": "5.000 Tokens",
        "price": "49,99€",
        "amount": 49.99,
        "tokens": 5000,
    },

    "elite_tokens": {
        "label": "20.000 Tokens",
        "price": "199,99€",
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
    "match_recap": 1,
    "thumbnail_system": 2,
    "viral_analysis": 2,
    "reel_script": 2,
    "matchday_package": 3,
    "optimized_package": 2,
    "auto_posting": 5,
    "deep_match_analysis": 3,
    "full_campaign": 5,
}

# Feature registry: min_plan + category for guards & UI
FOOTBALL_FEATURES = {
    "api_fixtures": {
        "min_plan": "football_starter",
        "label": "Fixtures",
        "category": "api",
        "description": "Anstehende Spiele eines Teams",
    },
    "api_results": {
        "min_plan": "football_starter",
        "label": "Results",
        "category": "api",
        "description": "Letzte Ergebnisse & Spielverlauf",
    },
    "api_standings": {
        "min_plan": "football_starter",
        "label": "Standings",
        "category": "api",
        "description": "Tabellen & Ligapositionen",
    },
    "api_team_overview": {
        "min_plan": "football_starter",
        "label": "Team Overview",
        "category": "api",
        "description": "Teamsuche & Vereinsprofil",
    },
    "api_player_stats": {
        "min_plan": "football_pro",
        "label": "Player Stats",
        "category": "api",
        "description": "Spielstatistiken pro Fixture",
    },
    "api_injuries": {
        "min_plan": "football_pro",
        "label": "Injuries",
        "category": "api",
        "description": "Verletzungen & Ausfälle (API)",
    },
    "api_predictions": {
        "min_plan": "football_pro",
        "label": "Predictions",
        "category": "api",
        "description": "API-Prognosen & Wahrscheinlichkeiten",
    },
    "api_form_analysis": {
        "min_plan": "football_pro",
        "label": "Form Analysis",
        "category": "api",
        "description": "Formkurve aus letzten Spielen",
    },
    "api_head_to_head": {
        "min_plan": "football_pro",
        "label": "Head-to-Head",
        "category": "api",
        "description": "Direktvergleich zweier Teams",
    },
    "api_live_scores": {
        "min_plan": "football_pro",
        "label": "Live Scores",
        "category": "api",
        "description": "Live-Spiele weltweit",
    },
    "api_multi_league": {
        "min_plan": "football_elite",
        "label": "Multi-League Monitoring",
        "category": "api",
        "description": "Mehrere Ligen parallel überwachen",
    },
    "api_watchlists": {
        "min_plan": "football_elite",
        "label": "Team/Player Watchlists",
        "category": "api",
        "description": "Watchlists für Teams & Spieler",
    },
    "api_priority_cache": {
        "min_plan": "football_elite",
        "label": "Priority Cache",
        "category": "api",
        "description": "Kürzere Cache-TTL für Elite",
    },
    "ai_match_summary": {
        "min_plan": "football_starter",
        "label": "Simple AI Match Summary",
        "category": "ai",
        "action": "match_recap",
    },
    "ai_match_preview": {
        "min_plan": "football_pro",
        "label": "AI Match Preview",
        "category": "ai",
        "action": "matchday_package",
    },
    "ai_reel_hooks": {
        "min_plan": "football_pro",
        "label": "AI Reel Hooks",
        "category": "ai",
        "action": "reel_script",
    },
    "ai_predictions": {
        "min_plan": "football_pro",
        "label": "AI Predictions",
        "category": "ai",
        "action": "basic_prediction",
    },
    "ai_viral_analysis": {
        "min_plan": "football_pro",
        "label": "Viral Analysis",
        "category": "ai",
        "action": "viral_analysis",
    },
    "ai_matchday_reports": {
        "min_plan": "football_elite",
        "label": "Matchday Reports",
        "category": "ai",
        "action": "full_campaign",
    },
    "ai_viral_reel_generator": {
        "min_plan": "football_pro",
        "label": "Viral Football Reel Generator",
        "category": "ai",
        "action": "reel_script",
    },
    "ai_content_calendar": {
        "min_plan": "football_elite",
        "label": "Content Calendar",
        "category": "ai",
        "action": "full_campaign",
    },
    "export_reels_studio": {
        "min_plan": "football_pro",
        "label": "Export to Reels Studio",
        "category": "export",
    },
    "automation_triggers": {
        "min_plan": "football_elite",
        "label": "Automation Triggers",
        "category": "automation",
    },
    "ai_betting_intelligence": {
        "min_plan": "football_pro",
        "label": "AI Betting Intelligence",
        "category": "analysis",
        "description": "EV, Value Bets, Bookmaker-Vergleich (Analyse only)",
    },
    "ai_betting_advanced": {
        "min_plan": "football_elite",
        "label": "Advanced Betting AI",
        "category": "analysis",
        "description": "Live-Marktdaten, Multi-Markt Value Scan",
    },
    "ai_live_match_intelligence": {
        "min_plan": "football_pro",
        "label": "Live Match Intelligence (Preview)",
        "category": "analysis",
        "description": "Momentum & Basis-Live-Alerts",
    },
    "ai_elite_live_intelligence": {
        "min_plan": "football_elite",
        "label": "Elite Live Match Intelligence",
        "category": "analysis",
        "description": "Vollstaendige Live AI Match Intelligence",
        "action": "deep_match_analysis",
    },
    "elite_odds_calculator": {
        "min_plan": "football_pro",
        "label": "Odds / Quote Calculator",
        "category": "analysis",
        "description": "Mathematische Value-Bet-Analyse (keine Wettberatung)",
    },
}

FOOTBALL_PLANS = {
    "football_starter": {
        "label": "Football Starter",
        "tier": 1,
        "price": "19,99€ / Monat",
        "monthly_price": 19.99,
        "daily_ai_analyses": 5,
        "daily_api_requests": 80,
        "api_requests": 2500,
        "live_api_access": True,
        "priority_cache": False,
        "rate_limit_per_minute": 20,
        "stripe_price_env": "STRIPE_PRICE_FOOTBALL_STARTER",
        "badge": "Starter",
        "description": "Basis-API + einfache AI Match Summaries für Einsteiger.",
        "features": [
            "api_fixtures",
            "api_results",
            "api_standings",
            "api_team_overview",
            "ai_match_summary",
        ],
        "highlights": [
            "Fixtures, Results, Standings, Team Overview",
            "Simple AI Match Summary",
            "5 AI Analysen / Tag",
            "Keine Predictions · kein Reel-Export",
        ],
    },

    "football_pro": {
        "label": "Football Pro",
        "tier": 2,
        "price": "99,99€ / Monat",
        "monthly_price": 99.99,
        "daily_ai_analyses": 30,
        "daily_api_requests": 800,
        "api_requests": 25000,
        "live_api_access": True,
        "priority_cache": False,
        "rate_limit_per_minute": 60,
        "stripe_price_env": "STRIPE_PRICE_FOOTBALL_PRO",
        "badge": "Growth",
        "description": "Volle Analyse-API + AI Previews, Hooks & Reels-Export.",
        "features": [
            "api_player_stats",
            "api_injuries",
            "api_predictions",
            "api_form_analysis",
            "api_head_to_head",
            "api_live_scores",
            "ai_match_preview",
            "ai_reel_hooks",
            "ai_predictions",
            "ai_viral_reel_generator",
            "ai_betting_intelligence",
            "ai_live_match_intelligence",
            "export_reels_studio",
            "elite_odds_calculator",
        ],
        "highlights": [
            "Alles aus Starter",
            "Player Stats, H2H, Live Scores, Predictions",
            "AI Previews, Betting Intelligence, Viral Reels",
            "30 AI Analysen / Tag",
            "Export zu Reels Studio",
        ],
    },

    "football_elite": {
        "label": "Football Elite",
        "tier": 3,
        "price": "249,99€ / Monat",
        "monthly_price": 249.99,
        "daily_ai_analyses": 9999,
        "daily_api_requests": 5000,
        "api_requests": 100000,
        "live_api_access": True,
        "priority_cache": True,
        "rate_limit_per_minute": 240,
        "stripe_price_env": "STRIPE_PRICE_FOOTBALL_ELITE",
        "badge": "Infrastructure",
        "description": "Maximale Limits, Multi-League, Automation-ready.",
        "features": [
            "api_multi_league",
            "api_watchlists",
            "api_priority_cache",
            "ai_matchday_reports",
            "ai_content_calendar",
            "automation_triggers",
            "ai_betting_advanced",
            "ai_elite_live_intelligence",
            "ai_viral_reel_generator",
            "elite_odds_calculator",
        ],
        "highlights": [
            "Alles aus Pro",
            "Multi-League & Matchday Reports",
            "Elite Automation & Auto-Posting Architektur",
            "Advanced Betting AI & Priority Cache",
            "Unbegrenzte AI-Analysen",
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
        "description": "Für Agenturen, Netzwerke und Football Apps.",
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


def football_daily_ai_limit(plan_key):
    plan = get_football_plan(plan_key)
    if not plan:
        return 0
    return int(plan.get("daily_ai_analyses") or 0)


def football_daily_api_limit(plan_key):
    plan = get_football_plan(plan_key)
    if not plan:
        return 0
    if not plan.get("live_api_access"):
        return 0
    return int(plan.get("daily_api_requests") or 0)


def football_api_limit(plan_key):
    """Monthly-style cap (Elite); daily enforcement uses football_daily_api_limit."""
    plan = get_football_plan(plan_key)
    if not plan:
        return 0
    if not plan.get("live_api_access"):
        return 0
    return int(plan.get("api_requests") or 0)


def football_has_live_api(plan_key):
    plan = get_football_plan(plan_key)
    if not plan:
        return False
    return bool(plan.get("live_api_access"))


def football_has_feature(plan_key, feature_id):
    if feature_id not in FOOTBALL_FEATURES:
        return False
    min_plan = FOOTBALL_FEATURES[feature_id]["min_plan"]
    return football_plan_allows(plan_key, min_plan)


def football_feature_meta(feature_id):
    return FOOTBALL_FEATURES.get(feature_id) or {}


def football_features_for_plan(plan_key):
    """All features unlocked at or below this plan tier."""
    rank = football_plan_rank(plan_key)
    out = []
    for fid, meta in FOOTBALL_FEATURES.items():
        if football_plan_rank(meta.get("min_plan", "football_starter")) <= rank:
            out.append((fid, meta))
    return out


def football_priority_cache(plan_key):
    plan = get_football_plan(plan_key)
    return bool(plan and plan.get("priority_cache"))


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
