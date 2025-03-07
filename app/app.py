import streamlit as st
from analyze import analyze_document

st.title("PDF/JPG Document Analyzer")

uploaded_file = st.file_uploader("Upload your PDF/JPG file", type=["pdf", "jpg", "jpeg"])

if uploaded_file:
    file_bytes = uploaded_file.getvalue()

    # Directly analyze file without saving
    structured_data = analyze_document(file_bytes=file_bytes)

    st.json(structured_data)