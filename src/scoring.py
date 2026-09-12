from __future__ import annotations

KEYWORD_WEIGHT = 0.5
SEMANTIC_WEIGHT = 0.5
MISSING_REQUIRED_PENALTY = 0.55


def final_score(keyword_score: float, semantic_score: float, missing_required_count: int) -> float:
    combined = KEYWORD_WEIGHT * keyword_score + SEMANTIC_WEIGHT * semantic_score
    penalty = MISSING_REQUIRED_PENALTY**missing_required_count
    return max(0.0, min(100.0, combined * penalty))
