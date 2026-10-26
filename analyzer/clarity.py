import re
from typing import Dict, Any, List
import textstat

# List of common filler words & phrases
FILLER_PATTERNS = [
    r'\bum\b', r'\buh\b', r'\blike\b', r'\bbasically\b', r'\bactually\b',
    r'\byou know\b', r'\bkind of\b', r'\bsort of\b', r'\bI mean\b',
    r'\bliterally\b', r'\bhonestly\b', r'\bto be honest\b', r'\banyway\b'
]

# List of hedging/uncertainty phrases
HEDGING_PATTERNS = [
    r'\bmaybe\b', r'\bI guess\b', r'\bprobably\b', r'\bsomewhat\b',
    r'\bpretty much\b', r'\bI think\b', r'\bhopefully\b', r'\bkind of\b',
    r'\bsort of\b', r'\bI feel like\b', r'\bmight be\b'
]

def analyze_clarity(answer: str) -> Dict[str, Any]:
    """
    Analyzes measurable text clarity, readability, filler words, hedging language,
    and sentence complexity.
    """
    if not answer.strip():
        return {
            "score": 0.0,
            "readability_score": 0.0,
            "avg_sentence_length": 0.0,
            "filler_words_found": [],
            "filler_count": 0,
            "hedging_words_found": [],
            "hedging_count": 0,
            "long_sentences": [],
            "feedback": "No answer provided to analyze clarity."
        }

    answer_clean = answer.strip()
    words = answer_clean.split()
    word_count = len(words)

    # Sentence splitting
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', answer_clean) if s.strip()]
    sentence_count = len(sentences) if len(sentences) > 0 else 1
    avg_sentence_length = round(word_count / sentence_count, 1)

    # Find long run-on sentences (> 32 words)
    long_sentences = [s for s in sentences if len(s.split()) > 32]

    # Filler words detection
    filler_words_found = []
    answer_lower = answer_clean.lower()
    for pat in FILLER_PATTERNS:
        matches = re.findall(pat, answer_lower)
        if matches:
            filler_words_found.extend(matches)
    
    filler_count = len(filler_words_found)

    # Hedging words detection
    hedging_words_found = []
    for pat in HEDGING_PATTERNS:
        matches = re.findall(pat, answer_lower)
        if matches:
            hedging_words_found.extend(matches)

    hedging_count = len(hedging_words_found)

    # Readability calculation using textstat
    try:
        flesch_reading_ease = textstat.flesch_reading_ease(answer_clean)
        # Bounded between 0 and 100
        readability = max(0.0, min(100.0, float(flesch_reading_ease)))
    except Exception:
        readability = 60.0  # Reasonable default if textstat fails

    # Score deductions / additions:
    # Base score start at 90
    score = 90.0

    # Filler word penalty: -3 points per filler word, max -25
    filler_penalty = min(25.0, filler_count * 3.0)
    score -= filler_penalty

    # Hedging word penalty: -2 points per hedging word, max -15
    hedging_penalty = min(15.0, hedging_count * 2.0)
    score -= hedging_penalty

    # Sentence length penalty:
    # Ideal average sentence length for spoken/interview text is 12-22 words.
    if avg_sentence_length > 28:
        score -= min(15.0, (avg_sentence_length - 28) * 1.5)
    elif avg_sentence_length < 6 and sentence_count > 2:
        score -= 10.0

    # Penalty for long run-on sentences
    if len(long_sentences) > 0:
        score -= min(15.0, len(long_sentences) * 5.0)

    # Readability adjustment: ideal range 45-75 (clear professional English)
    if readability < 30:
        score -= 10.0  # Too dense / difficult to follow
    elif readability > 85:
        score += 5.0   # Very clean and accessible

    score = round(float(max(0.0, min(100.0, score))), 1)

    # Feedback message
    feedback_parts = []
    if filler_count > 0:
        feedback_parts.append(f"Detected {filler_count} filler words (e.g., '{', '.join(set(filler_words_found[:3]))}'). Try replacing them with brief pauses.")
    else:
        feedback_parts.append("Great job avoiding common filler words.")

    if hedging_count > 0:
        feedback_parts.append(f"Found {hedging_count} hedging expressions (e.g., '{', '.join(set(hedging_words_found[:3]))}'). Use direct active phrasing.")
    
    if len(long_sentences) > 0:
        feedback_parts.append(f"Contains {len(long_sentences)} complex or run-on sentence(s). Consider breaking long thoughts into distinct sentences.")

    if avg_sentence_length >= 12 and avg_sentence_length <= 25 and filler_count == 0 and hedging_count == 0:
        feedback_parts.append("Sentence length and clarity are well balanced.")

    return {
        "score": score,
        "readability_score": round(readability, 1),
        "avg_sentence_length": avg_sentence_length,
        "filler_words_found": list(set(filler_words_found)),
        "filler_count": filler_count,
        "hedging_words_found": list(set(hedging_words_found)),
        "hedging_count": hedging_count,
        "long_sentences": long_sentences,
        "feedback": " ".join(feedback_parts)
    }
