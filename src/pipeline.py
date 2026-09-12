from __future__ import annotations

from dataclasses import dataclass, field

from src.evidence import Evidence, build_evidence
from src.explain import explain
from src.keyword_engine import KeywordMatch, keyword_score
from src.parsing import Requirement, parse_jd, parse_resume
from src.scoring import final_score
from src.semantic_engine import SemanticMatch, semantic_score

TOP_N_EXPLAINED = 3


@dataclass
class CandidateResult:
    name: str
    keyword_score: float
    semantic_score: float
    final_score: float
    keyword_matches: list[KeywordMatch]
    semantic_matches: list[SemanticMatch]
    evidence: Evidence
    explanation: str | None = None


def rank_candidates(jd_text: str, resumes: dict[str, str]) -> list[CandidateResult]:
    requirements: list[Requirement] = parse_jd(jd_text)

    results: list[CandidateResult] = []
    for name, resume_text in resumes.items():
        sections = parse_resume(resume_text)
        kw_score, kw_matches = keyword_score(requirements, sections)
        sm_score, sm_matches = semantic_score(requirements, sections)
        evidence = build_evidence(kw_matches, sm_matches)
        f_score = final_score(
            keyword_score=kw_score,
            semantic_score=sm_score,
            missing_required_count=len(evidence.missing_required),
        )
        results.append(
            CandidateResult(
                name=name,
                keyword_score=kw_score,
                semantic_score=sm_score,
                final_score=f_score,
                keyword_matches=kw_matches,
                semantic_matches=sm_matches,
                evidence=evidence,
            )
        )

    results.sort(key=lambda r: (r.final_score, r.keyword_score), reverse=True)

    for result in results[:TOP_N_EXPLAINED]:
        result.explanation = explain(result.evidence)

    return results
