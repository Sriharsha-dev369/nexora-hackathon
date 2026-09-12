from __future__ import annotations

from src.parsing import Requirement

REQUIRED_WEIGHT = 1.0
PREFERRED_WEIGHT = 0.4


def weight(requirement: Requirement) -> float:
    return REQUIRED_WEIGHT if requirement.kind == "required" else PREFERRED_WEIGHT
