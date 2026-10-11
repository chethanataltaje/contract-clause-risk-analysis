"""
Information Extractor Module.
Extracts monetary penalty amounts, deadlines, notice periods, and timeframes.
"""

import re
from typing import Dict, List, Any

# Regex patterns for financial figures & notice durations
CURRENCY_PATTERN = re.compile(r"(\$\s?[0-9]+(?:,[0-9]{3})*(?:\.[0-9]{2})?|\b[0-9]+(?:\.[0-9]+)?\s?(?:USD|EUR|GBP|INR)\b)", re.IGNORECASE)
PERCENTAGE_PATTERN = re.compile(r"\b([0-9]+(?:\.[0-9]+)?\s?%|[0-9]+\s?percent)\b", re.IGNORECASE)
NOTICE_PERIOD_PATTERN = re.compile(r"\b([0-9]{1,3}\s?(?:calendar|business)?\s?(?:days?|weeks?|months?))\b", re.IGNORECASE)

def extract_key_information(clause_text: str) -> Dict[str, Any]:
    """
    Extracts structured entities from clause text.
    """
    currencies = CURRENCY_PATTERN.findall(clause_text)
    percentages = PERCENTAGE_PATTERN.findall(clause_text)
    notice_periods = NOTICE_PERIOD_PATTERN.findall(clause_text)

    return {
        "extracted_amounts": list(set(currencies + percentages)),
        "extracted_deadlines": list(set(notice_periods)),
        "has_financial_entity": len(currencies + percentages) > 0,
        "has_deadline_entity": len(notice_periods) > 0
    }
