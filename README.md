# Smart Shortlisting Engine

Built for the **InternLoom AI Hackathon** (Manipal Institute of Technology) — *"Rank Resumes Against a Job Description."*

Given one Job Description and a batch of resumes, this system produces a full ranked list of candidates with a score for each, and a grounded explanation for the top 3 — using both **keyword matching** and **semantic matching**, genuinely combined, not an LLM asked to "score this out of 100."

## Status

| Piece | State |
|---|---|
| Parsing (JD → requirements, resume → sections) | ✅ Done, unit-tested |
| Keyword matching (PDF + DOCX resumes) | ✅ Done, unit-tested |
| Semantic matching | ✅ Done (local embedding model), rescale calibrated against real data |
| Scoring / ranking | ✅ Done, unit-tested |
| Top-3 explanations | ✅ Done, unit-tested |
| UI | ✅ Upload-only (PDF/DOCX), no local-file dependency — see `app.py` |
| Run against real hackathon data | ✅ Tested against an 18-resume batch (see [`sample_data/`](./sample_data)) |
| Deployment | Not yet deployed — see [Deployment](#deployment) |
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

The `0.55^missing_required_count` term is the key design decision: a candidate missing even one Required Skill gets multiplicatively penalized, so no amount of semantic similarity can let them outrank a candidate who actually has the required stack. **Verified on the real 18-resume batch**: a candidate with a lower keyword score but zero missing Required Skills (39.9 final) outranked one with a much higher keyword score but one missing Required Skill (36.2 final) — the gating behaves as designed, not just in the unit test.

The semantic rescale range (`RAW_SIMILARITY_FLOOR`/`CEILING` in `src/semantic_engine.py`) was recalibrated from the real batch's observed cosine-similarity distribution (roughly p5=0.0 to p95=0.25, not the initial guess of 0.15-0.75) — without this, semantic scores were compressed near zero for almost every candidate. Constants remain tunable (see `src/scoring.py`, `src/weights.py`, `src/semantic_engine.py`) if you swap in different data.

### Evaluation approach

No ground-truth labels exist for this problem, so correctness is checked by:
1. Manual spot-check against 2-3 resumes with an obvious expected outcome (clearly strong / clearly weak / borderline).
2. A keyword-only vs. semantic-only vs. combined ranking comparison (shown in the UI) — proving both signals actually move the ranking, not just one doing all the work.

## Architecture & design decisions

- **No database** — single-batch, single-run pipeline; everything held in memory, nothing needs to persist between runs.
- **Upload-only, no local file dependency** — the app never reads from disk paths; JD and resumes are supplied through the browser (PDF or DOCX), so it works for any user on any machine, not just this laptop.
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

The app is upload-only — no local file paths. Open it, upload a JD and one or more resumes (PDF or DOCX) through the browser, and click **Run Ranking**.

For a quick demo without hunting for files, [`sample_data/`](./sample_data) in this repo has a ready-to-upload JD + 18-resume batch (see [`sample_data/SOURCE.md`](./sample_data/SOURCE.md) for where it came from).

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
  pdf_extract.py      # PDF -> text
  docx_extract.py     # DOCX -> text
  document_extract.py # dispatches to the right extractor by file extension
app.py                 # Streamlit UI (upload-only)
tests/                 # 25 tests covering every module above except the UI/document adapters
sample_data/           # ready-to-upload JD + 18 resumes for a live demo (see SOURCE.md)
```

## Deployment

Not yet deployed. The app is a standard Streamlit app, so it's deployable to [Streamlit Community Cloud](https://streamlit.io/cloud) in a few minutes: push this repo to GitHub (done), go to share.streamlit.io, sign in with GitHub, point it at this repo/branch/`app.py`, and deploy. One thing to watch: the free tier's memory limit can be tight with `torch` + `sentence-transformers` loaded — if the deploy fails on memory, the fallback is swapping to a smaller/quantized embedding model or a lighter host.

## What's deliberately out of scope

Per the hackathon's own guidance ("a complete, working core solution will always score higher than an incomplete one with extras"), these bonus features were not attempted, in favor of a clean, defensible core:

- Bias/narrow-phrasing flagging on the JD
- Recruiter chat Q&A layer ("Why is X ranked above Y?")
- Robustness beyond the built-in catch-all fallback for messy resume formatting
