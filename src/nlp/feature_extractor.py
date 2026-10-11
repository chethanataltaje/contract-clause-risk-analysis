"""
Feature Extractor Module (Unit 1 & Unit 2).
Extracts modal verbs (obligation vs. permission), conditionals, negations, amounts, and dates.
"""

import re
from typing import Dict, List, Any
from src.utils.config import (
    MODAL_OBLIGATIONS,
    MODAL_PERMISSIONS,
    CONDITIONALS,
    NEGATION_TERMS
)

def extract_linguistic_features(clause_text: str) -> Dict[str, Any]:
    """
    Identifies syllabus-mandated linguistic patterns in a clause text.
    """
    text_lower = clause_text.lower()

    # Obligation vs Permission
    found_obligations = [m for m in MODAL_OBLIGATIONS if re.search(rf"\b{m}\b", text_lower)]
    found_permissions = [m for m in MODAL_PERMISSIONS if re.search(rf"\b{m}\b", text_lower)]

    # Conditionals
    found_conditionals = [c for c in CONDITIONALS if re.search(rf"\b{c}\b", text_lower)]

    # Negations & Limitations
    found_negations = [n for n in NEGATION_TERMS if re.search(rf"\b{n}\b", text_lower)]

    return {
        "obligations": found_obligations,
        "permissions": found_permissions,
        "conditionals": found_conditionals,
        "negations": found_negations,
        "has_obligation": len(found_obligations) > 0,
        "has_permission": len(found_permissions) > 0,
        "has_conditional": len(found_conditionals) > 0,
        "has_negation": len(found_negations) > 0,
    }
