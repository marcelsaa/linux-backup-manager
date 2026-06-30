def is_yes(answer: str, yes_short: str) -> bool:
    return answer.strip().lower() in {"j", "y", yes_short}
