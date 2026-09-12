from __future__ import annotations

import docx


def extract_text(path_or_file) -> str:
    document = docx.Document(path_or_file)
    return "\n".join(p.text for p in document.paragraphs)
