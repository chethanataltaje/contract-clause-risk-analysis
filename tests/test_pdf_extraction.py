"""
Unit tests for Document Ingestion and Preprocessing.
Tests PDF extraction (file, bytes, error handling), text normalization, and clause segmentation.
"""

import pytest
from pathlib import Path
from src.utils.config import SAMPLE_CONTRACTS_DIR
from src.document_processing.pdf_extractor import extract_text_from_pdf
from src.document_processing.text_cleaner import clean_text
from src.document_processing.clause_segmenter import segment_into_clauses


def test_extract_text_from_pdf_path():
    sample_pdf = SAMPLE_CONTRACTS_DIR / "sample_nda.pdf"
    assert sample_pdf.exists(), "sample_nda.pdf not found in sample_contracts"

    pages = extract_text_from_pdf(sample_pdf)
    assert len(pages) > 0
    assert pages[0]["page_number"] == 1
    assert "CONFIDENTIALITY" in pages[0]["text"].upper() or "AGREEMENT" in pages[0]["text"].upper()


def test_extract_text_from_pdf_bytes():
    sample_pdf = SAMPLE_CONTRACTS_DIR / "sample_nda.pdf"
    with open(sample_pdf, "rb") as f:
        pdf_bytes = f.read()

    pages = extract_text_from_pdf(pdf_bytes)
    assert len(pages) > 0
    assert pages[0]["page_number"] == 1
    assert len(pages[0]["text"].strip()) > 0


def test_extract_text_invalid_type_raises():
    with pytest.raises(ValueError):
        extract_text_from_pdf(12345)


def test_clean_text_normalization():
    raw_dirty = "Party\xa0A \t\t agrees to   pay. \u201cSmart\u201d and \u2018fast\u2019. Con-\ntract."
    cleaned = clean_text(raw_dirty)
    assert "\xa0" not in cleaned
    assert "  " not in cleaned
    assert "\u201c" not in cleaned and "\u201d" not in cleaned
    assert "\u2018" not in cleaned and "\u2019" not in cleaned
    assert '"Smart"' in cleaned
    assert "'fast'" in cleaned
    assert "Contract." in cleaned


def test_segment_into_clauses():
    mock_pages = [
        {
            "page_number": 1,
            "text": (
                "1. CONFIDENTIALITY. Each party agrees to safeguard confidential data for three years.\n\n"
                "2. TERMINATION. Either party may terminate with thirty days written notice.\n\n"
                "Short line"
            )
        }
    ]

    clauses = segment_into_clauses(mock_pages)
    assert len(clauses) == 2
    assert clauses[0]["clause_id"] == "CL-001"
    assert clauses[0]["page_number"] == 1
    assert "CONFIDENTIALITY" in clauses[0]["text"]
    assert clauses[1]["clause_id"] == "CL-002"
    assert "TERMINATION" in clauses[1]["text"]
