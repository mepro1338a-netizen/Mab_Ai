REEL_SCRIPT_COST = 90
REEL_VIDEO_COST = 100
AUTOMATION_UNLOCK_COST = 1000

BASE_IMAGE_COST = 35
BASE_MUSIC_COST = 120
BASE_CODING_COST = 20


def get_reel_script_cost() -> int:
    return REEL_SCRIPT_COST


def get_reel_video_cost(seconds: int = 7) -> int:
    return REEL_VIDEO_COST


def get_automation_unlock_cost() -> int:
    return AUTOMATION_UNLOCK_COST


def get_image_cost(quality: str = "standard", size: str = "1024") -> int:
    cost = BASE_IMAGE_COST
    if quality == "hd":
        cost += 30
    size_key = str(size).strip()
    addons = {"512": -5, "1024": 0, "1536": 20, "2048": 40}
    cost += addons.get(size_key, 0)
    return max(cost, 25)


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