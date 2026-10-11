"""
Analysis Service Module.
Orchestrates the complete contract intelligence pipeline:
PDF Ingestion -> Cleaning & Segmentation -> NLP Extraction -> Classification -> Risk Engine.
"""

from pathlib import Path
from typing import Dict, List, Any, Union
import time

from src.document_processing.pdf_extractor import extract_text_from_pdf
from src.document_processing.text_cleaner import clean_text
from src.document_processing.clause_segmenter import segment_into_clauses
from src.nlp.feature_extractor import extract_linguistic_features
from src.nlp.information_extractor import extract_key_information
from src.nlp.ambiguity_detector import detect_ambiguity
from src.nlp.clause_classifier import ClauseClassifier
from src.risk_engine.risk_scorer import score_clause_risk
from src.utils.logging_utils import get_logger

logger = get_logger("analysis_service")

class ContractAnalysisService:
    def __init__(self, default_model: str = "baseline"):
        self.default_model = default_model
        logger.info(f"Initializing ContractAnalysisService with model '{default_model}'...")
        self.classifier = ClauseClassifier(model_type=default_model)

    def analyze_contract_pdf(
        self, 
        pdf_input: Union[str, Path, bytes], 
        filename: str = "contract.pdf"
    ) -> Dict[str, Any]:
        """
        Executes end-to-end analysis on an uploaded PDF contract.
        """
        start_time = time.time()
        logger.info(f"Beginning analysis of {filename}...")

        # 1. Document Extraction
        pages = extract_text_from_pdf(pdf_input)
        
        # 2. Text Cleaning per page
        for p in pages:
            p["text"] = clean_text(p["text"])

        # 3. Clause Segmentation
        raw_clauses = segment_into_clauses(pages)
        logger.info(f"Segmented {len(raw_clauses)} candidate clauses across {len(pages)} pages.")

        # 4. Pipeline Execution per clause
        analyzed_clauses = []
        for cl in raw_clauses:
            text = cl["text"]
            
            # Linguistic & Information extraction
            ling_feats = extract_linguistic_features(text)
            info_feats = extract_key_information(text)
            ambig_feats = detect_ambiguity(text)

            # Classification
            pred_res = self.classifier.predict_clause(text)

            # Risk scoring & explanation
            scored_clause = score_clause_risk(
                clause_id=cl["clause_id"],
                clause_text=text,
                page_number=cl["page_number"],
                classification_result=pred_res,
                linguistic_feats=ling_feats,
                info_feats=info_feats,
                ambiguity_feats=ambig_feats
            )
            analyzed_clauses.append(scored_clause)

        total_duration = time.time() - start_time

        # 5. Executive Contract Summary
        high_risk_count = sum(1 for c in analyzed_clauses if c["risk_level"] == "High Risk")
        needs_review_count = sum(1 for c in analyzed_clauses if c["risk_level"] == "Needs Review")
        info_count = sum(1 for c in analyzed_clauses if c["risk_level"] == "Informational")

        overall_contract_risk = "HIGH RISK" if high_risk_count > 0 else ("MODERATE RISK" if needs_review_count > 0 else "LOW RISK")

        return {
            "filename": filename,
            "total_pages": len(pages),
            "total_clauses": len(analyzed_clauses),
            "overall_contract_risk": overall_contract_risk,
            "risk_counts": {
                "high_risk": high_risk_count,
                "needs_review": needs_review_count,
                "informational": info_count
            },
            "analysis_time_seconds": round(total_duration, 2),
            "model_used": self.default_model,
            "clauses": analyzed_clauses
        }
