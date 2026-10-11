"""
Document Text Extraction Module.
Uses PyMuPDF (fitz) with safe fallback to extract text page-by-page.
"""

from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_source: str | Path | bytes) -> List[Dict[str, Any]]:
    """
    Extracts text from PDF page by page with page numbering.
    Accepts filepath, Path object, or raw PDF bytes (from file uploader).
    """
    if isinstance(pdf_source, (str, Path)):
        doc = fitz.open(str(pdf_source))
    elif isinstance(pdf_source, bytes):
        doc = fitz.open(stream=pdf_source, filetype="pdf")
    else:
        raise ValueError("Unsupported pdf_source type. Expected str, Path, or bytes.")

    pages = []
    for page_idx, page in enumerate(doc):
        text = page.get_text("text")
        pages.append({
            "page_number": page_idx + 1,
            "text": text
        })
    doc.close()
    return pages
