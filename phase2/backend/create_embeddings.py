"""
Script: create_embeddings.py

Purpose:
This script generates embeddings for text extracted from HTML files located in the specified `DATA_DIR`. It uses the Azure OpenAI embedding model (text-embedding-ada-002) to convert text sections into vector representations suitable for similarity search or retrieval tasks. These embeddings are stored persistently in a pickle file (`knowledge_base_embeddings.pkl`), enabling efficient retrieval of relevant content during runtime.

Functionality:
- Iterates over all `.html` files within the `DATA_DIR` directory.
- Parses each HTML file and extracts text sections using BeautifulSoup.
- Generates embeddings for each text section using the Azure OpenAI embedding model.
- Saves the generated embeddings along with their corresponding texts to `knowledge_base_embeddings.pkl`.

Running the script again will overwrite the existing embeddings file.

Dependencies:
- Azure OpenAI Python SDK
- BeautifulSoup
- Python-dotenv (for environment variable management)

Make sure the `.env` file includes correct Azure OpenAI credentials:
- AZURE_OPENAI_SERVICES_KEY
- AZURE_OPENAI_SERVICES_URL
"""

import os
import logging
import pickle
from bs4 import BeautifulSoup
import numpy as np
import faiss
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()
logging.basicConfig(level=logging.INFO)

DATA_DIR = "../phase2_data"
EMBEDDINGS_FILE = "knowledge_base_embeddings.pkl"

openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_SERVICES_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_SERVICES_URL"),
    api_version="2024-02-01"
)

def get_embedding(text):
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def create_and_save_embeddings():
    logging.info("Starting embeddings creation from HTML files...")
    knowledge_base_embeddings = []
    knowledge_base_texts = []

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".html"):
            logging.info(f"Processing file: {filename}")
            with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
                sections = soup.get_text(separator="\n").split("\n\n")
                for section in sections:
                    cleaned_section = section.strip()
                    if cleaned_section:
                        embedding = openai_client.embeddings.create(
                            model="text-embedding-ada-002",
                            input=cleaned_section
                        ).data[0].embedding
                        knowledge_base_embeddings.append(embedding)
                        knowledge_base_texts.append(cleaned_section)
            logging.info(f"Processed {filename}, extracted {len(knowledge_base_texts)} sections.")

    # Save embeddings
    with open(EMBEDDINGS_FILE, "wb") as f:
        pickle.dump((knowledge_base_embeddings, knowledge_base_texts), f)

    logging.info(f"Saved {len(knowledge_base_texts)} embeddings successfully.")

# Run this function separately to build embeddings once
if __name__ == "__main__":
    create_and_save_embeddings()