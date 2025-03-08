from openai import AzureOpenAI
import os
import logging
from dotenv import load_dotenv
from data_loader import load_html_knowledge_base


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_SERVICES_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_SERVICES_URL"),
    api_version="2024-02-01"
)

# Load the knowledge base at startup
knowledge_base = load_html_knowledge_base()

async def get_answer_from_openai(question: str, user_info: dict, history: list) -> str:
    prompt = f"""
    You're an assistant specialized in medical services for Israeli HMOs. 
    Use the following Knowledge Base to answer clearly and accurately:

    Knowledge Base:
    {knowledge_base[:20000]}  # Limit context if needed

    User Information: 
    {user_info}
    
    Conversation history:
    {history}

    Question:
    {question}

    Provide a detailed, accurate response based on the knowledge base.
    """

    logger.info(f"Sending prompt to OpenAI: {prompt[:500]}...")  # Log initial part of the prompt for brevity

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1000
    )

    answer = response.choices[0].message.content.strip()
    logger.info(f"Received response from OpenAI: {response.choices[0].message.content[:500]}...")

    return response.choices[0].message.content.strip()