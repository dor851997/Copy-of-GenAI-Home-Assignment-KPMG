import os
import json
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# Retrieve credentials from .env file
ENDPOINT_OCR = os.getenv("AZURE_OCR_AI_SERVICES_URL")
API_KEY_OCR = os.getenv("AZURE_OCR_AI_SERVICES_KEY")

ENDPOINT_OPENAI = os.getenv("AZURE_OPENAI_SERVICES_URL")
API_KEY_OPENAI = os.getenv("AZURE_OPENAI_SERVICES_KEY")


print("Endpoint:", ENDPOINT_OCR)
print("API Key:", "Present" if API_KEY_OPENAI else "Not Found")  # Mask actual key for security

# Initialize Document Analysis Client
client = DocumentAnalysisClient(endpoint=ENDPOINT_OCR, credential=AzureKeyCredential(API_KEY_OCR))

# Initialize Azure OpenAI Client
openai_client = AzureOpenAI(
    api_key=API_KEY_OPENAI,
    azure_endpoint=ENDPOINT_OPENAI,
    api_version="2024-02-01"
)

import re

def extract_fields_with_openai(extracted_text):
    prompt = f"""
    Extract structured key-value pairs from the following text and output as JSON.

    {extracted_text}

    Only output valid JSON. Do not include explanations or additional text.
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    # Remove Markdown code fences if present
    content = re.sub(r'^```json\n?|```$', '', content, flags=re.MULTILINE).strip()

    try:
        structured_data = json.loads(content)
    except json.JSONDecodeError:
        print("⚠️ Warning: Received invalid JSON from OpenAI:")
        print(content)
        structured_data = {"error": "Invalid JSON", "raw_response": content}

    return structured_data


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

    # Combine extracted text into a single string
    extracted_text = " ".join(word["text"] for page in extracted_data["pages"] for word in page["words"])

    # Extract structured fields using Azure OpenAI
    structured_data = extract_fields_with_openai(extracted_text)

    # Save structured data to JSON file
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    output_path_structured = os.path.join(output_folder, os.path.basename(file_path) + "_structured.json")
    with open(output_path_structured, "w", encoding="utf-8") as structured_file:
        json.dump(structured_data, structured_file, ensure_ascii=False, indent=4)

    print(f"Structured data extraction completed! Results saved to: {output_path_structured}")

    # Save to JSON file

    output_path = os.path.join(output_folder, os.path.basename(file_path) + ".json")