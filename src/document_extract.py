from __future__ import annotations

from src.docx_extract import extract_text as extract_docx_text
from src.pdf_extract import extract_text as extract_pdf_text

SUPPORTED_EXTENSIONS = (".pdf", ".docx")


def extract_text(path_or_file, filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_pdf_text(path_or_file)
    if lower.endswith(".docx"):
        return extract_docx_text(path_or_file)
    raise ValueError(f"Unsupported file type: {filename}")
