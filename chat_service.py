from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

DEFAULT_CHAT_MODEL = "gpt-4o-mini"


def generate_chat(prompt, history=None):
    try:
        messages = [
            {
                "role": "system",
                "content": "Du bist Mabyte, ein hilfreicher deutschsprachiger AI-Assistent."
            }
        ]

        if history:
            for msg in history:
                if msg.get("role") in ["user", "assistant", "system"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

        messages.append({
            "role": "user",
            "content": prompt
        })

        response = client.chat.completions.create(
            model=DEFAULT_CHAT_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=700,
        )

        return True, response.choices[0].message.content

    except Exception as e:
        return False, str(e)
