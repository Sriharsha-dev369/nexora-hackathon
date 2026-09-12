from __future__ import annotations

from dataclasses import dataclass

from src.keyword_engine import KeywordMatch
from src.parsing import Requirement
from src.semantic_engine import SemanticMatch


@dataclass(frozen=True)
class MatchedRequirement:
    requirement: Requirement
    match_type: str  # "keyword", "semantic", or "both"


@dataclass(frozen=True)
class Evidence:
    matched: list[MatchedRequirement]
    missing_required: list[Requirement]


def build_evidence(keyword_matches: list[KeywordMatch], semantic_matches: list[SemanticMatch]) -> Evidence:
    semantic_by_text = {m.requirement.text: m.matched for m in semantic_matches}

    matched: list[MatchedRequirement] = []
    missing_required: list[Requirement] = []

    for kw in keyword_matches:
        req = kw.requirement
        sm_matched = semantic_by_text.get(req.text, False)

        if kw.matched and sm_matched:
            matched.append(MatchedRequirement(requirement=req, match_type="both"))
        elif kw.matched:
            matched.append(MatchedRequirement(requirement=req, match_type="keyword"))
        elif sm_matched:
            matched.append(MatchedRequirement(requirement=req, match_type="semantic"))
        elif req.kind == "required":
            missing_required.append(req)

    return Evidence(matched=matched, missing_required=missing_required)
