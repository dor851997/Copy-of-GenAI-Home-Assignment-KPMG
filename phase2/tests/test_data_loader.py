import os
import sys
import pytest

# Ensure backend directory is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from data_loader import load_embeddings_from_pickle

def test_load_embeddings_from_pickle():
    test_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'backend', 'knowledge_base_embeddings.pkl')
    )
    assert os.path.exists(test_file_path), f"File {test_file_path} does not exist."

    index, texts = load_embeddings_from_pickle(test_file_path)

    assert index is not None, "FAISS index was not created."
    assert texts is not None, "Texts are not loaded."
    assert len(texts) > 0, "Texts loaded are empty."