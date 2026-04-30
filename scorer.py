def score_prompt(prompt: str):
    score = 0

    if "Act as" in prompt:
        score += 20
    if "Audience" in prompt:
        score += 20
    if "Constraints" in prompt:
        score += 20
    if "Structure" in prompt:
        score += 20
    if len(prompt) > 120:
        score += 20

    return min(score, 100)
