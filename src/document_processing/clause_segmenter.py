"""
Clause Segmentation Module.
Splits contract document text into candidate clauses with unique Clause IDs.
Handles legal numbered headers (e.g. '1. ', 'SECTION 2.', 'Article III.') as well as paragraph breaks.
"""

import re
from typing import List, Dict, Any

# Section splitter pattern for legal documents
SECTION_PATTERN = re.compile(
    r"(?=(?:^|\n)\s*(?:SECTION\s+[0-9IVXLCDM]+|ARTICLE\s+[0-9IVXLCDM]+|[0-9]{1,2}(?:\.[0-9]{1,2})*\.?\s+[A-Za-z]))",
    re.IGNORECASE
)

def segment_into_clauses(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Splits text across pages into numbered clauses using legal section headers
    or paragraph markers.
    """
    clauses = []
    clause_counter = 1

    for page_dict in pages:
        page_num = page_dict["page_number"]
        page_text = page_dict["text"].strip()

        if not page_text:
            continue

        # Split on section headings or numbered markers
        raw_parts = [p.strip() for p in SECTION_PATTERN.split(page_text) if p.strip()]
        
        # If no section headings found or only single block, split on double linebreaks
        if len(raw_parts) <= 1:
            raw_parts = [p.strip() for p in re.split(r"\n\s*\n", page_text) if p.strip()]

        # If still only 1 block and page is substantial, split on single linebreaks before capital letters
        if len(raw_parts) <= 1 and len(page_text) > 200:
            raw_parts = [p.strip() for p in re.split(r"\n(?=[A-Z0-9])", page_text) if p.strip()]

        for part in raw_parts:
            part_clean = part.strip()
            # Omit document title lines without clause bodies
            if len(part_clean) >= 40:
                clauses.append({
                    "clause_id": f"CL-{clause_counter:03d}",
                    "page_number": page_num,
                    "text": part_clean
                })
                clause_counter += 1

    return clauses
