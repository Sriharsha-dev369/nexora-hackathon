from pathlib import Path

import streamlit as st

from src.pdf_extract import extract_text
from src.pipeline import rank_candidates

st.set_page_config(page_title="Smart Shortlisting Engine", layout="wide")
st.title("Smart Shortlisting Engine")

DATA_DIR = Path(__file__).parent / "data"
JD_PATH = DATA_DIR / "jd.pdf"
RESUMES_DIR = DATA_DIR / "resumes"


def load_preloaded():
    jd_text = extract_text(str(JD_PATH))
    resumes = {
        p.stem: extract_text(str(p)) for p in sorted(RESUMES_DIR.glob("*.pdf"))
    }
    return jd_text, resumes


def load_uploaded():
    jd_file = st.file_uploader("Job Description (PDF)", type="pdf")
    resume_files = st.file_uploader("Resumes (PDF)", type="pdf", accept_multiple_files=True)
    if not jd_file or not resume_files:
        return None, None
    jd_text = extract_text(jd_file)
    resumes = {f.name: extract_text(f) for f in resume_files}
    return jd_text, resumes


if JD_PATH.exists() and RESUMES_DIR.exists():
    jd_text, resumes = load_preloaded()
    st.caption(f"Loaded JD + {len(resumes)} resumes from data/")
else:
    jd_text, resumes = load_uploaded()

if jd_text and resumes:
    if st.button("Run Ranking", type="primary"):
        with st.spinner("Scoring candidates..."):
            results = rank_candidates(jd_text, resumes)
        st.session_state["results"] = results

if "results" in st.session_state:
    results = st.session_state["results"]

    st.subheader("Ranked candidates")
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
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Top 3 explanations")
    for i, r in enumerate(results[:3]):
        with st.expander(f"#{i + 1} {r.name} — {round(r.final_score, 1)}"):
            st.write(r.explanation)

    with st.expander("Signal comparison (keyword-only vs semantic-only vs combined)"):
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
