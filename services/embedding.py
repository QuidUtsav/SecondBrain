# services/embedding.py

from sentence_transformers import SentenceTransformer
import numpy as np

_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> list[float]:
    """
    Encodes text into a 384-dim embedding vector.
    Returns a plain Python list (pgvector/SQLAlchemy expects list, not np.ndarray).
    """
    embedding = _model.encode(text)
    return embedding.tolist()