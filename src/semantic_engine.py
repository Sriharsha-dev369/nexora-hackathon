from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from src.parsing import Requirement, ResumeSections
from src.weights import weight

SIMILARITY_MATCH_THRESHOLD = 0.45
# Raw cosine similarity from this model clusters roughly in [0.15, 0.75] for
# related-vs-unrelated tech text; rescale that range to 0-100 for visible spread.
RAW_SIMILARITY_FLOOR = 0.15
RAW_SIMILARITY_CEILING = 0.75


@dataclass(frozen=True)
class SemanticMatch:
    requirement: Requirement
    similarity: float
    matched: bool


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache(maxsize=None)
def _encode_cached(text: str) -> tuple[float, ...]:
    # JD requirement text repeats identically across every resume in a ranking
    # run; cache by text so the model only encodes each distinct string once.
    return tuple(_model().encode(text))


def _cosine(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    a_arr, b_arr = np.array(a), np.array(b)
    denom = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    if denom == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / denom)


def _rescale(raw: float) -> float:
    span = RAW_SIMILARITY_CEILING - RAW_SIMILARITY_FLOOR
    scaled = (raw - RAW_SIMILARITY_FLOOR) / span * 100.0
    return max(0.0, min(100.0, scaled))


def _best_section_text(sections: ResumeSections) -> str:
    # Skills + Experience/Projects is where semantic evidence for a JD
    # requirement is most likely to live; fall back to the unclassified catch-all.
    combined = "\n".join([sections.skills.strip(), sections.experience.strip()]).strip()
    return combined or sections.unclassified.strip()


def semantic_score(
    requirements: list[Requirement], sections: ResumeSections
) -> tuple[float, list[SemanticMatch]]:
    if not requirements:
        return 100.0, []

    resume_text = _best_section_text(sections) or " "
    resume_embedding = _encode_cached(resume_text)

    matches: list[SemanticMatch] = []
    for req in requirements:
        req_embedding = _encode_cached(req.text)
        raw = _cosine(req_embedding, resume_embedding)
        rescaled = _rescale(raw)
        matches.append(
            SemanticMatch(requirement=req, similarity=rescaled, matched=rescaled >= SIMILARITY_MATCH_THRESHOLD * 100)
        )

    total_weight = sum(weight(m.requirement) for m in matches)
    weighted_similarity = sum(weight(m.requirement) * m.similarity for m in matches)
    score = weighted_similarity / total_weight
    return score, matches
