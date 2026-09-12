from __future__ import annotations

import pdfplumber


def extract_text(path_or_file) -> str:
    with pdfplumber.open(path_or_file) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)
