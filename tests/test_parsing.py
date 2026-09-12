from src.parsing import parse_jd, parse_resume, Requirement


def test_lines_under_a_requirements_header_are_required():
    text = """
Requirements:
- Node.js
- MongoDB
"""
    reqs = parse_jd(text)
    assert Requirement(text="Node.js", kind="required") in reqs
    assert Requirement(text="MongoDB", kind="required") in reqs


def test_lines_under_a_preferred_header_are_preferred():
    text = """
Nice to have:
- Docker
- GraphQL
"""
    reqs = parse_jd(text)
    assert Requirement(text="Docker", kind="preferred") in reqs
    assert Requirement(text="GraphQL", kind="preferred") in reqs


def test_switching_back_to_a_required_section_after_a_preferred_one():
    text = """
Preferred:
- Docker

Requirements:
- SQL
"""
    reqs = parse_jd(text)
    assert Requirement(text="Docker", kind="preferred") in reqs
    assert Requirement(text="SQL", kind="required") in reqs


def test_bullets_with_no_section_header_default_to_required():
    text = """
- Python
- React
"""
    reqs = parse_jd(text)
    assert Requirement(text="Python", kind="required") in reqs
    assert Requirement(text="React", kind="required") in reqs


def test_inline_marker_overrides_the_section_default():
    text = """
Requirements:
- Python
- Docker (nice to have)
"""
    reqs = parse_jd(text)
    assert Requirement(text="Python", kind="required") in reqs
    assert Requirement(text="Docker", kind="preferred") in reqs


def test_lines_are_grouped_under_their_section_header():
    text = """
Skills:
Python, React

Experience:
Built REST APIs with Express and MongoDB

Education:
BS Computer Science
"""
    sections = parse_resume(text)
    assert "Python, React" in sections.skills
    assert "Express and MongoDB" in sections.experience
    assert "BS Computer Science" in sections.education
    assert sections.unclassified == ""


def test_resume_with_no_recognizable_headers_falls_back_to_unclassified():
    text = "Just a wall of text with no section headers of any kind at all."
    sections = parse_resume(text)
    assert sections.skills == ""
    assert sections.experience == ""
    assert sections.education == ""
    assert "wall of text" in sections.unclassified


def test_content_under_an_unrecognized_header_falls_back_to_unclassified_instead_of_vanishing():
    text = """
Core Competencies:
Python, Java, AWS

Experience:
Built services in Python
"""
    sections = parse_resume(text)
    assert "Python, Java, AWS" in sections.unclassified
    assert "Built services in Python" in sections.experience


def test_prose_sentence_containing_a_marker_word_does_not_switch_the_current_section():
    text = """
Requirements:
- Python
- Java

This role has some nice to have extras but the core stack is mandatory for delivery.
- Docker
- Kubernetes
"""
    reqs = parse_jd(text)
    assert Requirement(text="Docker", kind="required") in reqs
    assert Requirement(text="Kubernetes", kind="required") in reqs


def test_a_bullet_that_is_only_a_marker_produces_no_requirement():
    text = """
Requirements:
- Python
- (Preferred)
"""
    reqs = parse_jd(text)
    assert all(r.text for r in reqs)
    assert len(reqs) == 1
