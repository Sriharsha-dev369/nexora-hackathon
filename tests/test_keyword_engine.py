from src.parsing import Requirement, ResumeSections
from src.keyword_engine import keyword_score


def test_full_score_when_every_required_skill_is_present():
    reqs = [Requirement(text="Python", kind="required"), Requirement(text="React", kind="required")]
    sections = ResumeSections(skills="Python, React, CSS")
    score, matches = keyword_score(reqs, sections)
    assert score == 100.0
    assert all(m.matched for m in matches)


def test_zero_score_when_no_required_skill_is_present():
    reqs = [Requirement(text="Rust", kind="required")]
    sections = ResumeSections(skills="Python, React")
    score, matches = keyword_score(reqs, sections)
    assert score == 0.0
    assert matches[0].matched is False


def test_short_requirement_does_not_false_positive_inside_a_longer_word():
    reqs = [Requirement(text="Go", kind="required")]
    sections = ResumeSections(skills="MongoDB, Google Cloud")
    score, matches = keyword_score(reqs, sections)
    assert score == 0.0
    assert matches[0].matched is False


def test_alias_counts_as_a_match():
    reqs = [Requirement(text="JavaScript", kind="required")]
    sections = ResumeSections(skills="JS, HTML, CSS")
    score, matches = keyword_score(reqs, sections)
    assert score == 100.0
    assert matches[0].matched is True


def test_symbol_bearing_skills_still_match_verbatim():
    reqs = [
        Requirement(text="C++", kind="required"),
        Requirement(text=".NET", kind="required"),
        Requirement(text="C#", kind="required"),
    ]
    sections = ResumeSections(skills="C++, .NET, C#")
    score, matches = keyword_score(reqs, sections)
    assert score == 100.0
    assert all(m.matched for m in matches)


def test_missing_preferred_skill_costs_less_than_missing_a_required_one():
    reqs = [Requirement(text="Python", kind="required"), Requirement(text="Docker", kind="preferred")]
    sections = ResumeSections(skills="Python")
    score, _ = keyword_score(reqs, sections)
    # weighted: required=1.0, preferred=0.4 -> 1.0 / 1.4 * 100
    assert round(score, 1) == round(100 * 1.0 / 1.4, 1)

