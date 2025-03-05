import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Azure API credentials
endpoint = os.getenv("AZURE_AI_SERVICES_URL")
api_key = os.getenv("AZURE_AI_SERVICES_KEY")

# Ensure endpoint is formatted correctly
if not endpoint.endswith("/"):
    endpoint += "/"

# Correct API URL for Document Intelligence
api_url = f"{endpoint}formrecognizer/documentModels/prebuilt-document:analyze?api-version=2023-07-31"

headers = {
    "Ocp-Apim-Subscription-Key": api_key,
    "Content-Type": "application/json"
}

# Test request with a sample PDF file from the web
test_payload = {
    "urlSource": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
}

response = requests.post(api_url, headers=headers, json=test_payload)

print("Status Code:", response.status_code)
print("Response:", response.json())  # Parse JSON response for debugging
