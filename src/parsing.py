from __future__ import annotations

import re
from dataclasses import dataclass

PREFERRED_MARKERS = ["preferred", "nice to have", "nice-to-have", "bonus", "good to have", "plus"]
REQUIRED_MARKERS = ["require", "must have", "must-have", "mandatory"]


@dataclass(frozen=True)
class Requirement:
    text: str
    kind: str  # "required" or "preferred"


def _section_header_kind(line: str) -> str | None:
    lower = line.strip().lower().rstrip(":")
    if any(m in lower for m in PREFERRED_MARKERS):
        return "preferred"
    if any(m in lower for m in REQUIRED_MARKERS):
        return "required"
    return None


def _is_bullet(line: str) -> bool:
    return bool(re.match(r"^\s*[-*•]\s+", line))


def _looks_like_header(line: str) -> bool:
    stripped = line.strip()
    return stripped.endswith(":") or len(stripped.split()) <= 4


def _clean_bullet(line: str) -> str:
    return re.sub(r"^\s*[-*•]\s+", "", line).strip()


_INLINE_MARKER_RE = re.compile(r"\s*\(([^)]*)\)\s*$")


def _split_inline_marker(text: str) -> tuple[str, str | None]:
    match = _INLINE_MARKER_RE.search(text)
    if not match:
        return text, None
    kind = _section_header_kind(match.group(1))
    if kind is None:
        return text, None
    return text[: match.start()].strip(), kind


SKILLS_HEADERS = ["skills", "technical skills", "technologies"]
EXPERIENCE_HEADERS = ["experience", "work experience", "professional experience", "projects"]
EDUCATION_HEADERS = ["education", "academic background"]


@dataclass(frozen=True)
class ResumeSections:
    skills: str = ""
    experience: str = ""
    education: str = ""
    unclassified: str = ""


def _resume_header_kind(line: str) -> str | None:
    lower = line.strip().lower().rstrip(":")
    if lower in SKILLS_HEADERS:
        return "skills"
    if lower in EXPERIENCE_HEADERS:
        return "experience"
    if lower in EDUCATION_HEADERS:
        return "education"
    return None


def parse_resume(text: str) -> ResumeSections:
    buckets = {"skills": [], "experience": [], "education": [], "unclassified": []}
    current = "unclassified"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        header_kind = _resume_header_kind(line)
        if header_kind:
            current = header_kind
            continue
        buckets[current].append(line)
    return ResumeSections(
        skills="\n".join(buckets["skills"]),
        experience="\n".join(buckets["experience"]),
        education="\n".join(buckets["education"]),
        unclassified="\n".join(buckets["unclassified"]),
    )


def parse_jd(text: str) -> list[Requirement]:
    requirements: list[Requirement] = []
    current_kind = "required"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        header_kind = _section_header_kind(line)
        if header_kind and not _is_bullet(line) and _looks_like_header(line):
            current_kind = header_kind
            continue
        if _is_bullet(line):
            text_only, inline_kind = _split_inline_marker(_clean_bullet(line))
            if not text_only:
                continue
            requirements.append(Requirement(text=text_only, kind=inline_kind or current_kind))
    return requirements
