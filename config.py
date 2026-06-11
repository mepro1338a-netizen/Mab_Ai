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
YOUTUBE_OAUTH_CLIENT_ID = os.getenv("YOUTUBE_OAUTH_CLIENT_ID", GOOGLE_CLIENT_ID).strip()
YOUTUBE_OAUTH_CLIENT_SECRET = os.getenv(
    "YOUTUBE_OAUTH_CLIENT_SECRET", GOOGLE_CLIENT_SECRET
).strip()
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
VIDEO_PROVIDER = os.getenv("VIDEO_PROVIDER", "auto").strip().lower()
MUSIC_PROVIDER = os.getenv("MUSIC_PROVIDER", "openai")

# VIDEO_MODEL = Railway-Alias (legacy); bevorzugt REPLICATE_VIDEO_MODEL
REPLICATE_VIDEO_MODEL = (
    os.getenv("REPLICATE_VIDEO_MODEL", "").strip()
    or os.getenv("VIDEO_MODEL", "").strip()
)
REPLICATE_REELS_MODEL = (
    os.getenv("REPLICATE_REELS_MODEL", "").strip() or REPLICATE_VIDEO_MODEL
)
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
FOOTBALL_API_CACHE_TTL = int(os.getenv("FOOTBALL_API_CACHE_TTL", "600") or 600)
FOOTBALL_API_LIVE_CACHE_TTL = int(os.getenv("FOOTBALL_API_LIVE_CACHE_TTL", "60") or 60)
FOOTBALL_API_FIXTURES_CACHE_TTL = int(os.getenv("FOOTBALL_API_FIXTURES_CACHE_TTL", "600") or 600)  # 10 min
FOOTBALL_API_STANDINGS_CACHE_TTL = int(os.getenv("FOOTBALL_API_STANDINGS_CACHE_TTL", "3600") or 3600)  # 1 h
FOOTBALL_API_INJURIES_CACHE_TTL = int(os.getenv("FOOTBALL_API_INJURIES_CACHE_TTL", "21600") or 21600)  # 6 h
FOOTBALL_API_TIMEOUT = int(os.getenv("FOOTBALL_API_TIMEOUT", "20") or 20)
FOOTBALL_DEFAULT_SEASON = int(os.getenv("FOOTBALL_DEFAULT_SEASON", "2025") or 2025)

# football-data.org v4 — Free-Tier Quelle für Spielpläne + Tabellen.
# API-Football bleibt optionaler Zusatz für Odds/Predictions/Injuries.
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "")
FOOTBALL_DATA_BASE_URL = os.getenv(
    "FOOTBALL_DATA_BASE_URL",
    "https://api.football-data.org/v4",
)
FOOTBALL_DATA_TIMEOUT = int(os.getenv("FOOTBALL_DATA_TIMEOUT", "20") or 20)
FOOTBALL_DATA_CACHE_TTL = int(os.getenv("FOOTBALL_DATA_CACHE_TTL", "21600") or 21600)  # 6 h
FOOTBALL_DATA_LIVE_CACHE_TTL = int(os.getenv("FOOTBALL_DATA_LIVE_CACHE_TTL", "120") or 120)
FOOTBALL_DATA_STANDINGS_CACHE_TTL = int(
    os.getenv("FOOTBALL_DATA_STANDINGS_CACHE_TTL", "43200") or 43200
)  # 12 h


def football_api_season() -> int:
    """API-Football season year (start year of e.g. 2025/26 → 2025)."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    now = datetime.now(ZoneInfo("Europe/Berlin"))
    return now.year if now.month >= 7 else now.year - 1


def football_api_seasons_to_try() -> list[int]:
    """Try calendar year, then previous year, then football season start year."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    now = datetime.now(ZoneInfo("Europe/Berlin"))
    cy, py = int(now.year), int(now.year) - 1
    primary = football_api_season()
    seen: set[int] = set()
    out: list[int] = []
    for year in (cy, py, primary, primary - 1):
        if year not in seen and year >= 2020:
            seen.add(year)
            out.append(year)
    for year in (2024, 2023, 2022):
        if year not in seen:
            seen.add(year)
            out.append(year)
    return out

# API-Football league IDs (v3) — Phase 2 beta whitelist only
# Tier 0=UEFA · 1=DE · 2=England · 3=Top leagues · 4=International
FOOTBALL_LEAGUE_GROUPS: dict[str, list[dict[str, str | int]]] = {
    "uefa": [
        {"id": 2, "name": "Champions League", "country": "Europe"},
        {"id": 3, "name": "Europa League", "country": "Europe"},
        {"id": 848, "name": "Conference League", "country": "Europe"},
        {"id": 32, "name": "World Cup - Qualification Europe", "country": "Europe"},
    ],
    "deutschland": [
        {"id": 78, "name": "1. Bundesliga", "country": "Germany"},
        {"id": 79, "name": "2. Bundesliga", "country": "Germany"},
        {"id": 81, "name": "DFB Pokal", "country": "Germany"},
    ],
    "england": [
        {"id": 39, "name": "Premier League", "country": "England"},
    ],
    "europa_top": [
        {"id": 140, "name": "La Liga", "country": "Spain"},
        {"id": 135, "name": "Serie A", "country": "Italy"},
        {"id": 61, "name": "Ligue 1", "country": "France"},
        {"id": 88, "name": "Eredivisie", "country": "Netherlands"},
        {"id": 94, "name": "Primeira Liga", "country": "Portugal"},
    ],
    "national": [
        {"id": 1, "name": "World Cup", "country": "World"},
        {"id": 4, "name": "Euro Championship", "country": "Europe"},
        {"id": 5, "name": "UEFA Nations League", "country": "Europe"},
    ],
}

_FOOTBALL_TIER_ORDER = (
    "uefa",
    "deutschland",
    "england",
    "europa_top",
    "national",
)

# Live Center sort: UCL → UEL → Bundesliga → PL → rest
FOOTBALL_LIVE_SORT_PRIORITY: dict[int, int] = {
    2: 10,
    3: 20,
    848: 30,
    78: 40,
    39: 50,
    79: 55,
    81: 56,
    140: 60,
    135: 61,
    61: 62,
    88: 63,
    94: 64,
    1: 70,
    4: 71,
    5: 72,
    32: 73,
}

FOOTBALL_LEAGUE_TIER: dict[int, int] = {}
FOOTBALL_LEAGUE_PRIORITY: dict[int, int] = {}
FOOTBALL_LEAGUE_META: dict[int, dict[str, str | int]] = {}

for _tier_idx, _group in enumerate(_FOOTBALL_TIER_ORDER):
    for _prio, _lg in enumerate(FOOTBALL_LEAGUE_GROUPS.get(_group, [])):
        _lid = int(_lg["id"])
        FOOTBALL_LEAGUE_TIER[_lid] = _tier_idx
        FOOTBALL_LEAGUE_PRIORITY[_lid] = _prio
        FOOTBALL_LEAGUE_META[_lid] = dict(_lg)

FOOTBALL_PREMIUM_LEAGUE_IDS = frozenset(
    _lid
    for _grp in ("uefa", "deutschland", "england", "europa_top", "national")
    for _lg in FOOTBALL_LEAGUE_GROUPS.get(_grp, [])
    for _lid in (int(_lg["id"]),)
)

# Football AI competition browser — strict league whitelists per filter
FOOTBALL_COMPETITION_GROUPS: dict[str, frozenset[int]] = {
    "deutschland": frozenset({78, 79, 81}),
    "uefa": frozenset({2, 3, 848}),
    "topligen": frozenset({39, 140, 135, 61, 88, 94}),
    "nationalteams": frozenset({1, 4, 5, 10}),
}

FOOTBALL_FRIENDLIES_LEAGUE_ID = 10

# API-Football Liga-ID -> football-data.org Wettbewerbs-Code (Free-Tier).
# Ohne Free-Tier-Quelle: Europa League (3), Conference League (848),
# 2. Bundesliga (79), DFB-Pokal (81), Nations League (5), Friendlies (10),
# WM-Quali Europa (32).
FOOTBALL_DATA_COMPETITION_CODES: dict[int, str] = {
    78: "BL1",   # 1. Bundesliga
    2: "CL",     # Champions League
    39: "PL",    # Premier League
    140: "PD",   # La Liga
    135: "SA",   # Serie A
    61: "FL1",   # Ligue 1
    88: "DED",   # Eredivisie
    94: "PPL",   # Primeira Liga
    1: "WC",     # World Cup
    4: "EC",     # Euro Championship
    40: "ELC",   # Championship (England)
    71: "BSA",   # Brasileirão Serie A
}

# football-data.org Wettbewerbs-ID -> API-Football Liga-ID (für den Fixture-Mapper,
# damit alle Konsumenten weiter mit den bekannten numerischen IDs arbeiten).
FOOTBALL_DATA_ID_TO_LEAGUE_ID: dict[int, int] = {
    2002: 78,    # BL1
    2001: 2,     # CL
    2021: 39,    # PL
    2014: 140,   # PD
    2019: 135,   # SA
    2015: 61,    # FL1
    2003: 88,    # DED
    2017: 94,    # PPL
    2000: 1,     # WC
    2018: 4,     # EC
    2016: 40,    # ELC
    2013: 71,    # BSA
}

# Football AI Topspiele — union of curated competition leagues (excl. friendlies id 10)
FOOTBALL_TOPSPIELE_LEAGUE_IDS = frozenset(
    lid
    for grp, ids in FOOTBALL_COMPETITION_GROUPS.items()
    for lid in ids
    if lid != FOOTBALL_FRIENDLIES_LEAGUE_ID
) | frozenset({1, 4, 5})

# Football AI betting board — top-tier whitelist (+ WM/Euro for curated feed)
FOOTBALL_BETTING_CORE_LEAGUE_IDS = frozenset(
    FOOTBALL_TOPSPIELE_LEAGUE_IDS | {1, 4}
)

FOOTBALL_UPCOMING_HORIZON_DAYS = 60

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
    "video_quality_high": 135,
    "video_quality_business": 1.75,
    "video_studio_base": 28,
    "video_studio_per_sec": 2,
    "video_ai_base": 120,
    "video_ai_per_sec": 18,
    "video_ai_hd_multiplier": 145,
    "reel_studio_base": 22,
    "reel_studio_per_sec": 3,
    "reel_ai_5s": 90,
    "reel_ai_7s": 110,
    "reel_ai_hd_7s": 130,
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
        "label": "Content Automation",
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
            "Content Automation",
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
    "ai_elite_betting_card": {
        "min_plan": "football_elite",
        "label": "Elite Betting Intelligence Card",
        "category": "analysis",
        "description": "Kompakte Tippempfehlung mit Confidence, Risiko & Value",
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
