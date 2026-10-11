"""
Unit tests for End-to-End Pipeline Service (tests/test_end_to_end.py).
Tests entire flow: PDF file/stream -> segmentation -> NLP -> risk scoring -> report.
"""

import pytest
from pathlib import Path
from src.utils.config import SAMPLE_CONTRACTS_DIR
from src.services.analysis_service import ContractAnalysisService
from src.services.report_service import generate_markdown_report

def test_full_pipeline_on_sample_nda():
    pdf_path = SAMPLE_CONTRACTS_DIR / "sample_nda.pdf"
    assert pdf_path.exists(), "sample_nda.pdf must exist"

    service = ContractAnalysisService(default_model="baseline")
    result = service.analyze_contract_pdf(pdf_path, filename="sample_nda.pdf")

    assert result["filename"] == "sample_nda.pdf"
    assert result["total_clauses"] >= 3
    assert result["total_pages"] >= 1
    assert "risk_counts" in result
    assert result["overall_contract_risk"] in ["HIGH RISK", "MODERATE RISK", "LOW RISK"]

    # Verify at least one confidentiality clause was recognized
    categories = [c["predicted_category"] for c in result["clauses"]]
    assert "Confidentiality" in categories

    # Verify report generation
    report_md = generate_markdown_report(result)
    assert "# 🛡️ Contract Intelligence & Risk Audit Report" in report_md
    assert "sample_nda.pdf" in report_md

def test_full_pipeline_on_sample_msa_with_sbert():
    pdf_path = SAMPLE_CONTRACTS_DIR / "sample_msa.pdf"
    assert pdf_path.exists(), "sample_msa.pdf must exist"

    service = ContractAnalysisService(default_model="sbert")
    result = service.analyze_contract_pdf(pdf_path, filename="sample_msa.pdf")

    assert result["total_clauses"] >= 4
    assert result["model_used"] == "sbert"

    # In MSA, limitation of liability with $100,000 should extract financial figure
    all_amounts = []
    for c in result["clauses"]:
        all_amounts.extend(c["extracted_entities"]["amounts"])
    
    assert any("$100,000" in amt for amt in all_amounts)
