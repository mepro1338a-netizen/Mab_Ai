from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_FREE_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_chat(prompt, history=None):
    try:
        messages = [
            {
                "role": "system",
                "content": "Du bist MAB.AI, ein hilfreicher deutschsprachiger AI-Assistent."
            }
        ]

        if history:
            for msg in history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        messages.append({
            "role": "user",
            "content": prompt
        })

        response = client.chat.completions.create(
            model=OPENAI_FREE_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=700,
        )

        answer = response.choices[0].message.content

        return True, answer

    except Exception as e:
        return False, str(e)