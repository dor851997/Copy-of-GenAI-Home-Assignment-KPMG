import os
import json
from dotenv import load_dotenv
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from openai import AsyncAzureOpenAI
import logging
import re
import asyncio
from celery import Celery

# Load environment variables
load_dotenv()

# Retrieve credentials from .env file
ENDPOINT_OCR = os.getenv("AZURE_OCR_AI_SERVICES_URL")
API_KEY_OCR = os.getenv("AZURE_OCR_AI_SERVICES_KEY")

ENDPOINT_OPENAI = os.getenv("AZURE_OPENAI_SERVICES_URL")
API_KEY_OPENAI = os.getenv("AZURE_OPENAI_SERVICES_KEY")

# Celery configuration
celery_app = Celery('document_analysis', broker='redis://localhost:6379/0',backend='redis://localhost:6379/0'
)
celery_app.conf.broker_connection_retry_on_startup = True

# Initialize Document Analysis Client
client = DocumentAnalysisClient(endpoint=ENDPOINT_OCR, credential=AzureKeyCredential(API_KEY_OCR))

# Initialize Azure OpenAI Client
openai_client = AsyncAzureOpenAI(
    api_key=API_KEY_OPENAI,
    azure_endpoint=ENDPOINT_OPENAI,
    api_version="2024-02-01"
)

async def detect_language(text):
    """
    Detects the primary language of the provided text using Azure OpenAI.

    Args:
        text (str): The text whose language is to be detected.

    Returns:
        str: Detected language ('Hebrew' or 'English'). Defaults to 'English' if detection is ambiguous.
    """

    prompt = f"""
    Detect the primary language of the following text. 
    Respond with only "Hebrew" or "English".

    Text:
    {text}
    """

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=5,
        temperature=0
    )

    language = response.choices[0].message.content.strip()
    return language if language in ["Hebrew", "English"] else "English"

async def extract_fields_with_openai(extracted_text):
    """
    Uses Azure OpenAI to extract structured information from raw extracted text based on a predefined JSON schema.

    Args:
        extracted_text (str): The raw text extracted from the document.

    Returns:
        dict: Structured JSON matching the provided schema or an error message if parsing fails.
    """
    
    language = await detect_language(extracted_text)

    if language == "Hebrew":
        json_structure = {
            "שם משפחה": "",
            "שם פרטי": "",
            "מספר זהות": "",
            "מין": "",
            "תאריך לידה": {"יום": "", "חודש": "", "שנה": ""},
            "כתובת": {
                "רחוב": "",
                "מספר בית": "",
                "כניסה": "",
                "דירה": "",
                "עיר": "",
                "מיקוד": "",
                "תא דואר": ""
            },
            "טלפון קווי": "",
            "טלפון נייד": "",
            "סוג העבודה": "",
            "תאריך הפגיעה": {"יום": "", "חודש": "", "שנה": ""},
            "שעת הפגיעה": "",
            "מיקום התאונה": "",
            "תיאור התאונה": "",
            "האיבר שנפגע": "",
            "חתימה": "",
            "תאריך מילוי הטופס": {"יום": "", "חודש": "", "שנה": ""},
            "תאריך קבלת הטופס בקופה": {"יום": "", "חודש": "", "שנה": ""},
            "למילוי ע\"י המוסד הרפואי": {
                "חבר בקופת חולים": "",
                "מהות התאונה": "",
                "אבחנות רפואיות": ""
            }
        }
    else:
        json_structure = {
            "lastName": "",
            "firstName": "",
            "idNumber": "",
            "gender": "",
            "dateOfBirth": {
                "day": "",
                "month": "",
                "year": ""
            },
            "address": {
                "street": "",
                "houseNumber": "",
                "entrance": "",
                "apartment": "",
                "city": "",
                "postalCode": "",
                "poBox": ""
            },
            "landlinePhone": "",
            "mobilePhone": "",
            "jobType": "",
            "dateOfInjury": {
                "day": "",
                "month": "",
                "year": ""
            },
            "timeOfInjury": "",
            "accidentLocation": "",
            "accidentAddress": "",
            "accidentDescription": "",
            "injuredBodyPart": "",
            "signature": "",
            "formFillingDate": {
                "day": "",
                "month": "",
                "year": ""
            },
            "formReceiptDateAtClinic": {
                "day": "",
                "month": "",
                "year": ""
            },
            "medicalInstitutionFields": {
                "healthFundMember": "",
                "natureOfAccident": "",
                "medicalDiagnoses": ""
            }
        }

    prompt = f"""
    Extract the following information strictly into this JSON structure.  
    Respond with ONLY valid JSON matching exactly this schema—no additional text, explanations, or markdown formatting:

    {json.dumps(json_structure, ensure_ascii=False, indent=2)}

    Text to extract from:
    {extracted_text}
    """

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    def extract_json_from_response(text):
        """
        Attempts to robustly extract and parse JSON from OpenAI response, handling extraneous text or markdown fences gracefully.

        Args:
            text (str): The raw response text from OpenAI.

        Returns:
            dict or None: Parsed JSON dictionary or None if parsing fails.
        """
        try:
            json_match = re.search(r'```json(.*?)```', text, re.DOTALL)
            if json_match:
                json_content = json_match.group(1).strip()
                return json.loads(json_content)
            else:
                json_match = re.search(r'({.*})', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1).strip())
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing error: {e}")
        return None

    structured_json = extract_json_from_response(content)

    if structured_json is None:
        structured_json = {"error": "Invalid JSON", "raw_response": content}

    return structured_json

async def analyze_document(file_bytes):
    """
    Analyzes an uploaded document by performing OCR and structured data extraction via Azure OpenAI.

    Args:
        file_bytes (bytes): Byte content of the uploaded document.

    Returns:
        dict: Extracted structured data along with validation results, including accuracy scores and missing fields.
    """
    
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting document analysis.")
    
    poller = client.begin_analyze_document("prebuilt-document", file_bytes)
    result = poller.result()

    extracted_data = {"pages": []}

    for page in result.pages:
        page_data = {"page_number": page.page_number, "words": []}
        for word in page.words:
            page_data["words"].append({"text": word.content, "confidence": word.confidence})
        extracted_data["pages"].append(page_data)

    logging.info(f"Extracted {sum(len(page['words']) for page in extracted_data['pages'])} words from document.")
    
    # Combine extracted text into a single string
    extracted_text = " ".join(word["text"] for page in extracted_data["pages"] for word in page["words"])

    logging.info("Sending extracted text to OpenAI for field extraction.")
    
    # Extract structured fields using Azure OpenAI
    structured_data = await extract_fields_with_openai(extracted_text)

    logging.info("Successfully received structured data from OpenAI.")

    ocr_confidence_data = [word["confidence"] for page in extracted_data["pages"] for word in page["words"]]
    validation_result = validate_extracted_data(structured_data, ocr_confidence_data)

    if validation_result["is_complete"]:
        logging.info(f"Extracted data is complete with accuracy score: {validation_result['accuracy_score']}")
    else:
        logging.warning(
            f"Extracted data incomplete. Missing fields: {validation_result['missing_fields']}, "
            f"Accuracy score: {validation_result['accuracy_score']}"
        )
    structured_data["validation"] = validation_result
    
    return structured_data

def validate_extracted_data(extracted_json, ocr_confidence_data, required_fields=None):
    """
    Validates the completeness and accuracy of extracted JSON data based on OCR confidence levels.

    Args:
        extracted_json (dict): JSON data extracted from the document.
        ocr_confidence_data (list): List of OCR confidence scores.
        required_fields (list, optional): List of fields required for completeness validation. Defaults to all fields in extracted_json.

    Returns:
        dict: Validation result including completeness status, missing fields, and overall accuracy score.
    """

    if required_fields is None:
        required_fields = list(extracted_json.keys())

    missing_fields = []

    for field in required_fields:
        if isinstance(extracted_json.get(field, ""), dict):
            if not all(extracted_json[field].values()):
                missing_fields.append(field)
        elif not extracted_json.get(field):
            missing_fields.append(field)

    is_complete = len(missing_fields) == 0

    avg_confidence = sum(ocr_confidence_data) / len(ocr_confidence_data) if ocr_confidence_data else 0

    validation_result = {
        "is_complete": is_complete,
        "missing_fields": missing_fields,
        "accuracy_score": round(avg_confidence, 2)
    }

    return validation_result

@celery_app.task(name="analyze_document_task")
def analyze_document_task(file_bytes):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(analyze_document(file_bytes))
    return result