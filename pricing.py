from math import ceil


TOKEN_VALUE_EUR = 0.01
SAFETY_MULTIPLIER = 2.8

BASE_CHAT_COST = 5
BASE_REEL_SCRIPT_COST = 60
BASE_REEL_AUTOMATION_COST = 180
BASE_CODING_COST = 20
BASE_MUSIC_COST = 120


def euro_to_tokens(euro_cost: float) -> int:
    safe_cost = float(euro_cost) * SAFETY_MULTIPLIER
    return max(1, ceil(safe_cost / TOKEN_VALUE_EUR))


def get_chat_cost() -> int:
    return BASE_CHAT_COST


def get_image_cost(quality: str = "standard", size: str = "1024") -> int:
    euro = 0.10

    if quality == "hd":
        euro *= 2.0

    if size == "2048":
        euro *= 2.2

    return max(35, euro_to_tokens(euro))


def get_reel_script_cost(seconds: int = 7) -> int:
    cost = BASE_REEL_SCRIPT_COST

    if seconds > 7:
        cost += 25

    if seconds > 12:
        cost += 40

    return cost


def get_reel_automation_cost(
    seconds: int = 7,
    provider: str = "kling",
    quality: str = "standard",
    with_audio: bool = False,
    auto_caption: bool = True,
    auto_schedule: bool = True,
) -> int:
    video_cost = get_video_cost(
        provider=provider,
        seconds=seconds,
        quality=quality,
        with_audio=with_audio,
    )

    automation_cost = BASE_REEL_AUTOMATION_COST

    if auto_caption:
        automation_cost += 40

    if auto_schedule:
        automation_cost += 40

    return int(video_cost + automation_cost)


def get_video_cost(
    provider: str = "kling",
    seconds: int = 7,
    quality: str = "standard",
    with_audio: bool = False,
) -> int:
    provider = provider.lower()

    if provider == "kling":
        euro = 0.65 + (seconds * 0.14)

        if quality == "premium":
            euro *= 1.9

        if quality == "cinematic":
            euro *= 2.8

        if with_audio:
            euro += 0.45

        return max(180, euro_to_tokens(euro))

    if provider == "runway":
        euro = 1.20 + (seconds * 0.28)

        if quality == "premium":
            euro *= 2.2

        if quality == "cinematic":
            euro *= 3.4

        if with_audio:
            euro += 0.70

        return max(320, euro_to_tokens(euro))

    return max(180, euro_to_tokens(1.00))


def get_music_cost(length: str = "short") -> int:
    cost = BASE_MUSIC_COST

    if length == "medium":
        cost += 80

    if length == "long":
        cost += 150

    return cost


def get_coding_cost(complexity: str = "normal") -> int:
    cost = BASE_CODING_COST

    if complexity == "advanced":
        cost += 35

    if complexity == "fullstack":
        cost += 90

    return cost