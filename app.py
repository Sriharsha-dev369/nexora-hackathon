import statistics

import streamlit as st

from src.document_extract import extract_text

st.set_page_config(page_title="Smart Shortlisting Engine", page_icon="🎯", layout="wide")

st.markdown(
    """
    <style>
    .hero {
        padding: 1.75rem 2rem;
        border-radius: 14px;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        margin-bottom: 1.5rem;
    }
    .hero h1 { margin: 0 0 0.25rem 0; font-size: 1.9rem; }
    .hero p { margin: 0; opacity: 0.9; font-size: 1rem; }

    .candidate-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 1rem;
    }
    .candidate-rank {
        display: inline-block;
        background: #4f46e5;
        color: white;
        border-radius: 999px;
        width: 28px; height: 28px;
        text-align: center;
        line-height: 28px;
        font-weight: 700;
        margin-right: 0.5rem;
    }
    .pill {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.8rem;
        margin: 0.15rem 0.3rem 0.15rem 0;
        font-weight: 600;
    }
    .pill-matched { background: #dcfce7; color: #166534; }
    .pill-missing { background: #fee2e2; color: #991b1b; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🎯 Smart Shortlisting Engine</h1>
        <p>Upload a Job Description and a batch of resumes to get a ranked, explainable shortlist —
        combining genuine keyword and semantic matching, not a single opaque LLM score.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("1. Upload")
upload_col1, upload_col2 = st.columns(2)
with upload_col1:
    jd_file = st.file_uploader("Job Description", type=["pdf", "docx"], key="jd")
with upload_col2:
    resume_files = st.file_uploader(
        "Resumes (select multiple)", type=["pdf", "docx"], accept_multiple_files=True, key="resumes"
    )

ready = bool(jd_file and resume_files)
run = st.button("Run Ranking", type="primary", disabled=not ready, use_container_width=False)

if not ready:
    st.caption("Upload a JD and at least one resume to enable ranking.")

if run:
    from src.pipeline import rank_candidates

    progress = st.progress(0, text="Reading Job Description...")
    jd_text = extract_text(jd_file, jd_file.name)
    progress.progress(20, text="Reading resumes...")
    resumes = {f.name: extract_text(f, f.name) for f in resume_files}
    progress.progress(45, text="Scoring keyword + semantic matches...")
    results = rank_candidates(jd_text, resumes)
    progress.progress(100, text="Done")
    progress.empty()
    st.session_state["results"] = results

if "results" in st.session_state:
    results = st.session_state["results"]
    scores = [r.final_score for r in results]

    st.subheader("2. Results")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Candidates ranked", len(results))
    m2.metric("Top score", f"{scores[0]:.0f}")
    m3.metric("Median score", f"{statistics.median(scores):.0f}")
    m4.metric("Score spread", f"{scores[0] - scores[-1]:.0f}")

    st.dataframe(
        [
            {
                "Rank": i + 1,
                "Candidate": r.name,
                "Final Score": round(r.final_score, 1),
                "Keyword Score": round(r.keyword_score, 1),
                "Semantic Score": round(r.semantic_score, 1),
            }
            for i, r in enumerate(results)
        ],
        column_config={
            "Final Score": st.column_config.ProgressColumn(
                "Final Score", min_value=0, max_value=100, format="%.1f"
            ),
        },
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("3. Top 3 — why they ranked there")
    for i, r in enumerate(results[:3]):
        matched_html = "".join(
            f'<span class="pill pill-matched">✓ {m.requirement.text}</span>' for m in r.evidence.matched
        )
        missing_html = "".join(
            f'<span class="pill pill-missing">✗ {req.text}</span>' for req in r.evidence.missing_required
        )
        st.markdown(
            f"""
            <div class="candidate-card">
                <span class="candidate-rank">{i + 1}</span>
                <strong style="font-size:1.15rem">{r.name}</strong>
                <span style="float:right; font-weight:700; color:#4f46e5;">{r.final_score:.1f} / 100</span>
                <div style="margin-top:0.6rem;">{matched_html}{missing_html or ''}</div>
                <p style="margin-top:0.7rem; margin-bottom:0;">{r.explanation}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Signal comparison — keyword-only vs. semantic-only vs. combined"):
        st.caption(
            "Shows each candidate's rank under each signal alone, to demonstrate both signals "
            "genuinely move the ranking rather than one doing all the work."
        )
        keyword_rank = {
            r.name: rank
            for rank, r in enumerate(sorted(results, key=lambda x: x.keyword_score, reverse=True), start=1)
        }
        semantic_rank = {
            r.name: rank
            for rank, r in enumerate(sorted(results, key=lambda x: x.semantic_score, reverse=True), start=1)
        }
        st.dataframe(
            [
                {
                    "Candidate": r.name,
                    "Keyword-only rank": keyword_rank[r.name],
                    "Semantic-only rank": semantic_rank[r.name],
                    "Combined rank": i + 1,
                }
                for i, r in enumerate(results)
            ],
            use_container_width=True,
            hide_index=True,
        )

st.divider()
st.caption(
    "Smart Shortlisting Engine — built for the InternLoom AI Hackathon. "
    "Scores combine independently-computed keyword and semantic signals; a missing required skill "
    "is penalized so broad semantic similarity alone can never outrank a candidate who has it. "
    "[Source](https://github.com/Sriharsha-dev369/nexora-hackathon)"
)
