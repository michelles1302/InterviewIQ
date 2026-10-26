import os
import numpy as np
from typing import Tuple, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Global model cache to avoid re-loading outside Streamlit context
_MODEL_CACHE = None

def load_embedding_model():
    """
    Loads sentence-transformers model all-MiniLM-L6-v2 with fallback.
    Caches the model efficiently.
    """
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    try:
        from sentence_transformers import SentenceTransformer
        # Load lightweight CPU model
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        _MODEL_CACHE = model
        return model
    except Exception as e:
        print(f"[Warning] Could not load SentenceTransformer: {e}. Falling back to TF-IDF vectorizer.")
        _MODEL_CACHE = "TFIDF_FALLBACK"
        return _MODEL_CACHE

# Streamlit-cached wrapper
try:
    import streamlit as st
    @st.cache_resource(show_spinner="Loading NLP Semantic Model (all-MiniLM-L6-v2)...")
    def get_cached_model():
        return load_embedding_model()
except ImportError:
    def get_cached_model():
        return load_embedding_model()


def compute_semantic_similarity(text1: str, text2: str) -> float:
    """
    Computes cosine similarity between two text strings (0.0 to 1.0).
    Uses SentenceTransformer embeddings when available, fallback to TF-IDF otherwise.
    """
    if not text1.strip() or not text2.strip():
        return 0.0

    model = get_cached_model()

    if model != "TFIDF_FALLBACK" and hasattr(model, 'encode'):
        try:
            # Encode texts into 384-dim dense vectors
            embeddings = model.encode([text1, text2], convert_to_numpy=True)
            emb1 = embeddings[0].reshape(1, -1)
            emb2 = embeddings[1].reshape(1, -1)
            sim = float(cosine_similarity(emb1, emb2)[0][0])
            # Ensure similarity is bounded [0, 1]
            return float(np.clip(sim, 0.0, 1.0))
        except Exception as e:
            print(f"[Warning] Embedding encode failed: {e}. Using TF-IDF fallback.")

    # Fallback TF-IDF cosine similarity
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform([text1, text2])
        sim = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
        return float(np.clip(sim, 0.0, 1.0))
    except Exception:
        return 0.0
