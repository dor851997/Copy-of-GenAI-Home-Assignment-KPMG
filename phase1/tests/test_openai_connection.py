# tests/test_openai_connection.py
import pytest
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # If you store keys in a .env file

def test_openai_connection():
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_SERVICES_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_SERVICES_URL"),
        api_version="2024-02-01"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "Hello, OpenAI!"}
            ],
            max_tokens=10
        )
        assert response is not None
        assert len(response.choices) > 0
        assert response.choices[0].message.content.strip() != ""
    except Exception as e:
        pytest.fail(f"OpenAI API connection failed: {e}")