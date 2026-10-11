"""
Report Service Module.
Generates structured Markdown and JSON audit reports from contract analysis results.
"""

from typing import Dict, Any

def generate_markdown_report(analysis_result: Dict[str, Any]) -> str:
    """
    Constructs an executive legal review report in Markdown format.
    """
    fn = analysis_result.get("filename", "Contract")
    overall = analysis_result.get("overall_contract_risk", "UNKNOWN")
    counts = analysis_result.get("risk_counts", {})
    t_sec = analysis_result.get("analysis_time_seconds", 0)
    clauses = analysis_result.get("clauses", [])

    lines = [
        f"# 🛡️ Contract Intelligence & Risk Audit Report",
        f"**Document:** `{fn}` | **Total Clauses Analyzed:** {len(clauses)} | **Latency:** {t_sec}s",
        f"**Overall Assessment:** **{overall}**",
        "",
        "## 📊 Risk Overview",
        f"- 🔴 **High Risk Clauses:** {counts.get('high_risk', 0)}",
        f"- 🟡 **Needs Review Clauses:** {counts.get('needs_review', 0)}",
        f"- 🟢 **Informational Clauses:** {counts.get('informational', 0)}",
        "",
        "---",
        "## 🔍 Detailed Clause Breakdown",
        ""
    ]

    for cl in clauses:
        risk_emoji = "🔴" if cl["risk_level"] == "High Risk" else ("🟡" if cl["risk_level"] == "Needs Review" else "🟢")
        lines.append(f"### {risk_emoji} [{cl['clause_id']}] {cl['predicted_category']} (Page {cl['page_number']})")
        lines.append(f"> \"{cl['clause_text']}\"")
        lines.append("")
        lines.append(f"- **Risk Level:** **{cl['risk_level']}** (Confidence: {cl['confidence'] * 100:.1f}%)")
        lines.append(f"- **Rationale:** {cl['explanation']['summary']}")
        lines.append(f"- **Action:** *{cl['explanation']['recommendation']}*")
        
        entities = cl.get("extracted_entities", {})
        if entities.get("amounts"):
            lines.append(f"- **Financial Figures:** `{', '.join(entities['amounts'])}`")
        if entities.get("deadlines"):
            lines.append(f"- **Notice Periods / Deadlines:** `{', '.join(entities['deadlines'])}`")
        if entities.get("parties"):
            lines.append(f"- **Identified Parties:** `{', '.join(entities['parties'])}`")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("*Disclaimer: This automated assessment flags clauses for human legal review and does not constitute formal legal counsel.*")
    return "\n".join(lines)
