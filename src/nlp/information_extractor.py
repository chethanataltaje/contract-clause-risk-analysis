"""
Information Extractor Module.
Extracts structured legal entities:
- Monetary caps & penalty figures ($, %, currency words)
- Temporal notice periods & deadlines (e.g., '30 days', '12 months')
- Named contracting parties and entities
"""

import re
from typing import Dict, List, Any

# Currencies & percentages
CURRENCY_PATTERN = re.compile(
    r"(?:\$\s?[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?|\b[0-9]+(?:\.[0-9]+)?\s?(?:USD|EUR|GBP|INR|dollars)\b)",
    re.IGNORECASE
)
PERCENTAGE_PATTERN = re.compile(
    r"\b[0-9]+(?:\.[0-9]+)?\s?(?:%|percent)\b",
    re.IGNORECASE
)

# Durations & Notice Deadlines (e.g. '30 days', 'sixty (60) days', '2 years')
DEADLINE_PATTERN = re.compile(
    r"\b(?:(?:within|upon|prior to)\s+)?(?:[0-9]{1,3}|\b(?:one|two|three|five|ten|fifteen|twenty|thirty|sixty|ninety|one hundred eighty)\b)\s*(?:\([0-9]{1,3}\)\s*)?(?:business\s+|calendar\s+)?(?:days?|weeks?|months?|years?)\b",
    re.IGNORECASE
)

# Common contract party roles
PARTY_ROLES = [
    r"\b(?:Licensor|Licensee)\b",
    r"\b(?:Provider|Client|Customer)\b",
    r"\b(?:Employer|Employee)\b",
    r"\b(?:Landlord|Tenant)\b",
    r"\b(?:Disclosing Party|Recipient|Receiving Party)\b",
    r"\b(?:Vendor|Purchaser|Supplier)\b",
    r"\b(?:Company|Consultant|Contractor)\b"
]

def extract_key_information(clause_text: str) -> Dict[str, Any]:
    """
    Extracts monetary amounts, deadline/notice timeframes, and referenced parties.
    """
    currencies = CURRENCY_PATTERN.findall(clause_text)
    percentages = PERCENTAGE_PATTERN.findall(clause_text)
    deadlines = DEADLINE_PATTERN.findall(clause_text)

    # Clean & normalize entities
    cleaned_amounts = list(dict.fromkeys([c.strip() for c in (currencies + percentages)]))
    cleaned_deadlines = list(dict.fromkeys([d.strip() for d in deadlines]))

    # Identify involved party roles
    detected_parties = []
    for role_pat in PARTY_ROLES:
        matches = re.findall(role_pat, clause_text, re.IGNORECASE)
        if matches:
            detected_parties.extend(matches)
    detected_parties = list(dict.fromkeys([p.capitalize() for p in detected_parties]))

    return {
        "extracted_amounts": cleaned_amounts,
        "extracted_deadlines": cleaned_deadlines,
        "extracted_parties": detected_parties,
        "has_financial_entity": len(cleaned_amounts) > 0,
        "has_deadline_entity": len(cleaned_deadlines) > 0,
        "has_party_reference": len(detected_parties) > 0
    }
