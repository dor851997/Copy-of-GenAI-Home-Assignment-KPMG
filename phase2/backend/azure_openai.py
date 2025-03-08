from openai import AzureOpenAI
import os
import logging
from dotenv import load_dotenv
import numpy as np

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_SERVICES_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_SERVICES_URL"),
    api_version="2024-02-01"
)

# Load the knowledge base at startup
from data_loader import load_embeddings_from_pickle
index, knowledge_base_texts = load_embeddings_from_pickle()

async def select_relevant_content(question: str, top_k=50):
    question_embedding_response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=question
    )

    question_embedding = np.array(question_embedding_response.data[0].embedding).reshape(1, -1)

    distances, indices = index.search(question_embedding, top_k)
    relevant_sections = [knowledge_base_texts[i] for i in indices[0]]

    return "\n\n".join(relevant_sections)

async def get_answer_from_openai(question: str, user_info: dict, history: list) -> str:
    relevant_knowledge = await select_relevant_content(question)

    prompt = f"""
    You're an assistant specialized in medical services for Israeli HMOs and your name is 'Medical Assitant'. 
    Use the following Knowledge Base to answer clearly and accurately:

    Knowledge Base:
    {relevant_knowledge}

    User Information: 
    {user_info}
    
    Conversation history:
    {history}

    Question:
    {question}

    Provide a detailed, accurate response based on the knowledge base.
    """

    logger.info(f"Sending prompt to OpenAI: {prompt[:500]}...")

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1000
    )

    answer = response.choices[0].message.content.strip()
    logger.info(f"Received response from OpenAI: {response.choices[0].message.content[:500]}...")

    return answer