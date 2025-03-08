import os
import sys
import pytest

# Ensure backend directory is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from create_embeddings import create_and_save_embeddings, DATA_DIR

def test_create_embeddings():
    # Temporarily change working directory to backend
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    original_dir = os.getcwd()
    os.chdir(backend_dir)

    try:
        create_and_save_embeddings()
        embeddings_file_path = os.path.join(os.getcwd(), 'knowledge_base_embeddings.pkl')

        assert os.path.exists(embeddings_file_path), "Embeddings file not created successfully."
    finally:
        os.chdir(original_dir)