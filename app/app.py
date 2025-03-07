import streamlit as st
from analyze import analyze_document

st.title("Document Analysis and Extraction")

uploaded_file = st.file_uploader("Upload your document", type=["pdf", "png", "jpg"])

if uploaded_file:
    with st.spinner("Analyzing document..."):
        structured_data = analyze_document(uploaded_file.getvalue())

    validation = structured_data.pop("validation", {})
    if validation.get("is_complete"):
        st.success("All required fields extracted successfully!")
    else:
        st.warning(f"Missing or incomplete fields detected: {', '.join(validation.get('missing_fields', []))}")

    st.json(structured_data, expanded=False)