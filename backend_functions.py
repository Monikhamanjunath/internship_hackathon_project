import PyPDF2
from transformers import pipeline
from googletrans import Translator
from fpdf import FPDF
import os

# -----------------------
# PDF Text Extraction
# -----------------------
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# -----------------------
# Text Summarization
# -----------------------
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
def summarize_text(text):
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summary = ""
    for chunk in chunks:
        summary += summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
    return summary

# -----------------------
# Clause Detection & Risk Tags
# -----------------------
def detect_clauses(text):
    standard_clauses = [
        "Termination", "Governing Law", "Confidentiality",
        "Indemnity", "Dispute Resolution", "Force Majeure", "Payment Terms"
    ]
    found = [clause for clause in standard_clauses if clause.lower() in text.lower()]
    missing = [clause for clause in standard_clauses if clause not in found]

    risk_tags = {}
    for clause in found:
        if clause in ["Termination", "Confidentiality"]:
            risk_tags[clause] = "🟡 Present but Weak"
        else:
            risk_tags[clause] = "🟢 Strong"
    for clause in missing:
        risk_tags[clause] = "🔴 Missing"

    return found, missing, risk_tags

# -----------------------
# Translation Support
# -----------------------
def translate_text(text, target_lang_code):
    translator = Translator()
    translated = translator.translate(text, dest=target_lang_code)
    return translated.text

# -----------------------
# Clause Suggestions
# -----------------------
def suggest_clauses(missing):
    suggestions = []
    if "Indemnity" in missing:
        suggestions.append("💡 **Suggested Indemnity Clause:** Each party agrees to indemnify and hold the other harmless from any liability...")
    if "Dispute Resolution" in missing:
        suggestions.append("💡 **Suggested Dispute Resolution Clause:** All disputes shall be resolved via arbitration in accordance with Indian laws...")
    return suggestions

# -----------------------
# Download PDF
# -----------------------
def download_summary_as_pdf(summary, missing_clauses):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, "JuriScan Summary Report\n", align="C")
    pdf.ln()
    pdf.multi_cell(0, 10, "📄 Summary:\n" + summary)
    pdf.ln()
    pdf.multi_cell(0, 10, "⚠️ Missing Clauses:\n" + ", ".join(missing_clauses))

    output_path = "JuriScan_Report.pdf"
    pdf.output(output_path)
    return output_path
