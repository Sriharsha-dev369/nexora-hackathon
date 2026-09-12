from src.parsing import Requirement
from src.keyword_engine import KeywordMatch
from src.semantic_engine import SemanticMatch
from src.evidence import build_evidence


def test_a_required_skill_matched_by_keyword_only_is_tagged_keyword():
    req = Requirement(text="Python", kind="required")
    kw = [KeywordMatch(requirement=req, matched=True)]
    sm = [SemanticMatch(requirement=req, similarity=10.0, matched=False)]
    evidence = build_evidence(kw, sm)
    assert evidence.matched[0].requirement == req
    assert evidence.matched[0].match_type == "keyword"
    assert evidence.missing_required == []


def test_a_required_skill_matched_by_neither_is_missing():
    req = Requirement(text="Rust", kind="required")
    kw = [KeywordMatch(requirement=req, matched=False)]
    sm = [SemanticMatch(requirement=req, similarity=5.0, matched=False)]
    evidence = build_evidence(kw, sm)
    assert evidence.matched == []
    assert evidence.missing_required == [req]


def test_an_unmatched_preferred_skill_is_neither_matched_nor_missing():
    req = Requirement(text="Docker", kind="preferred")
    kw = [KeywordMatch(requirement=req, matched=False)]
    sm = [SemanticMatch(requirement=req, similarity=5.0, matched=False)]
    evidence = build_evidence(kw, sm)
    assert evidence.matched == []
    assert evidence.missing_required == []


def test_matched_by_both_signals_is_tagged_both():
    req = Requirement(text="React", kind="required")
    kw = [KeywordMatch(requirement=req, matched=True)]
    sm = [SemanticMatch(requirement=req, similarity=80.0, matched=True)]
    evidence = build_evidence(kw, sm)
    assert evidence.matched[0].match_type == "both"
