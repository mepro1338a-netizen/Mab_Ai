from openai import OpenAI

from config import OPENAI_API_KEY, PLANS
from providers import generate_image_provider, generate_video_provider, generate_music_provider


def openai_ready():
    return bool(OPENAI_API_KEY)


def get_client():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY missing in .env")
    return OpenAI(api_key=OPENAI_API_KEY)


def system_prompt(mode, language, memory=None):
    prompts = {
        "chat": "You are Mabyte Memory Chat. Work like ChatGPT: answer naturally, help with writing, ideas, planning and everyday questions.",
        "coding": "You are Mabyte Coding Area. Help build, debug and improve code. Provide complete working code when possible.",
        "content": "You are Mabyte Content Studio. Create TikTok and Instagram content ideas.",
        "script": "You are Mabyte Script Generator. Create high-retention scripts.",
        "reels": "You are Mabyte Short Reels Generator. Create ready-to-film TikTok, Instagram Reels and YouTube Shorts concepts.",
        "video": "You are Mabyte Video Generator. Create video prompts and production-ready concepts.",
        "music": "You are Mabyte Music Generator. Create music prompts, lyrics ideas, style direction and production-ready song concepts.",
    }

    memory_text = ""
    if memory:
        memory_text = "\\nUser memory:\\n" + "\\n".join([f"- {k}: {v}" for k, v in memory])

    return f"{prompts.get(mode, 'You are Mabyte.')}\\nAlways answer in {language}. Be useful, clear and concise.{memory_text}"


def ask_ai(history, prompt, plan="free", mode="chat", language="German", memory=None):
    if not openai_ready():
        return f"Demo Mode: OPENAI_API_KEY missing.\\n\\nPrompt:\\n{prompt}"

    client = get_client()
    plan_data = PLANS.get(plan, PLANS["free"])

    messages = [{"role": "system", "content": system_prompt(mode, language, memory)}]

    for role, content in history[-8:]:
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=plan_data["model"],
        messages=messages,
        temperature=0.35,
        max_tokens=plan_data["max_output"],
    )

    return response.choices[0].message.content.strip()


def generate_image(prompt):
    return generate_image_provider(prompt)


def generate_video(prompt, mode="Fast"):
    return generate_video_provider(prompt, mode)


def generate_music(prompt):
    output, error = generate_music_provider(prompt)

    if error == "openai_prompt":
        concept = ask_ai(
            history=[],
            prompt=f"Create a production-ready music generation prompt/brief for this idea:\\n{prompt}",
            plan="pro",
            mode="music",
            language="German",
            memory=None,
        )
        return concept, None

    return output, error

