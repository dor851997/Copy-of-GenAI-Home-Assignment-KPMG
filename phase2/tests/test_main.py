import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Change the working directory to backend
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_chat_endpoint(client):
    payload = {
        "user_info": {
            "first_name": "Test",
            "last_name": "User",
            "id_number": "123456789",
            "gender": "male",
            "age": 30,
            "hmo_name": "מכבי",
            "hmo_card_number": "123456789",
            "insurance_membership": "זהב"
        },
        "history": [],
        "question": "מה ההנחות שיש לי על יישור שיניים?"
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    assert "response" in response.json()

