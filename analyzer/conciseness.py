import re
from typing import Dict, Any, List, Set
from collections import Counter

def detect_ngram_repetition(text: str, n: int = 4) -> List[str]:
    """
    Detects repeated n-grams (phrases of length n) to identify excessive verbosity/repetition.
    """
    words = re.findall(r'\b\w+\b', text.lower())
    if len(words) < n * 2:
        return []
    
    ngrams = [' '.join(words[i:i+n]) for i in range(len(words) - n + 1)]
    counts = Counter(ngrams)
    
    # Filter phrases repeated more than once
    repeated = [phrase for phrase, count in counts.items() if count > 1]
    return repeated


def analyze_conciseness(answer: str, category: str = "Technical") -> Dict[str, Any]:
    """
    Analyzes answer conciseness, word count suitability, and repetition.
    """
    if not answer.strip():
        return {
            "score": 0.0,
            "word_count": 0,
            "sentence_count": 0,
            "repeated_phrases": [],
            "status": "empty",
            "feedback": "No answer provided to analyze conciseness."
        }

    answer_clean = answer.strip()
    words = answer_clean.split()
    word_count = len(words)
    
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', answer_clean) if s.strip()]
    sentence_count = len(sentences) if len(sentences) > 0 else 1

    # Detect repeated n-grams
    repeated_phrases = detect_ngram_repetition(answer_clean, n=3)

    # Word count scoring logic by category:
    # Behavioral / Project: expects 90 - 250 words
    # Technical: expects 60 - 200 words
    # HR: expects 50 - 180 words
    if category.lower() in ["behavioral", "project experience", "leadership"]:
        target_min, target_opt_min, target_opt_max, target_max = 40, 80, 240, 380
    elif category.lower() in ["technical", "problem solving"]:
        target_min, target_opt_min, target_opt_max, target_max = 35, 65, 200, 320
    else:  # HR
        target_min, target_opt_min, target_opt_max, target_max = 30, 50, 180, 280

    score = 100.0
    status = "optimal"
    feedback = ""

    if word_count < target_min:
        status = "too_short"
        # Severe penalty for extremely brief answers (e.g. 10 words)
        ratio = word_count / target_min
        score = 30.0 + (ratio * 35.0)  # 30 to 65
        feedback = f"Your answer is very brief ({word_count} words). Consider adding specific details, context, and examples."
    elif word_count < target_opt_min:
        status = "slightly_short"
        score = 70.0 + ((word_count - target_min) / (target_opt_min - target_min)) * 20.0  # 70 to 90
        feedback = f"Your answer is concise ({word_count} words). You can elaborate slightly more to add technical or contextual depth."
    elif word_count <= target_opt_max:
        status = "optimal"
        score = 95.0
        feedback = f"Optimal length ({word_count} words). Your answer balances detail and conciseness effectively."
    elif word_count <= target_max:
        status = "slightly_long"
        score = 80.0 - ((word_count - target_opt_max) / (target_max - target_opt_max)) * 15.0  # 80 to 65
        feedback = f"Your answer is fairly detailed ({word_count} words). Ensure every paragraph contributes new information."
    else:
        status = "too_long"
        score = 50.0 - min(25.0, (word_count - target_max) / 10.0)
        feedback = f"Your answer is quite verbose ({word_count} words). Streamline background details to focus on core actions and results."

    # Repetition penalty
    if len(repeated_phrases) > 0:
        penalty = min(20.0, len(repeated_phrases) * 5.0)
        score -= penalty
        feedback += f" Detected repeating phrases ('{repeated_phrases[0]}'). Try eliminating duplicate explanations."

    score = round(float(max(0.0, min(100.0, score))), 1)

    return {
        "score": score,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "repeated_phrases": repeated_phrases,
        "status": status,
        "feedback": feedback
    }
