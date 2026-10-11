"""
Unit tests for Step 1 Data Preparation.
Validates contract-level split integrity, no data leakage, and category coverage.
"""

import pytest
import pandas as pd
from pathlib import Path
from src.utils.config import PROCESSED_DATA_DIR, TARGET_CATEGORIES

def test_processed_files_exist():
    train_path = PROCESSED_DATA_DIR / "train_clauses.csv"
    test_path = PROCESSED_DATA_DIR / "test_clauses.csv"
    assert train_path.exists(), "train_clauses.csv does not exist"
    assert test_path.exists(), "test_clauses.csv does not exist"

def test_no_data_leakage_between_contracts():
    train_df = pd.read_csv(PROCESSED_DATA_DIR / "train_clauses.csv")
    test_df = pd.read_csv(PROCESSED_DATA_DIR / "test_clauses.csv")
    
    train_contracts = set(train_df["contract_id"].unique())
    test_contracts = set(test_df["contract_id"].unique())
    
    # Contract-level split verification: intersection must be completely empty!
    overlap = train_contracts.intersection(test_contracts)
    assert len(overlap) == 0, f"Data leakage detected! Contracts present in both train & test: {overlap}"

def test_all_target_categories_represented():
    train_df = pd.read_csv(PROCESSED_DATA_DIR / "train_clauses.csv")
    test_df = pd.read_csv(PROCESSED_DATA_DIR / "test_clauses.csv")
    
    all_categories = set(train_df["category"].unique()).union(set(test_df["category"].unique()))
    for cat in TARGET_CATEGORIES:
        assert cat in all_categories, f"Target category '{cat}' is missing from processed datasets"

def test_clause_text_quality():
    train_df = pd.read_csv(PROCESSED_DATA_DIR / "train_clauses.csv")
    # All clauses should have non-empty text with substantial length
    assert (train_df["clause_text"].str.len() > 20).all(), "Found trivial or empty clause texts in training set"
