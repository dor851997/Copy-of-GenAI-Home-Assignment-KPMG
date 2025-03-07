import streamlit as st
from analyze import analyze_document

st.title("Document Analysis and Extraction")

uploaded_file = st.file_uploader("Upload your document", type=["pdf", "png", "jpg"])

if uploaded_file:
    with st.spinner("Analyzing document..."):
        structured_data = analyze_document(uploaded_file.getvalue())

    validation = structured_data.pop("validation", {})
    if validation.get("is_complete"):
        st.success(f"Extraction complete! Accuracy Score: {validation['accuracy_score']*100}%")
    else:
        st.warning(
            f"Missing or incomplete fields: {', '.join(validation.get('missing_fields', []))}. "
            f"Accuracy Score: {validation['accuracy_score']*100}%"
        )
    st.json(structured_data, expanded=False)