from pathlib import Path

BASE_DIR = Path(__file__).parent

APP_NAME = "MAB.AI"
APP_TAGLINE = "AI workspace for creators, coders and businesses."

LOGO_PATH = BASE_DIR / "logo.png"
HEADER_PATH = BASE_DIR / "Header.png"

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
        "description": "Memory Chat inklusive.",
        "features": ["chat", "dashboard", "support", "premium"],
    },
    "pro": {
        "label": "Pro",
        "price": "9,99€ / Monat",
        "tokens": 800,
        "description": "Coding, Image Generator, Musik und Short Reels.",
        "features": ["chat", "dashboard", "support", "premium", "coding", "image", "music", "reels"],
    },
    "grand": {
        "label": "Grand",
        "price": "49,99€ / Monat",
        "tokens": 4000,
        "description": "Alles aus Pro plus AI Video Generator.",
        "features": ["chat", "dashboard", "support", "premium", "coding", "image", "music", "reels", "video"],
    },
    "elite": {
        "label": "Elite",
        "price": "199€ / Monat",
        "tokens": 999999,
        "description": "Alles freigeschaltet. Beste Qualität. Höchste API-Leistung.",
        "features": ["all"],
    },
}
