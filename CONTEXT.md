# Smart Shortlisting Engine

Ranks a batch of resumes against a single Job Description using both keyword and semantic matching, producing a full ranked list with scores and an explanation for the top 3.

## Language

**Good Ranking**:
A ranking where a recruiter skimming the top 5 would agree they're plausible strong fits, and no candidate missing an explicit required skill outranks one who has it, absent a strong compensating signal.
_Avoid_: "accurate ranking", "correct order" — implies a single ground-truth ordering this project has no labels to verify against.

**Required Skill**:
A skill listed in the JD with no "preferred/nice-to-have/bonus" marker; treated as mandatory — a candidate missing it should not be able to reach the top of the ranking on other strengths alone.

**Preferred Skill**:
A skill the JD explicitly marks as preferred, nice-to-have, or bonus; desirable but its absence must not penalize a candidate the way a missing Required Skill does.

**Keyword Match**:
Evidence that a specific skill/tool/term from the JD appears explicitly (allowing normalization and known aliases) in a resume.
_Avoid_: "exact match" — normalization and aliasing mean it's not always literal string equality.

**Semantic Match**:
Evidence that a resume demonstrates a JD requirement through meaning/context rather than the literal term appearing (e.g. "Express + MongoDB" experience as evidence of "Node.js backend" ability). Degrades with distance from the JD's ecosystem, not binary.

**JD Requirement**:
A single skill/technology/qualification line extracted from the JD, classified as Required or Preferred. The unit that Keyword Match and Semantic Match are each evaluated against.

**Resume Section**:
One of the three chunks a resume is split into for comparison: Skills, Experience+Projects, or Education. The unit of semantic comparison against a JD Requirement. If header detection fails for a resume, its entire body falls back to one unclassified Section rather than being dropped or crashing the pipeline.
_Avoid_: "resume chunk" — Section is the stable name for this entity going forward.

**Keyword Score**:
A candidate's 0-100 measure of how much of the JD's weighted requirements are satisfied via Keyword Match.

**Semantic Score**:
A candidate's 0-100 measure of meaning-based similarity to the JD's requirements via Semantic Match, rescaled so scores spread meaningfully rather than clustering.

**Final Score**:
The published per-candidate score: combines Keyword Score and Semantic Score, then applies a steep penalty for each missing Required Skill — so no candidate missing a Required Skill can outrank one who has it purely on semantic strength. The score that determines the ranking.

**Evidence**:
The deterministic, per-candidate record of matched JD Requirements (tagged Keyword or Semantic) and missing Required Skills. Computed with zero LLM involvement; the only input an Explanation is allowed to draw from.

**Explanation**:
Natural-language prose, generated only from a candidate's Evidence, provided for the top 3 ranked candidates.
_Avoid_: any explanation text sourced from raw resume/JD text directly — that would break the traceability judges will test for.
