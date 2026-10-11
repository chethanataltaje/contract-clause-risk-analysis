"""
Data Preparation & Contract-Level Split Module for ClauseGuard AI.
Extracts target legal clause categories from CUAD or built-in benchmark contracts,
performing a strict contract-level split to prevent data leakage.
"""

import sys
import os
from pathlib import Path
import json
import re
import pandas as pd
from typing import List, Dict, Any, Tuple

# Ensure project root is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.utils.config import (
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    TARGET_CATEGORIES
)
from src.utils.logging_utils import get_logger

logger = get_logger("prepare_data")

# Mapping from CUAD exact question names / keys to clean standardized categories
CUAD_CATEGORY_MAP = {
    "Limitation Of Liability": "Limitation of Liability",
    "Limitation of Liability": "Limitation of Liability",
    "Cap on Liability": "Limitation of Liability",
    "Termination For Convenience": "Termination for Convenience",
    "Termination for Convenience": "Termination for Convenience",
    "Indemnification": "Indemnification",
    "Non-Compete": "Non-Compete",
    "Exclusivity": "Non-Compete",
    "Non-Disclosure": "Confidentiality",
    "Confidentiality": "Confidentiality",
    "Renewal Term": "Renewal / Term",
    "Term": "Renewal / Term"
}

# Synthetic & curated high-quality contract benchmark seeds
# Covers all 6 categories across real contract types for offline bootstrapping & testing
BENCHMARK_CONTRACT_SEEDS = [
    # Contract 1: Master Services Agreement (MSA) - Acme Corp & Beta LLC
    {
        "contract_id": "CONTRACT_001_MSA",
        "contract_type": "Master Services Agreement",
        "clauses": [
            {
                "category": "Limitation of Liability",
                "text": "In no event shall either party's cumulative liability under this Agreement exceed the total fees paid in the preceding twelve (12) months, or $100,000, whichever is less."
            },
            {
                "category": "Termination for Convenience",
                "text": "Either party may terminate this Agreement for any reason or no reason upon delivering sixty (60) days prior written notice to the other party."
            },
            {
                "category": "Indemnification",
                "text": "Provider shall indemnify, defend, and hold harmless Client from and against any third-party claims, liabilities, losses, and damages arising out of Provider's gross negligence or willful misconduct."
            },
            {
                "category": "Confidentiality",
                "text": "Each party agrees to maintain in strict confidence all proprietary technical and business information disclosed by the other party for a period of five (5) years following disclosure."
            },
            {
                "category": "Renewal / Term",
                "text": "This Agreement shall commence on the Effective Date and remain in effect for an initial period of two (2) years, renewing automatically for successive one (1) year terms unless terminated."
            }
        ]
    },
    # Contract 2: Non-Disclosure Agreement (NDA) - CyberSec Solutions
    {
        "contract_id": "CONTRACT_002_NDA",
        "contract_type": "Non-Disclosure Agreement",
        "clauses": [
            {
                "category": "Confidentiality",
                "text": "The Recipient shall hold all Confidential Information in confidence and shall not disclose such information to any third party without prior written authorization from Disclosing Party."
            },
            {
                "category": "Limitation of Liability",
                "text": "Except for breaches of confidentiality obligations, neither party shall be liable for indirect, incidental, punitive, or consequential damages."
            },
            {
                "category": "Renewal / Term",
                "text": "The term of confidentiality shall expire three (3) years from the date of initial disclosure of the applicable Confidential Information."
            },
            {
                "category": "Termination for Convenience",
                "text": "Disclosing Party may terminate discussions and demand return of all proprietary materials with seven (7) days written notice."
            }
        ]
    },
    # Contract 3: Employment & Restrictive Covenants - Horizon Global
    {
        "contract_id": "CONTRACT_003_EMP",
        "contract_type": "Employment Agreement",
        "clauses": [
            {
                "category": "Non-Compete",
                "text": "Employee agrees that during employment and for a period of twelve (12) months following termination, Employee shall not directly or indirectly engage in or operate any competing business within a 50-mile radius."
            },
            {
                "category": "Confidentiality",
                "text": "Employee shall not at any time, during or after employment, use or disclose Employer's proprietary customer lists, trade secrets, or source code."
            },
            {
                "category": "Termination for Convenience",
                "text": "Employer may terminate Employee's employment at will, with or without cause, provided Employer gives thirty (30) days written notice or pay in lieu thereof."
            },
            {
                "category": "Indemnification",
                "text": "Employer agrees to indemnify Employee to the maximum extent permitted by applicable law for actions performed within the scope of regular employment duties."
            }
        ]
    },
    # Contract 4: Commercial Software Licensing Agreement (SaaS) - CloudScale
    {
        "contract_id": "CONTRACT_004_SAAS",
        "contract_type": "Software License Agreement",
        "clauses": [
            {
                "category": "Limitation of Liability",
                "text": "To the maximum extent permitted by law, Vendor's total aggregate liability arising out of or related to the Cloud Service shall not exceed $50,000 or the subscription fees paid in the last 6 months."
            },
            {
                "category": "Indemnification",
                "text": "Vendor agrees to defend Customer against any third-party legal claims alleging that Customer's authorized use of the software infringes any valid patent or copyright."
            },
            {
                "category": "Non-Compete",
                "text": "Licensee shall not reverse engineer, decompile, or develop a substantially similar competing cloud service utilizing Vendor's benchmark metrics."
            },
            {
                "category": "Renewal / Term",
                "text": "The subscription term shall automatically renew for additional consecutive periods equal to twelve (12) months unless either party provides notice of non-renewal at least 30 days prior to expiration."
            },
            {
                "category": "Termination for Convenience",
                "text": "Customer may terminate the subscription for convenience upon forty-five (45) days prior written notice, subject to forfeiture of prepaid fees."
            }
        ]
    },
    # Contract 5: Consulting & Independent Contractor Agreement - Apex Advisory
    {
        "contract_id": "CONTRACT_005_CONSULT",
        "contract_type": "Consulting Agreement",
        "clauses": [
            {
                "category": "Indemnification",
                "text": "Consultant agrees to indemnify and hold harmless Company from any claims, damages, or fines arising from Consultant's failure to comply with statutory tax obligations."
            },
            {
                "category": "Limitation of Liability",
                "text": "In no event shall Company be liable for lost profits, loss of data, or special damages, and total liability shall be capped at $25,000."
            },
            {
                "category": "Non-Compete",
                "text": "During the term and for six (6) months thereafter, Consultant shall not solicit any active clients of Company whom Consultant worked with directly."
            },
            {
                "category": "Confidentiality",
                "text": "All deliverables and proprietary market analyses generated under this statement of work remain strictly confidential Company property."
            },
            {
                "category": "Termination for Convenience",
                "text": "Either party may terminate any ongoing Statement of Work with fourteen (14) days advance notice in writing."
            },
            {
                "category": "Renewal / Term",
                "text": "This agreement shall be valid for a duration of one (1) year from signature and may be renewed by mutual written amendment."
            }
        ]
    },
    # Contract 6: Commercial Lease Agreement - Metro Properties
    {
        "contract_id": "CONTRACT_006_LEASE",
        "contract_type": "Commercial Real Estate Lease",
        "clauses": [
            {
                "category": "Termination for Convenience",
                "text": "Tenant shall have the right to early terminate this Lease after Month 24 upon giving ninety (90) days advance written notice and paying a penalty fee of $15,000."
            },
            {
                "category": "Limitation of Liability",
                "text": "Landlord's liability for any default or damage under this lease shall be strictly limited to Landlord's equity interest in the leased commercial building."
            },
            {
                "category": "Indemnification",
                "text": "Tenant covenants to indemnify and hold Landlord harmless against any slip-and-fall injuries, damages, or liabilities occurring within the premises."
            },
            {
                "category": "Renewal / Term",
                "text": "Tenant is granted an option to renew the lease for an additional term of thirty-six (36) months by written notice delivered at least 180 days prior to expiration."
            }
        ]
    },
    # Contract 7: Vendor Procurement Agreement - Delta Supply
    {
        "contract_id": "CONTRACT_007_PROCURE",
        "contract_type": "Vendor Procurement Agreement",
        "clauses": [
            {
                "category": "Limitation of Liability",
                "text": "Neither Supplier nor Purchaser shall be liable for indirect or punitive damages; Supplier liability for defective hardware is strictly capped at product replacement costs."
            },
            {
                "category": "Termination for Convenience",
                "text": "Purchaser reserves the right to terminate any Purchase Order without penalty upon twenty-one (21) days notice to Supplier."
            },
            {
                "category": "Indemnification",
                "text": "Supplier warrants product compliance and agrees to defend Purchaser from IP infringement actions brought by third parties."
            },
            {
                "category": "Confidentiality",
                "text": "All unit pricing models, discount schedules, and specifications are confidential trade secrets."
            },
            {
                "category": "Renewal / Term",
                "text": "The procurement term shall continue for twenty-four (24) months and renew annually upon mutual written consent."
            }
        ]
    },
    # Contract 8: Joint Venture & Partnership Agreement - Zenith Ventures
    {
        "contract_id": "CONTRACT_008_PARTNER",
        "contract_type": "Partnership Agreement",
        "clauses": [
            {
                "category": "Non-Compete",
                "text": "Neither partner shall establish, finance, or advise an entity operating in direct competition with the Joint Venture for two (2) years following dissolution."
            },
            {
                "category": "Confidentiality",
                "text": "Both partners agree not to disclose financial records, audit findings, or intellectual property without unanimous written consent."
            },
            {
                "category": "Indemnification",
                "text": "Each partner shall indemnify the partnership for liabilities incurred as a result of unauthorized commitments made outside specified authority."
            },
            {
                "category": "Limitation of Liability",
                "text": "Liability between partners for operational errors shall be capped at each partner's respective initial capital contribution of $200,000."
            },
            {
                "category": "Termination for Convenience",
                "text": "Either partner may exit the partnership upon providing one hundred eighty (180) days advance notice to initiate orderly asset liquidation."
            },
            {
                "category": "Renewal / Term",
                "text": "The partnership term shall run for five (5) years from the Effective Date."
            }
        ]
    }
]


def load_cuad_from_hf_or_cache() -> List[Dict[str, Any]]:
    """
    Attempts to load CUAD clauses from Hugging Face datasets if online.
    Falls back gracefully to the benchmark seed contracts.
    """
    try:
        from datasets import load_dataset
        logger.info("Checking for Hugging Face CUAD dataset...")
        cuad_ds = load_dataset("cuad", split="train")
        logger.info(f"Loaded CUAD successfully with {len(cuad_ds)} samples.")

        records = []
        for row in cuad_ds:
            contract_title = row.get("title", "UNKNOWN_CONTRACT")
            context = row.get("context", "")
            qas = row.get("qas", [])
            for qa in qas:
                q_text = qa.get("question", "")
                answers = qa.get("answers", [])
                matched_category = None
                for cuad_cat, clean_cat in CUAD_CATEGORY_MAP.items():
                    if cuad_cat.lower() in q_text.lower():
                        matched_category = clean_cat
                        break

                if matched_category and answers:
                    for ans in answers:
                        ans_text = ans.get("text", "").strip()
                        if len(ans_text) > 30:
                            records.append({
                                "contract_id": contract_title,
                                "category": matched_category,
                                "clause_text": ans_text
                            })
        if len(records) > 50:
            logger.info(f"Extracted {len(records)} category-filtered clauses from Hugging Face CUAD.")
            return records
    except Exception as e:
        logger.warning(f"Hugging Face CUAD fetch skipped or unavailable ({e}). Using curated benchmark dataset.")

    # Fallback to curated benchmark contracts
    flat_records = []
    for contract in BENCHMARK_CONTRACT_SEEDS:
        c_id = contract["contract_id"]
        for cl in contract["clauses"]:
            flat_records.append({
                "contract_id": c_id,
                "category": cl["category"],
                "clause_text": cl["text"]
            })
    logger.info(f"Loaded {len(flat_records)} curated clauses across {len(BENCHMARK_CONTRACT_SEEDS)} benchmark contracts.")
    return flat_records


def perform_contract_level_split(
    records: List[Dict[str, Any]], 
    train_ratio: float = 0.75, 
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Performs contract-level splitting:
    All clauses originating from a single contract are strictly assigned to EITHER
    the training set OR the testing set, preventing data leakage.
    """
    df = pd.DataFrame(records)
    
    unique_contracts = df["contract_id"].drop_duplicates().sample(
        frac=1.0, 
        random_state=random_state
    ).tolist()

    n_train = max(1, int(len(unique_contracts) * train_ratio))
    train_contracts = set(unique_contracts[:n_train])
    test_contracts = set(unique_contracts[n_train:])

    # Edge case: Ensure test set has at least 1 contract
    if not test_contracts:
        test_contracts = {unique_contracts[-1]}
        train_contracts.remove(unique_contracts[-1])

    train_df = df[df["contract_id"].isin(train_contracts)].copy().reset_index(drop=True)
    test_df = df[df["contract_id"].isin(test_contracts)].copy().reset_index(drop=True)

    logger.info(f"Contract Split: {len(train_contracts)} train contracts vs {len(test_contracts)} test contracts.")
    logger.info(f"Clause Counts: {len(train_df)} train clauses vs {len(test_df)} test clauses.")

    return train_df, test_df


def prepare_and_save_data():
    """
    Main data preparation pipeline.
    """
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    records = load_cuad_from_hf_or_cache()
    train_df, test_df = perform_contract_level_split(records)

    train_path = PROCESSED_DATA_DIR / "train_clauses.csv"
    test_path = PROCESSED_DATA_DIR / "test_clauses.csv"
    full_path = PROCESSED_DATA_DIR / "all_clauses.csv"

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    pd.concat([train_df, test_df]).to_csv(full_path, index=False)

    logger.info(f"Saved training dataset: {train_path}")
    logger.info(f"Saved testing dataset: {test_path}")

    # Log class distribution
    logger.info("\n--- Training Set Class Distribution ---")
    logger.info(train_df["category"].value_counts().to_string())

    logger.info("\n--- Testing Set Class Distribution ---")
    logger.info(test_df["category"].value_counts().to_string())
    print("\n[SUCCESS] Step 1 Data Preparation Complete!")
    print(f"Train clauses: {len(train_df)} | Test clauses: {len(test_df)}")


if __name__ == "__main__":
    prepare_and_save_data()
