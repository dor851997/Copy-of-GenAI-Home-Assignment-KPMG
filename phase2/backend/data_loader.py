import pickle
import faiss
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

def load_embeddings_from_pickle(file_path="knowledge_base_embeddings.pkl"):
    """
    Loads pre-generated embeddings from a pickle file and initializes a FAISS vector index.

    Args:
        file_path (str): Path to the pickle file with embeddings.

    Returns:
        index (faiss.IndexFlatL2): FAISS index for efficient vector searches.
        texts (list): Corresponding text segments for embeddings.
    """
    logging.info(f"Loading embeddings from {file_path}...")
    with open(file_path, "rb") as file:
        embeddings, texts = pickle.load(file)
    
    embeddings_array = np.array(embeddings).astype('float32')
    index = faiss.IndexFlatL2(embeddings_array.shape[1])
    index.add(embeddings_array)

    logging.info(f"Loaded {len(texts)} embeddings into FAISS index.")
    return index, texts

# Load embeddings only once at startup
index, knowledge_base_texts = load_embeddings_from_pickle("knowledge_base_embeddings.pkl")

def find_relevant_sections(query, embedding_function, top_k=5):
    """
    Finds relevant sections from the knowledge base for a given user query.

    Parameters:
        query (str): User query text.
        embedding_function (callable): Function that creates embeddings for the query.
        top_k (int): Number of top relevant sections to return.

    Returns:
        list[str]: Most relevant knowledge base sections.
    """
    logging.info("Generating embedding for user query...")
    query_embedding = np.array([embedding_function(query)]).astype('float32')
    distances, indices = index.search(query_embedding, top_k)
    relevant_texts = [knowledge_base_texts[i] for i in indices[0]]
    logging.info(f"Found {len(relevant_texts)} relevant sections.")
    return relevant_texts