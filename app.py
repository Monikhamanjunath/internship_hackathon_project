import streamlit as st
from backend_functions import (
    extract_text_from_pdf,
    summarize_text,
    detect_clauses,
    translate_text,
    suggest_clauses,
    download_summary_as_pdf
)

st.set_page_config(page_title="JuriScan – AI Legal Assistant", page_icon="⚖️", layout="centered")

# Logo and Heading
st.image("your_logo.png", width=120)
st.markdown("<h1 style='text-align: center;'>JuriScan – Smart Legal Document Inspector</h1>", unsafe_allow_html=True)
st.markdown("---")

# Upload multiple PDFs
uploaded_files = st.file_uploader("📄 Upload one or more legal PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    for i, file in enumerate(uploaded_files):
        st.divider()
        st.header(f"📘 Document: {file.name}")

        # Extract and display
        text = extract_text_from_pdf(file)
        st.subheader("📃 Extracted Text")
        st.text_area("Extracted Legal Text", text[:3000], height=250, disabled=True)

        # Summary
        summary = summarize_text(text)
        st.subheader("✂️ Summary")
        st.write(summary)

        # Clause Detection
        found, missing, risk_tags = detect_clauses(text)
        st.subheader("🧩 Clause Detection with Risk Tags")
        for clause in found + missing:
            st.markdown(f"**{clause}**: {risk_tags.get(clause, '⚪ Unknown')}")

        # Tooltip Expander Example
        with st.expander("ℹ️ What is a Termination Clause?"):
            st.write("A termination clause allows either party to exit the agreement under certain conditions.")

        # Search for Clause
        search = st.text_input(f"🔍 Search clause in {file.name}", key=f"search-{i}")
        if search:
            found_in_text = search.lower() in text.lower()
            st.write(f"✅ Clause '{search}' found." if found_in_text else f"❌ Clause '{search}' not found.")

        # Suggestions
        st.subheader("💡 Suggestions")
        suggestions = suggest_clauses(missing)
        for tip in suggestions:
            st.info(tip)

        # Translation
        st.subheader("🌐 Translate Summary")
        language = st.selectbox("Choose Language", ["English", "Hindi", "Tamil", "Telugu", "Kannada", "Marathi", "Bengali", "Gujarati"], key=f"lang-{i}")
        if language != "English":
            lang_code = {
                "Hindi": "hi", "Tamil": "ta", "Telugu": "te",
                "Kannada": "kn", "Marathi": "mr", "Bengali": "bn", "Gujarati": "gu"
            }
            translated = translate_text(summary, lang_code[language])
            st.text_area(f"{language} Translation", translated, height=200, disabled=True)

        # Download PDF Button
        if st.button("📥 Download Report", key=f"download-{i}"):
            pdf_path = download_summary_as_pdf(summary, missing)
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Click to Download PDF", f, file_name="JuriScan_Report.pdf", mime="application/pdf")

