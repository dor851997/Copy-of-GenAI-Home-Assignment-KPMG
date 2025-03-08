from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_SERVICES_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_SERVICES_URL"),
    api_version="2024-02-01"
)

async def get_answer_from_openai(question: str, user_info: dict, history: list) -> str:
    prompt = f"""
    You're an assistant specialized in medical services for Israeli HMOs.
    
    User Info:
    {user_info}

    Conversation history:
    {history}

    Question:
    {question}

    Answer the question clearly based on the user info and previous history.
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=800
    )

    return response.choices[0].message.content.strip()