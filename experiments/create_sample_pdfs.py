"""
Script to generate standard evaluation contracts for live testing & demonstrations:
- sample_nda.pdf (Non-Disclosure Agreement)
- sample_msa.pdf (Master Services Agreement)
- sample_employment.pdf (Employment Agreement with Non-Compete)
"""

import sys
from pathlib import Path
import pymupdf

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.utils.config import SAMPLE_CONTRACTS_DIR

SAMPLE_CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_CONTRACT_TEXTS = {
    "sample_nda.pdf": """NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT

1. Confidential Information.
The Recipient agrees that all technical, commercial, and financial information disclosed by Disclosing Party shall be held in strict confidence. Recipient shall not disclose such information to any third party without prior written authorization.

2. Term and Survival.
The obligations of confidentiality under this Agreement shall survive for a period of three (3) years from the date of disclosure.

3. Termination for Convenience.
Disclosing Party may terminate discussions at its sole discretion upon providing seven (7) days written notice to Recipient.

4. Limitation of Liability.
Neither party shall be liable for indirect, incidental, or special damages arising under this Agreement.""",

    "sample_msa.pdf": """MASTER SERVICES AGREEMENT

SECTION 1. SCOPE OF SERVICES
Provider agrees to use best efforts to promptly perform IT infrastructure and cloud consulting services as detailed in applicable Statements of Work.

SECTION 2. LIMITATION OF LIABILITY
In no event shall either party's cumulative liability under this Agreement exceed the total fees paid in the preceding twelve (12) months, or $100,000, whichever is less.

SECTION 3. INDEMNIFICATION
Provider shall indemnify, defend, and hold harmless Client from and against any third-party claims, liabilities, losses, and damages arising out of Provider's gross negligence or willful misconduct.

SECTION 4. TERMINATION FOR CONVENIENCE
Either party may terminate this Agreement without cause upon giving sixty (60) days advance written notice to the other party.

SECTION 5. TERM AND RENEWAL
This Agreement shall remain in effect for an initial term of two (2) years and will automatically renew for successive one (1) year terms unless either party gives written notice of non-renewal at least 30 days prior to expiration.""",

    "sample_employment.pdf": """EMPLOYMENT AGREEMENT

1. Duties and Standard of Performance.
Employee agrees to devote full business time and best efforts to promote the business and affairs of Employer.

2. Non-Competition Covenant.
During the term of employment and for a period of twelve (12) months following termination, Employee shall not directly or indirectly engage in, manage, or operate any competing business within a 50-mile radius.

3. Termination of Employment.
Employer reserves the right to terminate Employee's employment at will, with or without cause, upon thirty (30) days prior written notice or payment of salary in lieu of notice.

4. Indemnification of Employee.
Employer agrees to indemnify Employee to the maximum extent permitted by law for actions taken within the scope of regular employment duties."""
}

def create_sample_pdfs():
    for fname, text in SAMPLE_CONTRACT_TEXTS.items():
        doc = pymupdf.open()
        page = doc.new_page(width=595, height=842)  # A4 size
        rect = pymupdf.Rect(50, 50, 545, 792)
        page.insert_textbox(rect, text, fontsize=11, fontname="helv")
        output_path = SAMPLE_CONTRACTS_DIR / fname
        doc.save(str(output_path))
        doc.close()
        print(f"Generated sample contract: {output_path}")

if __name__ == "__main__":
    create_sample_pdfs()
