from __future__ import annotations

from src.evidence import Evidence


def explain(evidence: Evidence) -> str:
    matched_texts = [m.requirement.text for m in evidence.matched]
    missing_texts = [r.text for r in evidence.missing_required]

    if matched_texts:
        matched_clause = "Matched: " + ", ".join(matched_texts) + "."
    else:
        matched_clause = "No requirements were matched."

    if missing_texts:
        missing_clause = "Missing required skills: " + ", ".join(missing_texts) + "."
    else:
        missing_clause = "No required skills appear to be missing."

    return f"{matched_clause} {missing_clause}"
