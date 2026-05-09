from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_FREE_MODEL
from logger import log_info, log_error

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_chat(messages, model=OPENAI_FREE_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
        )

        text = response.choices[0].message.content

        usage = response.usage.total_tokens if response.usage else 0

        return True, {
            "text": text,
            "tokens": usage,
        }

    except Exception as e:
        log_error(f"Chat Fehler: {e}")
        return False, str(e)