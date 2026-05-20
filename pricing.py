REEL_SCRIPT_COST = 45
REEL_VIDEO_BASE_COST = 90
AUTOMATION_UNLOCK_COST = 1000


def get_reel_script_cost():
    return REEL_SCRIPT_COST


def get_reel_video_cost(seconds=3):
    seconds = int(seconds)

    if seconds <= 3:
        return REEL_VIDEO_BASE_COST

    if seconds == 4:
        return 95

    if seconds == 5:
        return 100

    if seconds == 6:
        return 110

    return 120


def get_automation_unlock_cost():
    return AUTOMATION_UNLOCK_COST