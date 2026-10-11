# ClauseLens — Institutional Contract Audit & Risk Analysis Platform

**ClauseLens** is an end-to-end Natural Language Processing (NLP) and machine learning system for automated commercial contract review. It ingests complex legal agreements (PDFs), segments clauses, extracts mission-critical entities and linguistic patterns, classifies clauses across key legal categories, and flags hidden exposure and ambiguous language through an explainable risk scoring engine.

---

## 📌 1. Executive Summary & Capabilities

Manual legal review of commercial agreements (Master Services Agreements, Non-Disclosure Agreements, Vendor Contracts, Employment Covenants) is time-consuming and prone to human oversight. ClauseLens functions as an intelligent assistive workspace for legal, procurement, and operations teams:

- **Document Ingestion & Boundary Parsing**: Extracts text page-by-page from raw contract PDFs using PyMuPDF while preserving page references and document citations.
- **Contract-Level Data Splitting**: Avoids clause-level data leakage by strictly partitioning training and evaluation sets by whole contract agreements.
- **Deontic Modality & Linguistic Analysis**: Analyzes mandatory obligations (*"shall"*, *"must"*) versus discretionary permissions (*"may"*, *"can"*), conditional qualifiers (*"provided that"*, *"in the event that"*), and liability waivers (*"in no event"*).
- **Structured Information Extraction**: Automatically extracts financial caps (`$`, `%`), notice timeframes (`30 days`, `12 months`), renewal deadlines, and contracting entities.
- **Multi-Model Clause Classification**: Implements and benchmarks classical lexical baselines (**TF-IDF + Logistic Regression**) alongside dense semantic representations (**Sentence-BERT `all-MiniLM-L6-v2`**).
- **Explainable Legal Risk Engine**: Evaluates rule-based heuristics to flag uncapped liabilities, aggressive termination rights, and subjective legal standards (*"best efforts"*, *"reasonable efforts"*, *"promptly"*) with plain-English rationales.
- **Institutional Workspace UI**: Interactive split-screen review dashboard built with Streamlit, styled with editorial legal typography and instant markdown audit report generation.

---

## 🗂️ 2. Repository Architecture

```plaintext
contract-clause-risk-analysis/
├── app.py                             # Streamlit split-screen legal document workspace
├── requirements.txt                   # Production Python dependencies
├── .env.example                       # Environment template
├── .gitignore                         # Configured git exclusions (ignores caches & binaries)
├── README.md                          # Technical architecture & documentation
│
├── data/
│   ├── raw/                           # Raw benchmark downloads (CUAD archives)
│   ├── processed/                     # Cleaned, contract-level split datasets
│   │   ├── train_clauses.csv          # Training split (partitioned by contract ID)
│   │   ├── test_clauses.csv           # Evaluation split (strictly held-out contracts)
│   │   └── all_clauses.csv            # Combined reference corpus
│   └── sample_contracts/              # Evaluation PDFs for live testing
│       ├── sample_nda.pdf             # Non-Disclosure Agreement
│       ├── sample_msa.pdf             # Master Services Agreement
│       └── sample_employment.pdf      # Employment Agreement & Restrictive Covenants
│
├── src/
│   ├── document_processing/
│   │   ├── pdf_extractor.py           # PyMuPDF text extraction preserving page references
│   │   ├── text_cleaner.py            # Normalizes whitespace & extraction noise
│   │   └── clause_segmenter.py        # Splits documents into numbered clauses
│   │
│   ├── nlp/
│   │   ├── feature_extractor.py       # Modals (obligation vs permission), conditionals, negations
│   │   ├── information_extractor.py   # Currency amounts, deadlines, notice periods, parties
│   │   ├── ambiguity_detector.py      # Flags vague terms ('reasonable', 'best efforts', 'promptly')
│   │   └── clause_classifier.py       # Unified inference wrapper (TF-IDF / SBERT)
│   │
│   ├── risk_engine/
│   │   ├── risk_rules.py              # Transparent legal risk heuristics
│   │   ├── risk_scorer.py             # Aggregates signals into review priority tiers
│   │   └── explanations.py            # Generates plain-English findings & recommendations
│   │
│   ├── services/
│   │   ├── analysis_service.py        # End-to-end pipeline orchestrator
│   │   └── report_service.py          # Markdown legal audit report generator
│   │
│   └── utils/
│       ├── config.py                  # Project paths, categories, and keyword dictionaries
│       └── logging_utils.py           # Standardized logger
│
├── models/
│   ├── baselines/                     # Serialized TF-IDF vectorizer + Logistic Regression
│   └── embeddings/                    # SBERT model cache & classifier weights
│
├── experiments/
│   ├── prepare_data.py                # Contract-level split dataset generator
│   ├── create_sample_pdfs.py          # Generates test contract PDFs
│   ├── train_baseline.py              # Trains TF-IDF + Logistic Regression
│   ├── train_sbert.py                 # Encodes dense vectors & trains SBERT classifier
│   ├── evaluate_models.py             # Comparative benchmark evaluation
│   └── results/
│       └── model_comparison_metrics.csv # Saved metrics (accuracy, F1, latency)
│
└── tests/
    ├── test_data_preparation.py       # Contract split integrity & zero-leakage tests
    ├── test_information_extraction.py # Modality, regex entities, and vagueness tests
    ├── test_clause_classification.py  # Model inference and probability calibration tests
    ├── test_risk_engine.py            # Risk rules and explanation generation tests
    └── test_end_to_end.py             # Full pipeline tests on real sample PDFs
```

---

## 🔬 3. Machine Learning & NLP Architecture

### Target Legal Categories
1. **Limitation of Liability**: Damage caps, waivers of consequential loss, aggregate ceilings.
2. **Termination for Convenience**: Unilateral cancellation rights and advance notice requirements.
3. **Indemnification**: Third-party claim defense, hold-harmless commitments, IP liabilities.
4. **Non-Compete**: Restrictive employment covenants, geographic limitations, duration bars.
5. **Confidentiality**: Definition of trade secrets, non-disclosure durations, survival terms.
6. **Renewal / Term**: Automatic renewal conditions, term duration, non-renewal windows.

### Comparative Model Benchmarks
Evaluated on the held-out test split (partitioned strictly by contract to guarantee zero data leakage):

| Model Architecture | Accuracy | Macro Precision | Macro Recall | Macro F1 | Latency (ms/sample) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **TF-IDF + Logistic Regression** | **90.0%** | **0.9167** | **0.9167** | **0.8889** | **1.42 ms** |
| **Sentence-BERT (`all-MiniLM-L6-v2`)** | **90.0%** | **0.7500** | **0.8333** | **0.7778** | **8.89 ms** |

> **Key Insight**: Due to the formulaic, statutory nature of commercial drafting, classical TF-IDF provides high precision (0.9167) by leveraging exact keyword anchors (*"indemnify"*, *"cumulative liability"*). SBERT provides rich semantic flexibility across paraphrased clauses, though general-domain embeddings experience semantic overlap between closely related clauses like *Non-Compete* and *Confidentiality*.

---

## 🛡️ 4. Risk Evaluation Heuristics & Scoring

The risk engine decouples statistical clause classification from risk evaluation, applying configurable rules:

| Risk Tier | Condition / Trigger | Example Finding |
| :--- | :--- | :--- |
| 🔴 **High Risk** | Limitation of Liability with no financial cap | *Potential uncapped liability: Clause specifies no dollar ceiling.* |
| 🔴 **High Risk** | Immediate termination or undefined notice window | *Terminable without adequate advance notice window.* |
| 🔴 **High Risk** | Non-compete covenant lacking defined duration | *Perpetual competitive restriction without expiration date.* |
| 🟡 **Needs Review** | Vague legal qualifiers (*"best efforts"*, *"promptly"*) | *Subjective standard creates disproportionate exposure.* |
| 🟢 **Informational** | Bilateral boilerplate clause with clear definitions | *Standard reciprocal terms; no abnormal exposure identified.* |

---

## ⚡ 5. Setup & Installation

### 1. Clone & Environment Setup
```bash
git clone <YOUR_REPO_URL>
cd contract-clause-risk-analysis

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (cmd):
venv\Scripts\activate
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Prepare Data & Train Models
```bash
# Generate contract-level splits and sample evaluation PDFs
python experiments/prepare_data.py
python experiments/create_sample_pdfs.py

# Train classification models
python experiments/train_baseline.py
python experiments/train_sbert.py

# Benchmark all models
python experiments/evaluate_models.py
```

### 3. Launch the Workspace UI
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧪 6. Automated Test Suite

The platform includes full test coverage across document parsing, entity extraction, model inference, risk scoring, and end-to-end integration:

```bash
pytest tests/ -v
```

**Test Coverage Summary:**
- `test_data_preparation.py`: Validates contract-level split partition integrity and zero data leakage.
- `test_information_extraction.py`: Validates deontic modality, regex entity extraction (currency, percentages, deadlines), and ambiguity detection.
- `test_clause_classification.py`: Validates inference and probability calibration for TF-IDF and SBERT.
- `test_risk_engine.py`: Validates risk rules, scoring tiers, and plain-English explanation generation.
- `test_end_to_end.py`: Validates the end-to-end ingestion pipeline on real contract PDFs.
