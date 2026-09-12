# Smart Shortlisting Engine

Built for the **InternLoom AI Hackathon** (Manipal Institute of Technology) — *"Rank Resumes Against a Job Description."*

Given one Job Description and a batch of resumes, this system produces a full ranked list of candidates with a score for each, and a grounded explanation for the top 3 — using both **keyword matching** and **semantic matching**, genuinely combined, not an LLM asked to "score this out of 100."

## Status

| Piece | State |
|---|---|
| Parsing (JD → requirements, resume → sections) | ✅ Done, unit-tested |
| Keyword matching | ✅ Done, unit-tested |
| Semantic matching | ✅ Done (local embedding model) |
| Scoring / ranking | ✅ Done, unit-tested |
| Top-3 explanations | ✅ Done, unit-tested |
| Streamlit UI | ✅ Built, boots cleanly |
| Run against real hackathon data | ⏳ Pending — drop files into `data/` (see below) |
| Deployment | Not deployed — runs locally by design (see [Architecture](#architecture--design-decisions)) |
| Bonus features | Not attempted — core-first per hackathon guidance for solo builders |

25/25 tests passing. Run `pytest` to verify.

## Why keyword + semantic, genuinely combined

A resume that says *"built REST APIs with Express and MongoDB"* is clearly relevant to a *"Node.js backend"* requirement, even with zero literal word overlap — that's what semantic matching catches. But a JD that explicitly asks for a specific technology shouldn't be satisfiable by only vaguely-related experience — that's what keyword matching enforces. Neither alone is enough:

- **Keyword-only** misses paraphrased experience (different wording, same skill).
- **Semantic-only** lets broad similarity mask a genuinely missing required skill.
- **A single LLM score** is an opaque number with no inspectable evidence — can't be walked through or defended to a judge.

This system computes both signals independently and combines them with an explicit, inspectable formula (below), so every ranking decision can be traced to specific evidence.

## How it works

```
JD.pdf ──┐
         ├─► Parser ──► Requirements[] (Required / Preferred, extracted from JD text)
Resumes ─┘         ──► Sections{Skills, Experience+Projects, Education}
                          (falls back to one unclassified section if headers
                           aren't detected — never silently drops content)
                │
                ▼
     Keyword Engine ──► Keyword Score   (normalized, aliased, word-boundary-safe matching)
     Semantic Engine ──► Semantic Score  (sentence-embedding cosine similarity)
                │
                ▼
     Scoring: penalty-gated combination ──► Final Score, full ranking
                │
                ▼
     Evidence (deterministic, per top-3 candidate: matched reqs + missing required skills)
                │
                ▼
     Explanation (template text generated only from Evidence — never free-floating)
                │
                ▼
     Streamlit UI: ranked table + top-3 explanations + signal-comparison view
```

### Scoring formula

```
keyword_score  = 100 · Σ(weight_i · matched_i) / Σ(weight_i)       weight = 1.0 Required, 0.4 Preferred
semantic_score = rescaled average cosine similarity, same weighting
final_score    = (0.5 · keyword_score + 0.5 · semantic_score) × 0.55 ^ (missing_required_count)
```

The `0.55^missing_required_count` term is the key design decision: a candidate missing even one Required Skill gets multiplicatively penalized, so no amount of semantic similarity can let them outrank a candidate who actually has the required stack. Constants are starting points — expected to be tuned by eye once run against the real resume batch (see `src/scoring.py`, `src/weights.py`, `src/semantic_engine.py`).

### Evaluation approach

No ground-truth labels exist for this problem, so correctness is checked by:
1. Manual spot-check against 2-3 resumes with an obvious expected outcome (clearly strong / clearly weak / borderline).
2. A keyword-only vs. semantic-only vs. combined ranking comparison (shown in the UI) — proving both signals actually move the ranking, not just one doing all the work.

## Architecture & design decisions

- **No database** — single-batch, single-run pipeline; everything held in memory, nothing needs to persist between runs.
- **No deployment** — runs locally for live demo/judging. Zero deployment risk in a hackathon time budget. (Trivially deployable to Streamlit Community Cloud later if a public link is ever needed.)
- **Local embedding model** (`sentence-transformers/all-MiniLM-L6-v2`) — no API key, no network dependency, no latency risk during judging.
- **Template-based explanations**, not an LLM call — deterministic, always traceable to the Evidence object, and can't fail mid-demo on an API hiccup.

Full domain vocabulary (Required Skill, Keyword Match, Semantic Match, Evidence, etc.) is documented in [`CONTEXT.md`](./CONTEXT.md).

## Running it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# run tests
.venv/bin/pytest

# run the app
.venv/bin/streamlit run app.py
```

### Providing data

The app auto-loads from a `data/` folder if present (gitignored — not committed):

```
data/
├── jd.pdf
└── resumes/
    ├── candidate1.pdf
    ├── candidate2.pdf
    └── ...
```

Without a `data/` folder, the app falls back to file-upload widgets for the JD and resumes.

## Project layout

```
src/
  parsing.py          # JD text -> Requirements, resume text -> Sections
  keyword_engine.py   # Keyword Score
  semantic_engine.py  # Semantic Score (embedding model)
  weights.py          # shared Required/Preferred weighting
  scoring.py          # penalty-gated Final Score
  evidence.py         # deterministic per-candidate match evidence
  explain.py          # Evidence -> natural-language explanation
  pipeline.py         # orchestrates the full ranking run
  pdf_extract.py       # PDF -> text
app.py                 # Streamlit UI
tests/                 # 25 tests covering every module above except the UI/PDF adapters
```

## What's deliberately out of scope

Per the hackathon's own guidance ("a complete, working core solution will always score higher than an incomplete one with extras"), these bonus features were not attempted, in favor of a clean, defensible core:

- Bias/narrow-phrasing flagging on the JD
- Recruiter chat Q&A layer ("Why is X ranked above Y?")
- Robustness beyond the built-in catch-all fallback for messy resume formatting
