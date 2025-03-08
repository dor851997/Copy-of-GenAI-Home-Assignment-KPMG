import os
import pytest
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

@pytest.fixture
def azure_ocr_client():
    endpoint = os.getenv("AZURE_OCR_AI_SERVICES_URL")
    api_key = os.getenv("AZURE_OCR_AI_SERVICES_KEY")
    return DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

def test_azure_ocr_connection(azure_ocr_client):
    # Corrected file path (relative to current phase1 directory)
    local_file_path = "phase1_data/283_raw.pdf"
    try:
        with open(local_file_path, "rb") as fd:
            poller = azure_ocr_client.begin_analyze_document("prebuilt-layout", fd)
            result = poller.result()

        assert result is not None
        assert len(result.pages) > 0
        assert len(result.pages[0].lines) > 0

    except Exception as e:
        pytest.fail(f"Azure OCR API connection failed: {e}")