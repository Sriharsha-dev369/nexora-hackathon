from __future__ import annotations

import re
from dataclasses import dataclass

from src.parsing import Requirement, ResumeSections
from src.weights import weight

ALIASES: dict[str, list[str]] = {
    "javascript": ["js"],
    "typescript": ["ts"],
    "machine learning": ["ml"],
    "node.js": ["node", "nodejs"],
}


@dataclass(frozen=True)
class KeywordMatch:
    requirement: Requirement
    matched: bool


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _variants(requirement_text: str) -> list[str]:
    normalized = _normalize(requirement_text)
    variants = [normalized] + ALIASES.get(normalized, [])
    for canonical, aliases in ALIASES.items():
        if normalized in aliases:
            variants.append(canonical)
    return variants


def _resume_text(sections: ResumeSections) -> str:
    return _normalize(
        "\n".join([sections.skills, sections.experience, sections.education, sections.unclassified])
    )


def _is_present(requirement_text: str, resume_text: str) -> bool:
    for variant in _variants(requirement_text):
        # Alphanumeric-adjacency lookarounds, not \b: \b requires a word/non-word
        # transition, which breaks for terms that themselves start/end with a
        # non-word character (C++, .NET, C#).
        pattern = r"(?<![A-Za-z0-9])" + re.escape(variant) + r"(?![A-Za-z0-9])"
        if re.search(pattern, resume_text):
            return True
    return False


def keyword_score(requirements: list[Requirement], sections: ResumeSections) -> tuple[float, list[KeywordMatch]]:
    resume_text = _resume_text(sections)
    matches = [
        KeywordMatch(requirement=req, matched=_is_present(req.text, resume_text))
        for req in requirements
    ]
    if not matches:
        return 100.0, matches

    total_weight = sum(weight(m.requirement) for m in matches)
    matched_weight = sum(weight(m.requirement) for m in matches if m.matched)
    score = 100.0 * matched_weight / total_weight
    return score, matches
