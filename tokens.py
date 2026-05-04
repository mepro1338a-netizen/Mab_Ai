from config import TOKEN_COSTS


def estimate_cost(kind: str, prompt: str = "") -> int:
    base = TOKEN_COSTS.get(kind, 1)
    length = len(prompt or "")

    if kind == "chat":
        if length <= 700:
            return 1
        if length <= 1800:
            return 2
        return 4

    return base
