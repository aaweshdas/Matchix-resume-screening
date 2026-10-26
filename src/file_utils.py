"""
Extract plain text from uploaded resume files (PDF, DOCX, TXT).

Gracefully degrades: if pdfplumber / python-docx aren't installed, the
relevant file types are reported as unsupported rather than crashing.
"""
from __future__ import annotations

import io


def extract_text_from_upload(file_name: str, file_bytes: bytes) -> str:
    """Return extracted text from an uploaded file's bytes based on extension."""
    name = (file_name or "").lower()

    if name.endswith(".txt"):
        for enc in ("utf-8", "latin-1"):
            try:
                return file_bytes.decode(enc)
            except UnicodeDecodeError:
                continue
        return file_bytes.decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        return _extract_pdf(file_bytes)

    if name.endswith(".docx"):
        return _extract_docx(file_bytes)

    # Unknown -> best-effort decode
    return file_bytes.decode("utf-8", errors="ignore")


def _extract_pdf(file_bytes: bytes) -> str:
    try:
        import pdfplumber
    except Exception:
        return "[Could not read PDF: install `pdfplumber` (pip install pdfplumber).]"
    text_parts = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
    except Exception as exc:
        return f"[Could not read PDF: {exc}]"
    return "\n".join(text_parts)


def _extract_docx(file_bytes: bytes) -> str:
    try:
        import docx  # python-docx
    except Exception:
        return "[Could not read DOCX: install `python-docx` (pip install python-docx).]"
    try:
        document = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in document.paragraphs)
    except Exception as exc:
        return f"[Could not read DOCX: {exc}]"
