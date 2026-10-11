# Contract Clause Risk Analysis (ClauseGuard AI)

An end-to-end NLP and machine learning system for automated contract analysis, clause classification, entity extraction, and risk assessment.

---

## 📌 Overview
Reviewing commercial legal contracts manually is tedious, error-prone, and slow. **Contract Clause Risk Analysis** transforms raw contract documents into structured intelligence for human reviewers:

1. **Document Ingestion & Parsing**: Extracts clean text page-by-page from PDF contracts (NDAs, MSAs, Leases, Employment Agreements) while preserving page citations.
2. **Clause Segmentation**: Identifies clause boundaries and generates discrete, trackable clause units.
3. **Linguistic & Information Extraction**: Extracts deontic modals (*obligation vs. permission*), conditional triggers, limitations/negations, monetary penalties, notice periods, and renewal deadlines.
4. **Multi-Model Clause Classification**: Categorizes clauses into high-impact categories using multiple evaluated NLP approaches (TF-IDF baselines, semantic SBERT embeddings, and fine-tuned Transformer models).
5. **Configurable Risk Engine**: Identifies potentially risky clauses, ambiguous wording (*"best efforts"*, *"reasonable"*), and missing caps without claiming definitive legal counsel.
6. **Interactive Dashboard & Reporting**: Provides a human-in-the-loop Streamlit interface with color-coded risk highlights, entity badges, and exportable review summaries.

---

## 🗂️ Project Structure

```plaintext
contract-clause-risk-analysis/
├── app.py                             # Streamlit web application & review dashboard
├── requirements.txt                   # Project dependencies
├── .env.example                       # Environment configuration template
├── .gitignore                         # Git exclusion rules
├── README.md                          # Project documentation and guide
│
├── data/
│   ├── raw/                           # Raw benchmark datasets and source files
│   ├── processed/                     # Cleaned, contract-level split clause datasets
│   └── sample_contracts/              # Evaluation PDFs (NDA, MSA, Lease, Employment)
│
├── src/
│   ├── document_processing/
│   │   ├── pdf_extractor.py           # PyMuPDF text extraction preserving page references
│   │   ├── text_cleaner.py            # Normalizes whitespace & extraction artifacts
│   │   └── clause_segmenter.py        # Splits documents into numbered clauses
│   │
│   ├── nlp/
│   │   ├── feature_extractor.py       # Modal verbs, conditionals, negations
│   │   ├── information_extractor.py   # Amounts, deadlines, notice periods
│   │   ├── ambiguity_detector.py      # Flags vague legal terms ('reasonable', 'best efforts')
│   │   └── clause_classifier.py       # Classification wrappers (TF-IDF / SBERT / Transformers)
│   │
│   ├── risk_engine/
│   │   ├── risk_rules.py              # Rule heuristics for risk prioritization
│   │   ├── risk_scorer.py             # Combines signals into priority scores
│   │   └── explanations.py            # Generates human-readable rationales for flags
│   │
│   ├── services/
│   │   ├── analysis_service.py        # Orchestrates the end-to-end analysis pipeline
│   │   └── report_service.py          # Generates structured summary & downloadable reports
│   │
│   └── utils/
│       ├── config.py                  # Project paths, categories & thresholds
│       └── logging_utils.py           # Standardized logger
│
├── models/
│   ├── baselines/                     # Serialized TF-IDF + Logistic Regression models
│   ├── embeddings/                    # SBERT cache & configuration
│   └── transformer/                   # Fine-tuned Transformer weights
│
├── experiments/
│   ├── prepare_data.py                # Prepares benchmark data with contract-level splits
│   ├── train_baseline.py              # Trains TF-IDF + Logistic Regression
│   ├── train_sbert.py                 # Generates SBERT embeddings & trains classifier
│   ├── evaluate_models.py             # Benchmark comparisons (Precision, Recall, F1, Latency)
│   └── results/                       # Confusion matrices, metric tables & plots
│
└── tests/
    ├── test_pdf_extraction.py
    ├── test_clause_classification.py
    ├── test_information_extraction.py
    ├── test_risk_engine.py
    └── test_end_to_end.py
```

---

## 🔬 NLP & Machine Learning Architecture

The system evaluates and benchmarks multiple NLP paradigms:

| Approach | Architecture | Primary Role |
| :--- | :--- | :--- |
| **Regex & Rule Baseline** | Pattern matching & regular expressions | Transparent baseline for dates, currency, and modal verb counts |
| **Statistical Baseline** | TF-IDF Vectorizer + Logistic Regression | Fast, interpretable lexical classification baseline |
| **Semantic Embeddings** | Sentence-BERT (`all-MiniLM-L6-v2`) + Classifier | Dense contextual representations capturing semantic meaning |
| **Transformer Model** | Pretrained LegalBERT / RoBERTa | Fine-tuned deep language model for domain-specific contract understanding |

### Linguistic Patterns & Entity Detection
- **Deontic Modals:** Differentiates mandatory obligations (*"shall"*, *"must"*) from discretionary permissions (*"may"*, *"can"*).
- **Conditionals & Qualifiers:** Flags triggers including *"in the event that"*, *"provided that"*, and *"subject to"*.
- **Negation & Liability Caps:** Detects limitations such as *"in no event shall liability exceed"*.
- **Ambiguity Indicators:** Identifies vague standards like *"best efforts"*, *"reasonable notice"*, and *"promptly"*.

---

## ⚡ Quick Start

### 1. Installation
Clone the repository and install the dependencies:
```bash
git clone <YOUR_REPO_URL>
cd contract-clause-risk-analysis
python -m venv venv
venv\Scripts\activate      # On Windows (or 'source venv/bin/activate' on Linux/macOS)
pip install -r requirements.txt
```

### 2. Prepare Data & Train Models
```bash
python experiments/prepare_data.py
python experiments/train_baseline.py
python experiments/train_sbert.py
python experiments/evaluate_models.py
```

### 3. Run Web Dashboard
```bash
streamlit run app.py
```

---

## 🧪 Testing
Run unit and integration tests using `pytest`:
```bash
pytest tests/ -v
```
