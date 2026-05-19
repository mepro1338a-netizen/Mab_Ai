# =========================================================
# MABYTE PRICING ENGINE
# pricing.py
# =========================================================

from math import ceil


# =========================================================
# TOKEN VALUE
# =========================================================

# 1 TOKEN = 0.02€
TOKEN_VALUE_EUR = 0.02

# Sicherheitsfaktor damit du NIE draufzahlst
SAFETY_MULTIPLIER = 2.0


# =========================================================
# BASE COSTS
# =========================================================

BASE_CHAT_COST = 5
BASE_IMAGE_COST = 20
BASE_REEL_SCRIPT_COST = 25
BASE_CODING_COST = 15
BASE_MUSIC_COST = 100


# =========================================================
# HELPERS
# =========================================================

def euro_to_tokens(euro_cost: float) -> int:
    """
    Wandelt API Kosten in sichere MaByte Tokens um.
    """

    final_cost = euro_cost * SAFETY_MULTIPLIER

    return max(
        1,
        ceil(final_cost / TOKEN_VALUE_EUR)
    )


# =========================================================
# CHAT
# =========================================================

def get_chat_cost() -> int:
    return BASE_CHAT_COST


# =========================================================
# IMAGE AI
# =========================================================

def get_image_cost(
    quality: str = "standard",
    size: str = "1024"
) -> int:

    base_euro = 0.12

    # Qualität
    if quality == "hd":
        base_euro *= 1.8

    # Größe
    if size == "2048":
        base_euro *= 2.0

    return euro_to_tokens(base_euro)


# =========================================================
# REEL SCRIPT
# =========================================================

def get_reel_script_cost(
    seconds: int = 7
) -> int:

    base = BASE_REEL_SCRIPT_COST

    if seconds > 7:
        base += 10

    if seconds > 15:
        base += 20

    return int(base)


# =========================================================
# VIDEO AI
# =========================================================

def get_video_cost(
    provider: str = "kling",
    seconds: int = 5,
    quality: str = "standard",
    with_audio: bool = False,
) -> int:

    # =====================================================
    # KLING
    # =====================================================

    if provider == "kling":

        euro = 0.40

        # Sekunden
        euro += seconds * 0.08

        # Qualität
        if quality == "premium":
            euro *= 1.8

        if quality == "cinematic":
            euro *= 2.5

        # Audio
        if with_audio:
            euro += 0.30

        return euro_to_tokens(euro)

    # =====================================================
    # RUNWAY
    # =====================================================

    elif provider == "runway":

        euro = 0.90

        euro += seconds * 0.18

        if quality == "premium":
            euro *= 2.0

        if quality == "cinematic":
            euro *= 3.0

        if with_audio:
            euro += 0.50

        return euro_to_tokens(euro)

    # =====================================================
    # DEFAULT
    # =====================================================

    return euro_to_tokens(0.50)


# =========================================================
# MUSIC AI
# =========================================================

def get_music_cost(
    length: str = "short"
) -> int:

    base = BASE_MUSIC_COST

    if length == "medium":
        base += 40

    elif length == "long":
        base += 80

    return int(base)


# =========================================================
# CODING AI
# =========================================================

def get_coding_cost(
    complexity: str = "normal"
) -> int:

    base = BASE_CODING_COST

    if complexity == "advanced":
        base += 20

    elif complexity == "fullstack":
        base += 50

    return int(base)


# =========================================================
# ANALYTICS
# =========================================================

def estimate_profit(
    token_price_eur: float,
    api_cost_eur: float,
    tokens_used: int,
) -> dict:

    revenue = token_price_eur * tokens_used

    profit = revenue - api_cost_eur

    margin = 0

    if revenue > 0:
        margin = round((profit / revenue) * 100, 2)

    return {
        "revenue_eur": round(revenue, 2),
        "api_cost_eur": round(api_cost_eur, 2),
        "profit_eur": round(profit, 2),
        "margin_percent": margin,
    }


# =========================================================
# TESTS
# =========================================================

if __name__ == "__main__":

    print("=== MABYTE PRICING ENGINE ===")

    print()

    print("CHAT:")
    print(get_chat_cost())

    print()

    print("IMAGE:")
    print(get_image_cost())

    print()

    print("REEL SCRIPT:")
    print(get_reel_script_cost())

    print()

    print("VIDEO KLING:")
    print(
        get_video_cost(
            provider="kling",
            seconds=7,
            quality="premium",
            with_audio=True,
        )
    )

    print()

    print("VIDEO RUNWAY:")
    print(
        get_video_cost(
            provider="runway",
            seconds=7,
            quality="cinematic",
            with_audio=True,
        )
    )

    print()

    print("MUSIC:")
    print(get_music_cost())

    print()

    print("CODING:")
    print(get_coding_cost())

    print()

    print("PROFIT CHECK:")
    print(
        estimate_profit(
            token_price_eur=0.02,
            api_cost_eur=1.20,
            tokens_used=180,
        )
    )