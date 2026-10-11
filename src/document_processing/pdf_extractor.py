"""
PDF Text Extraction Module.
Uses PyMuPDF (fitz) to extract text and retain page metadata.
"""

from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extracts text from PDF page by page with page numbering.
    Returns: List of dicts with 'page_number' and 'text'.
    """
    doc = fitz.open(pdf_path)
    pages = []
    for page_idx, page in enumerate(doc):
        text = page.get_text("text")
        pages.append({
            "page_number": page_idx + 1,
            "text": text
        })
    doc.close()
    return pages
