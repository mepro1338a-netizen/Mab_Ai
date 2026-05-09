from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_reel_plan(topic, niche, platform, style, duration):
    try:
        prompt = f"""
Erstelle ein komplettes virales Reel-Konzept.

Thema: {topic}
Nische: {niche}
Plattform: {platform}
Stil: {style}
Dauer: {duration} Sekunden

Gib aus:
1. Hook
2. Szene-für-Szene Skript
3. Voiceover Text
4. Caption
5. Hashtags
6. Video Prompt für AI Video Generator
7. Musik-Stimmung
8. Call-to-Action
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Du bist ein viraler Social-Media-Reels-Stratege für TikTok, Instagram Reels und YouTube Shorts."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=1200,
        )

        return True, response.choices[0].message.content

    except Exception as e:
        return False, str(e)