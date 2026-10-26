import re
from typing import Dict, Any, List, Set, Optional

def extract_keywords_from_question(question: str) -> List[str]:
    """
    Extracts key phrases and nouns from a custom question if preset keywords are absent.
    """
    # Remove common question words & stop words
    stopwords = {
        "tell", "me", "about", "a", "an", "the", "time", "you", "faced", "how", "did", "what",
        "is", "are", "explain", "difference", "between", "describe", "situation", "where",
        "when", "why", "do", "can", "in", "on", "at", "for", "with", "your", "my", "or", "and"
    }

    # Clean punctuation
    cleaned = re.sub(r'[^\w\s-]', '', question.lower())
    words = cleaned.split()

    extracted = []
    for w in words:
        if len(w) > 3 and w not in stopwords:
            extracted.append(w)
    
    # Also extract hyphenated terms or word pairs if present
    pairs = []
    words_orig = cleaned.split()
    for i in range(len(words_orig) - 1):
        w1, w2 = words_orig[i], words_orig[i+1]
        if w1 not in stopwords and w2 not in stopwords:
            pairs.append(f"{w1} {w2}")

    result = list(set(extracted + pairs))
    return result if result else ["concept", "solution", "approach"]


def analyze_keyword_coverage(question: str, answer: str, preset_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Analyzes concept and keyword coverage between question and answer.
    """
    if not answer.strip():
        return {
            "score": 0.0,
            "covered_keywords": [],
            "missing_keywords": preset_keywords or [],
            "coverage_percentage": 0.0,
            "summary": "No answer provided to analyze keyword coverage."
        }

    target_keywords = preset_keywords if (preset_keywords and len(preset_keywords) > 0) else extract_keywords_from_question(question)
    
    answer_lower = answer.lower()
    covered = []
    missing = []

    for kw in target_keywords:
        kw_clean = kw.lower().strip()
        # Stem matching / substring matching / boundary matching
        pattern = r'\b' + re.escape(kw_clean) + r'|\b' + re.escape(kw_clean.rstrip('s'))
        if re.search(pattern, answer_lower) or kw_clean in answer_lower:
            covered.append(kw)
        else:
            missing.append(kw)

    total = len(target_keywords)
    covered_cnt = len(covered)
    coverage_pct = round((covered_cnt / total * 100.0), 1) if total > 0 else 100.0

    if coverage_pct >= 80:
        summary = f"Excellent coverage! You addressed {covered_cnt} out of {total} key concepts."
    elif coverage_pct >= 50:
        summary = f"Moderate coverage. You mentioned {covered_cnt} out of {total} key concepts."
    else:
        summary = f"Low coverage. You missed several key domain concepts ({len(missing)} missing)."

    return {
        "score": coverage_pct,
        "covered_keywords": covered,
        "missing_keywords": missing,
        "coverage_percentage": coverage_pct,
        "summary": summary
    }
