"""
Configuration constants and paths for ClauseGuard AI.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_CONTRACTS_DIR = DATA_DIR / "sample_contracts"

MODELS_DIR = BASE_DIR / "models"
BASELINES_DIR = MODELS_DIR / "baselines"
EMBEDDINGS_DIR = MODELS_DIR / "embeddings"
TRANSFORMER_DIR = MODELS_DIR / "transformer"

EXPERIMENTS_DIR = BASE_DIR / "experiments"
RESULTS_DIR = EXPERIMENTS_DIR / "results"

# 6 Focus CUAD Categories for high feasibility & rigorous evaluation
TARGET_CATEGORIES = [
    "Limitation of Liability",
    "Termination for Convenience",
    "Indemnification",
    "Non-Compete",
    "Confidentiality",
    "Renewal / Term"
]

# Risk Indicators (Configurable Rule Base - Not assumed to be CUAD labels)
RISK_CATEGORIES = {
    "HIGH_RISK": "High Risk",
    "NEEDS_REVIEW": "Needs Review",
    "INFORMATIONAL": "Informational"
}

# Modality & Conditionals
MODAL_OBLIGATIONS = ["shall", "must", "agrees to", "will", "is required to"]
MODAL_PERMISSIONS = ["may", "is entitled to", "can"]
CONDITIONALS = ["if", "provided that", "in the event that", "subject to", "unless", "except as"]
NEGATION_TERMS = ["in no event", "shall not", "neither", "nor", "without", "no liability", "waives"]
AMBIGUITY_TERMS = ["reasonable", "promptly", "best efforts", "material", "substantially", "from time to time"]
