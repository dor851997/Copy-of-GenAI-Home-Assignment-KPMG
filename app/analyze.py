import os
import json
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

# Retrieve credentials from .env file
ENDPOINT = os.getenv("AZURE_AI_SERVICES_URL")
API_KEY = os.getenv("AZURE_AI_SERVICES_KEY")

print("Endpoint:", ENDPOINT)
print("API Key:", "Present" if API_KEY else "Not Found")  # Mask actual key for security

# Initialize Document Analysis Client
client = DocumentAnalysisClient(endpoint=ENDPOINT, credential=AzureKeyCredential(API_KEY))

def analyze_document(file_path):
    """
    Analyzes a document (PDF, JPG, PNG) using Azure Document Intelligence.

    Args:
        file_path (str): Path to the document file.

    Returns:
        dict: Extracted text and data.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "rb") as document:
        poller = client.begin_analyze_document("prebuilt-document", document)
        result = poller.result()

    extracted_data = {"pages": []}

    for page in result.pages:
        page_data = {"page_number": page.page_number, "words": []}
        for word in page.words:
            page_data["words"].append({"text": word.content, "confidence": word.confidence})
        extracted_data["pages"].append(page_data)

    # Save to JSON file
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, os.path.basename(file_path) + ".json")
    
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)

    print(f"✅ Document analysis completed! Results saved to: {output_path}")
    return extracted_data
