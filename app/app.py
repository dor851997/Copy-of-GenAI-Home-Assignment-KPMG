"""
Streamlit application for uploading documents and asynchronously analyzing their content using OCR and structured data extraction through Celery and Azure OpenAI.

The app allows users to upload documents (PDF, PNG, JPG), processes these documents asynchronously, and presents structured extracted data along with accuracy and completeness validation.

Dependencies:
    - Streamlit: Frontend interface for document upload and result display.
    - Celery: Task queue for asynchronous document analysis.
    - Redis: Message broker and backend for Celery.

Usage:
    Run the Streamlit app and upload supported file types (PDF, PNG, JPG). The app asynchronously processes uploaded files, displaying extraction results and validation scores upon completion.
"""

import streamlit as st
from analyze import analyze_document_task
import time

st.title("Document Analysis and Extraction")

uploaded_file = st.file_uploader("Upload your document", type=["pdf", "png", "jpg"])

if uploaded_file:
    with st.spinner("Analyzing document..."):
        task = analyze_document_task.delay(uploaded_file.getvalue())

        while not task.ready():
            time.sleep(1)

        if task.successful():
            structured_data = task.result
            validation = structured_data.pop("validation", {})
        else:
            st.error(f"Task failed: {task.result}")
            structured_data = {}
            validation = {}

    if validation.get("is_complete"):
        st.success(f"Extraction complete! Accuracy Score: {validation['accuracy_score']*100}%")
    else:
        st.warning(
            f"Missing or incomplete fields: {', '.join(validation.get('missing_fields', []))}. "
            f"Accuracy Score: {validation['accuracy_score']*100}%"
        )
    st.json(structured_data, expanded=False)