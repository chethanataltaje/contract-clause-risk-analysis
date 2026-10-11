"""
Ambiguity & Vague Legal Terminology Detector Module.
Identifies subjective, imprecise, or overly broad legal phrasing that requires human review.
"""

import re
from typing import Dict, List, Any
from src.utils.config import AMBIGUITY_TERMS

# Context-specific legal vagueness patterns
AMBIGUOUS_PATTERNS = [
    (r"\breasonable(?:\s+efforts|\s+commercial\s+efforts|\s+manner|\s+time)?\b", "Reasonableness standard (subjective)"),
    (r"\bpromptly\b", "Vague temporal requirement ('promptly' lacks defined duration)"),
    (r"\bbest\s+efforts\b", "High-burden standard ('best efforts' creates disproportionate exposure)"),
    (r"\bmaterial(?:ly)?(?:\s+adverse|\s+breach)?\b", "Undefined materiality threshold"),
    (r"\bsubstantial(?:ly)?\b", "Imprecise qualification ('substantially')"),
    (r"\bfrom\s+time\s+to\s+time\b", "Unbounded unilateral modification or activity"),
    (r"\bat\s+(?:its|their)\s+(?:sole\s+)?discretion\b", "Unilateral discretionary power")
]

def detect_ambiguity(clause_text: str) -> Dict[str, Any]:
    """
    Scans a clause for ambiguous or imprecise legal standards.
    Returns detected terms, count, and descriptive flags.
    """
    text_lower = clause_text.lower()
    detected = []

    for pattern, description in AMBIGUOUS_PATTERNS:
        matches = re.findall(pattern, text_lower)
        if matches:
            detected.append({
                "term": matches[0].strip(),
                "description": description
            })

    # Also check base terms from config
    for term in AMBIGUITY_TERMS:
        if re.search(rf"\b{term}\b", text_lower) and not any(d["term"] == term for d in detected):
            detected.append({
                "term": term,
                "description": f"Vague qualifier '{term}'"
            })

    return {
        "ambiguous_terms": detected,
        "ambiguity_count": len(detected),
        "is_ambiguous": len(detected) > 0
    }
