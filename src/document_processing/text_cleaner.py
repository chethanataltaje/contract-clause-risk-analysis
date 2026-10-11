"""
Text Cleaning and Normalization Module.
"""

import re

def clean_text(text: str) -> str:
    """
    Normalizes whitespace, removes header/footer artifact line breaks, and standardizes quotes.
    """
    if not text:
        return ""
    # Replace non-breaking spaces and irregular whitespace
    text = re.sub(r"[\xa0\u200b]", " ", text)
    # Standardize quotation marks
    text = re.sub(r'["""]', '"', text)
    text = re.sub(r"[''']", "'", text)
    # Collapse multiple spaces while keeping paragraphs intact
    text = re.sub(r"[ \t]+", " ", text)
    # Fix broken hyphenated words across lines
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    return text.strip()
