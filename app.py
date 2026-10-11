"""
ClauseLens - Institutional Contract Intelligence & Due-Diligence Workspace.
Editorial legal document viewer with split-screen risk inspector.
"""

import streamlit as st
from pathlib import Path
import json

from src.utils.config import SAMPLE_CONTRACTS_DIR
from src.services.analysis_service import ContractAnalysisService
from src.services.report_service import generate_markdown_report

# Page Config
st.set_page_config(
    page_title="ClauseLens — Document Workspace",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Bespoke LegalTech Workspace CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Hide standard Streamlit chrome */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }

    body {
        background-color: #f8fafc;
        color: #0f172a;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* Top Navigation Bar - Crisp White Container */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.85rem 1.4rem;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .nav-brand {
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #0f172a;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .nav-breadcrumb {
        font-size: 0.82rem;
        color: #64748b;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
    }
    .status-pill {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .status-ready {
        background: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }

    /* Document Heading in Crisp White Paper Container */
    .doc-title-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.25rem 1.75rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .doc-title {
        font-family: 'Newsreader', Georgia, serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #0f172a !important;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .doc-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Document Clause Line Item - Crisp White Paper Card */
    .clause-row {
        position: relative;
        padding: 1.1rem 1.25rem 1.1rem 3.5rem;
        margin-bottom: 0.85rem;
        border-radius: 8px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        transition: all 0.15s ease;
    }
    .clause-row:hover {
        border-color: #cbd5e1;
        box-shadow: 0 3px 8px rgba(0,0,0,0.08);
    }
    .clause-row.active-clause {
        border-color: #94a3b8;
        background: #f8fafc;
        box-shadow: 0 0 0 2px rgba(148, 163, 184, 0.2);
    }
    .clause-num {
        position: absolute;
        left: 1rem;
        top: 1.15rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        font-weight: 600;
        color: #94a3b8;
        user-select: none;
    }
    .clause-body {
        font-family: 'Newsreader', Georgia, serif;
        font-size: 1.08rem;
        line-height: 1.65;
        color: #0f172a !important;
        font-weight: 500;
    }

    /* Risk indicators on document (crisp colored margin stripe) */
    .indicator-high {
        border-left: 5px solid #e11d48 !important;
    }
    .indicator-review {
        border-left: 5px solid #f59e0b !important;
    }
    .indicator-info {
        border-left: 5px solid #64748b !important;
    }

    /* Right Inspector Panel - Crisp Clean Paper Container */
    .inspector-panel {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
        color: #0f172a;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .inspector-header {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 700;
        color: #475569;
        margin-bottom: 1rem;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 0.5rem;
    }
    .inspector-field {
        margin-bottom: 1.1rem;
    }
    .field-title {
        font-size: 0.72rem;
        text-transform: uppercase;
        font-weight: 700;
        color: #64748b;
        margin-bottom: 0.25rem;
    }
    .field-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: #0f172a;
    }
    .tag-chip {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        background: #f1f5f9;
        color: #1e293b;
        padding: 2px 7px;
        border-radius: 4px;
        border: 1px solid #cbd5e1;
        display: inline-block;
        margin: 2px 4px 2px 0;
    }
    .badge-critical {
        background: #4c0519;
        color: #fecdd3;
        border: 1px solid #e11d48;
        font-weight: 600;
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 4px;
    }
    .badge-amber {
        background: #451a03;
        color: #fef3c7;
        border: 1px solid #d97706;
        font-weight: 600;
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 4px;
    }
    .badge-slate {
        background: #0f172a;
        color: #94a3b8;
        border: 1px solid #334155;
        font-weight: 600;
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_analysis_service(model_name: str):
    return ContractAnalysisService(default_model=model_name)

def main():
    # Top Utility Bar
    st.markdown("""
    <div class="top-nav">
        <div class="nav-brand">
            <span>ClauseLens</span>
            <span class="nav-breadcrumb">/ Workspace / Due Diligence</span>
        </div>
        <div>
            <span class="status-pill status-ready">Pipeline Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Workspace Control Bar
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 1])
    with ctrl_col1:
        sample_options = {
            "Master Services Agreement (MSA)": "sample_msa.pdf",
            "Non-Disclosure Agreement (NDA)": "sample_nda.pdf",
            "Employment Covenant": "sample_employment.pdf"
        }
        chosen_sample = st.selectbox(
            "Load Contract",
            options=list(sample_options.keys()),
            label_visibility="collapsed"
        )
    with ctrl_col2:
        model_choice = st.selectbox(
            "Classification Engine",
            options=["baseline", "sbert"],
            format_func=lambda x: "Lexical Engine (TF-IDF + LR)" if x == "baseline" else "Semantic Engine (Sentence-BERT)",
            label_visibility="collapsed"
        )
    with ctrl_col3:
        uploaded_file = st.file_uploader(
            "Upload Custom PDF",
            type=["pdf"],
            label_visibility="collapsed"
        )

    # Resolve document bytes
    doc_name = chosen_sample
    pdf_bytes = None

    if uploaded_file is not None:
        pdf_bytes = uploaded_file.read()
        doc_name = uploaded_file.name
    else:
        sample_file = sample_options[chosen_sample]
        sample_path = SAMPLE_CONTRACTS_DIR / sample_file
        if sample_path.exists():
            with open(sample_path, "rb") as f:
                pdf_bytes = f.read()

    if not pdf_bytes:
        st.warning("No document available.")
        return

    # Execute Analysis
    service = get_analysis_service(model_choice)
    result = service.analyze_contract_pdf(pdf_bytes, filename=doc_name)
    clauses = result["clauses"]

    # State tracking for selected clause
    if "selected_clause_idx" not in st.session_state or st.session_state.selected_clause_idx >= len(clauses):
        st.session_state.selected_clause_idx = 0

    st.markdown("<br>", unsafe_allow_html=True)

    # 2-Column Split-Screen Workspace (Left: Legal Document Sheet | Right: Audit Inspector)
    doc_col, inspector_col = st.columns([7, 5])

    # Left Column: Document Reader
    with doc_col:
        header_html = (
            f'<div class="doc-title-container">'
            f'<div class="doc-title">{doc_name.replace(".pdf", "").upper()}</div>'
            f'<div class="doc-subtitle">Segmented Legal Corpus &middot; {len(clauses)} Clauses Verified</div>'
            f'</div>'
        )
        st.markdown(header_html, unsafe_allow_html=True)

        for idx, cl in enumerate(clauses):
            risk_lvl = cl["risk_level"]
            indicator_class = "indicator-high" if risk_lvl == "High Risk" else ("indicator-review" if risk_lvl == "Needs Review" else "indicator-info")
            is_active = "active-clause" if idx == st.session_state.selected_clause_idx else ""

            # Interactive clause card
            c_label = f"¶ {idx+1:02d} · {cl['clause_id']} — {cl['predicted_category']} [{risk_lvl}]"
            with st.expander(c_label, expanded=(idx == st.session_state.selected_clause_idx)):
                clause_html = f'<div class="clause-row {indicator_class} {is_active}"><span class="clause-num">{idx+1:02d}</span><div class="clause-body">"{cl["clause_text"]}"</div></div>'
                st.markdown(clause_html, unsafe_allow_html=True)
                if st.button("Inspect in Panel →", key=f"btn_inspect_{idx}"):
                    st.session_state.selected_clause_idx = idx
                    st.rerun()

    # Right Column: Audit Inspector
    selected_cl = clauses[st.session_state.selected_clause_idx]
    with inspector_col:
        r_lvl = selected_cl["risk_level"]
        badge_cls = "badge-critical" if r_lvl == "High Risk" else ("badge-amber" if r_lvl == "Needs Review" else "badge-slate")

        ents = selected_cl.get("extracted_entities", {})
        ling = selected_cl.get("linguistic_summary", {})

        chips = []
        for amt in ents.get("amounts", []):
            chips.append(f"<span class='tag-chip'>Figure: {amt}</span>")
        for dl in ents.get("deadlines", []):
            chips.append(f"<span class='tag-chip'>Window: {dl}</span>")
        for p in ents.get("parties", []):
            chips.append(f"<span class='tag-chip'>Party: {p}</span>")
        chips.append(f"<span class='tag-chip'>Modality: {ling.get('modality', 'Neutral')}</span>")
        chips_html = "".join(chips) if chips else "<span style='font-size:0.8rem; color:#94a3b8;'>No distinct entities detected.</span>"

        panel_html = (
            '<div class="inspector-panel">'
            '<div class="inspector-header">Clause Audit Inspector</div>'
            '<div class="inspector-field">'
            '<div class="field-title">Clause Identification</div>'
            f'<div class="field-value" style="font-family:\'JetBrains Mono\', monospace; font-size:0.85rem;">{selected_cl["clause_id"]} &middot; Page {selected_cl["page_number"]}</div>'
            '</div>'
            '<div class="inspector-field">'
            '<div class="field-title">Predicted Legal Classification</div>'
            f'<div class="field-value">{selected_cl["predicted_category"]} <span style="font-size:0.75rem; color:#64748b; font-weight:400;">({selected_cl["confidence"]*100:.1f}% confidence)</span></div>'
            '</div>'
            '<div class="inspector-field">'
            '<div class="field-title">Risk Assessment Tier</div>'
            f'<div><span class="{badge_cls}">{r_lvl.upper()}</span></div>'
            '</div>'
            '<div class="inspector-field">'
            '<div class="field-title">Audit Finding & Rationale</div>'
            f'<div style="font-size:0.88rem; line-height:1.5; color:#1e293b; font-weight:500;">{selected_cl["explanation"]["summary"]}</div>'
            '</div>'
            '<div class="inspector-field">'
            '<div class="field-title">Recommended Counsel Action</div>'
            f'<div style="font-size:0.84rem; line-height:1.45; color:#334155; background:#f8fafc; padding:0.6rem 0.8rem; border-radius:4px; border:1px solid #e2e8f0; font-weight:500;">{selected_cl["explanation"]["recommendation"]}</div>'
            '</div>'
            '<div class="inspector-field">'
            '<div class="field-title">Linguistic & Entity Extraction</div>'
            f'<div>{chips_html}</div>'
            '</div>'
            '</div>'
        )
        st.markdown(panel_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        report_md = generate_markdown_report(result)
        st.download_button(
            label="Download Complete Audit Report (.md)",
            data=report_md,
            file_name=f"{Path(doc_name).stem}_audit.md",
            mime="text/markdown",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
