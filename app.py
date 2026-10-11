"""
ClauseGuard AI: Streamlit Entry Point and Upload Interface
Academic Activity Tracker (AAT) - Natural Language Processing for LLM (24AM7PCLLM)
"""

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="ClauseGuard AI — Contract Intelligence & Risk Analysis",
    page_icon="🛡️",
    layout="wide"
)

def main():
    st.title("🛡️ ClauseGuard AI")
    st.subheader("NLP-Powered Contract Analysis & Risk Review System")
    st.markdown(
        """
        *Upload a contract (PDF) to segment clauses, detect risk indicators, extract obligations/dates/amounts, and inspect linguistic patterns.*
        """
    )
    
    st.info("System initialized. Upload a contract PDF in the sidebar or select a pre-loaded sample contract.")

    with st.sidebar:
        st.header("📄 Contract Upload")
        uploaded_file = st.file_uploader("Upload Contract PDF", type=["pdf"])
        sample_choice = st.selectbox(
            "Or select sample contract",
            ["None", "Non-Disclosure Agreement (NDA)", "Master Services Agreement (MSA)", "Employment Contract"]
        )

if __name__ == "__main__":
    main()
