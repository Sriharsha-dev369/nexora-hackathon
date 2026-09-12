from src.scoring import final_score


def test_no_missing_required_skills_is_a_plain_average():
    assert final_score(keyword_score=100.0, semantic_score=100.0, missing_required_count=0) == 100.0


def test_each_missing_required_skill_applies_a_multiplicative_penalty():
    score = final_score(keyword_score=100.0, semantic_score=100.0, missing_required_count=1)
    assert round(score, 2) == 55.0


def test_candidate_with_no_missing_required_skills_beats_stronger_semantic_candidate_missing_one():
    # Candidate A: strong semantic similarity but missing one required skill.
    candidate_a = final_score(keyword_score=70.0, semantic_score=95.0, missing_required_count=1)
    # Candidate B: weaker semantic similarity but satisfies every required skill.
    candidate_b = final_score(keyword_score=100.0, semantic_score=60.0, missing_required_count=0)
    assert candidate_b > candidate_a
