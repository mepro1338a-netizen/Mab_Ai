from database import (
    spend_tokens,
    save_usage,
    add_audit_log,
    get_user,
)

from logger import log_info, log_error
from config import TOKEN_COSTS


def run_ai_task(username, tool, prompt, provider, generator_func, *args, **kwargs):
    if not username:
        return False, "Bitte zuerst einloggen.", None

    prompt = (prompt or "").strip()

    if not prompt:
        return False, "Bitte Prompt eingeben.", None

    cost = TOKEN_COSTS.get(tool, 1)

    ok, msg = spend_tokens(username, cost)

    if not ok:
        return False, msg, None

    log_info(f"AI Task gestartet | user={username} | tool={tool} | provider={provider}")

    try:
        success, result = generator_func(prompt, *args, **kwargs)

        if success:
            save_usage(
                username=username,
                tool=tool,
                prompt=prompt,
                tokens_used=0,
                cost_tokens=cost,
                api_provider=provider,
                status="success",
            )

            add_audit_log(
                actor=username,
                action=f"generate_{tool}",
                target=tool,
                details=prompt[:250],
            )

            user = get_user(username)

            log_info(f"AI Task erfolgreich | user={username} | tool={tool}")

            return True, result, user

        save_usage(
            username=username,
            tool=tool,
            prompt=prompt,
            tokens_used=0,
            cost_tokens=cost,
            api_provider=provider,
            status="failed",
        )

        log_error(f"AI Task fehlgeschlagen | user={username} | tool={tool} | error={result}")

        return False, result, get_user(username)

    except Exception as e:
        save_usage(
            username=username,
            tool=tool,
            prompt=prompt,
            tokens_used=0,
            cost_tokens=cost,
            api_provider=provider,
            status="error",
        )

        log_error(f"AI Task Exception | user={username} | tool={tool} | error={e}")

        return False, f"AI Fehler: {e}", get_user(username)

