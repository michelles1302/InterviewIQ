from typing import Dict, Any, List
import re
from analyzer.embeddings import compute_semantic_similarity

def analyze_relevance(question: str, answer: str) -> Dict[str, Any]:
    """
    Analyzes semantic relevance between interview question and answer.
    Returns relevance score (0-100), raw cosine similarity, explanation, and off-topic sentence flags.
    """
    if not answer.strip():
        return {
            "score": 0.0,
            "raw_similarity": 0.0,
            "explanation": "No answer provided.",
            "off_topic_sentences": []
        }

    # Compute overall cosine similarity
    raw_sim = compute_semantic_similarity(question, answer)

    # Calibrate cosine similarity (MiniLM cosine similarity for relevant answers usually ranges between 0.25 and 0.85)
    # Cosine <= 0.15 -> score ~ 0-20
    # Cosine = 0.40 -> score ~ 60
    # Cosine >= 0.70 -> score ~ 95-100
    if raw_sim <= 0.10:
        score = max(0.0, raw_sim * 200)  # 0 to 20
    elif raw_sim <= 0.35:
        score = 20.0 + ((raw_sim - 0.10) / 0.25) * 35.0  # 20 to 55
    elif raw_sim <= 0.65:
        score = 55.0 + ((raw_sim - 0.35) / 0.30) * 35.0  # 55 to 90
    else:
        score = 90.0 + ((raw_sim - 0.65) / 0.35) * 10.0  # 90 to 100

    score = round(float(min(100.0, max(0.0, score))), 1)

    # Sentence-level drift detection
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', answer) if len(s.strip()) > 10]
    off_topic_sentences = []
    
    if len(sentences) > 1:
        for s in sentences:
            s_sim = compute_semantic_similarity(question, s)
            # If sentence similarity is below 0.15 when answer overall is relevant, flag it
            if s_sim < 0.18 and raw_sim > 0.30:
                off_topic_sentences.append(s)

    # Generate explanation
    if score >= 85:
        explanation = "Your answer appears strongly aligned with the core focus of the question."
    elif score >= 70:
        explanation = "Your answer contains highly relevant ideas, directly addressing most aspects of the question."
    elif score >= 50:
        explanation = "Your answer is partially relevant, but some sections drift away from the main prompt."
    elif score >= 30:
        explanation = "Your answer has weak alignment with the question. Make sure to directly address the core topic."
    else:
        explanation = "Your answer appears off-topic or does not directly answer the question asked."

    return {
        "score": score,
        "raw_similarity": round(raw_sim, 3),
        "explanation": explanation,
        "off_topic_sentences": off_topic_sentences
    }
