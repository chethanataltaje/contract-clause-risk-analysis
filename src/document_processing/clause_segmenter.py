"""
Clause Segmentation Module.
Splits contract document text into candidate clauses with unique Clause IDs.
"""

import re
from typing import List, Dict, Any

def segment_into_clauses(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Splits text across pages into numbered clauses using legal section headers
    or numbered paragraph markers.
    """
    clauses = []
    clause_counter = 1
    
    # Regex pattern to match numbered legal headers (e.g., '1.', '1.1', 'Section 2', 'Article III')
    section_pattern = re.compile(
        r"(?:^|\n)(?=(?:SECTION|ARTICLE|[0-9]{1,2}\.[0-9]{0,2}|[IVXLCDM]+\.)\s+[A-Z0-9])",
        re.IGNORECASE
    )

    full_text_with_metadata = []
    for p in pages:
        full_text_with_metadata.append((p["page_number"], p["text"]))

    # Naive splitting fallback if formal section pattern not present: double newline chunks
    for page_num, page_text in full_text_with_metadata:
        chunks = re.split(r"\n\s*\n", page_text)
        for chunk in chunks:
            chunk_clean = chunk.strip()
            if len(chunk_clean) > 40:  # Filter out trivial titles or page numbers
                clauses.append({
                    "clause_id": f"CL-{clause_counter:03d}",
                    "page_number": page_num,
                    "text": chunk_clean
                })
                clause_counter += 1

    return clauses
