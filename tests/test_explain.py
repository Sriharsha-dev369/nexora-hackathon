from src.parsing import Requirement
from src.evidence import Evidence, MatchedRequirement
from src.explain import explain


def test_explanation_lists_matched_and_missing_skills():
    evidence = Evidence(
        matched=[
            MatchedRequirement(requirement=Requirement(text="Python", kind="required"), match_type="keyword"),
            MatchedRequirement(requirement=Requirement(text="React", kind="required"), match_type="semantic"),
        ],
        missing_required=[Requirement(text="Docker", kind="required")],
    )
    text = explain(evidence)
    assert "Python" in text
    assert "React" in text
    assert "Docker" in text


def test_explanation_does_not_claim_missing_skills_when_none_are_missing():
    evidence = Evidence(
        matched=[MatchedRequirement(requirement=Requirement(text="Python", kind="required"), match_type="keyword")],
        missing_required=[],
    )
    text = explain(evidence)
    assert "No required skills appear to be missing" in text
