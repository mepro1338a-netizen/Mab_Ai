from config import PLANS
from database import get_user, update_tokens, increment_usage, load_memory
from ai import ask_ai, generate_image, generate_video, generate_music
from tokens import estimate_cost


def refresh_user(username):
    return get_user(username)


def has_feature(user, feature):
    if not user:
        return False, "Please login first."

    if user.get("role") == "admin":
        return True, ""

    plan = user.get("plan", "free")
    features = PLANS.get(plan, PLANS["free"])["features"]

    if "all" in features or feature in features:
        return True, ""

    return False, f"{feature.title()} requires a higher plan."


def charge_tokens(username, cost):
    user = get_user(username)

    if not user:
        return False, "Please login first."

    if user["tokens"] < cost:
        return False, "Not enough tokens."

    update_tokens(username, -cost)
    return True, ""


def run_text_tool(username, prompt, mode, feature, language, history=None):
    user = get_user(username)

    ok, msg = has_feature(user, feature)
    if not ok:
        return msg, 0, False

    cost = estimate_cost(mode, prompt)

    ok, msg = charge_tokens(username, cost)
    if not ok:
        return msg, cost, False

    memory = load_memory(username) if mode == "chat" else []

    answer = ask_ai(
        history=history or [],
        prompt=prompt,
        plan=user["plan"],
        mode=mode,
        language=language,
        memory=memory,
    )

    return answer, cost, True


def process_chat(username, prompt, language, history=None):
    return run_text_tool(username, prompt, "chat", "chat", language, history)


def process_coding(username, task, language):
    prompt = f"""Help with this coding task:

{task}

Return:
- solution
- complete code if useful
- short explanation
"""
    return run_text_tool(username, prompt, "coding", "coding", language)


def process_content(username, topic, platform, niche, language):
    prompt = f"""Create content for {platform}.

Topic: {topic}
Niche: {niche}

Return:
- 5 viral ideas
- hook for each idea
- shot list
- caption
- CTA
- hashtags
- posting angle
"""
    answer, cost, ok = run_text_tool(username, prompt, "content", "content", language)
    if ok:
        increment_usage(username, "content_used")
    return answer, cost, ok


def process_script(username, topic, platform, style, language):
    prompt = f"""Create a high-retention {platform} script.

Topic: {topic}
Style: {style}

Return:
1. Hook
2. Full script
3. Scene structure
4. Caption
5. CTA
6. Hashtags
"""
    return run_text_tool(username, prompt, "script", "script", language)


def process_reels(username, topic, platform, language):
    prompt = f"""Create a ready-to-film short reel for {platform}.

Topic: {topic}

Return:
- 3 hook options
- 15-30 second script
- scene-by-scene shot list
- text overlays
- caption
- CTA
- hashtags
"""
    return run_text_tool(username, prompt, "reels", "reels", language)


def process_image(username, prompt):
    user = get_user(username)

    ok, msg = has_feature(user, "image")
    if not ok:
        return None, msg, 0, False

    cost = estimate_cost("image", prompt)

    ok, msg = charge_tokens(username, cost)
    if not ok:
        return None, msg, cost, False

    result, error = generate_image(prompt)

    if error:
        return None, error, cost, False

    increment_usage(username, "images_used")
    return result, "", cost, True


def process_video(username, prompt, mode_cost_key="video_fast"):
    user = get_user(username)

    ok, msg = has_feature(user, "video")
    if not ok:
        return None, msg, 0, False

    cost = estimate_cost(mode_cost_key, prompt)

    ok, msg = charge_tokens(username, cost)
    if not ok:
        return None, msg, cost, False

    mode_name = "Fast"
    if mode_cost_key == "reels":
        mode_name = "Fast"
    elif mode_cost_key == "video_quality":
        mode_name = "Quality"
    elif mode_cost_key == "video_premium":
        mode_name = "Premium"

    video, error = generate_video(prompt, mode_name)

    if error:
        return None, error, cost, False

    increment_usage(username, "videos_used")
    return video, "", cost, True


def process_music(username, prompt):
    user = get_user(username)
    ok, msg = has_feature(user, "music")
    if not ok:
        return None, msg, 0, False
    cost = estimate_cost("music", prompt)
    ok, msg = charge_tokens(username, cost)
    if not ok:
        return None, msg, cost, False
    music, error = generate_music(prompt)
    if error:
        return None, error, cost, False
    increment_usage(username, "music_used")
    return music, "", cost, True
