from __future__ import annotations

DIMS = ("R", "M", "P", "I", "S", "F", "C")


def forty_sixty(primary: str, applicable: list[str]) -> dict[str, float]:
    dims = []
    for code in applicable:
        if code not in dims:
            dims.append(code)
    if primary not in dims:
        dims.insert(0, primary)
    if len(dims) == 1:
        return {dims[0]: 1.0}
    share = 0.60 / (len(dims) - 1)
    weights = {d: share for d in dims if d != primary}
    weights[primary] = 0.40
    total = sum(weights.values())
    if abs(total - 1.0) > 1e-9:
        # Absorb rounding into the primary so Σα = 1.
        weights[primary] += 1.0 - total
    return {k: round(v, 6) for k, v in weights.items()}


def weighted_quality(scores: dict[str, float], weights: dict[str, float]) -> float:
    used = {k: v for k, v in weights.items() if k in scores and scores[k] is not None}
    if not used:
        return 0.0
    denom = sum(used.values())
    return sum(scores[k] * w for k, w in used.items()) / denom
