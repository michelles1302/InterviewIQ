import re
from typing import Dict, Any, List

# List of cause-and-effect / analytical reasoning terms
REASONING_PATTERNS = [
    r'\bbecause\b', r'\bdue to\b', r'\bled to\b', r'\bresulting in\b', r'\btherefore\b',
    r'\bconsequently\b', r'\btrade-off\b', r'\btradeoff\b', r'\bin order to\b',
    r'\bthe reason\b', r'\binstead of\b', r'\bcompared to\b', r'\bsignificantly\b',
    r'\boptimized\b', r'\bprevented\b', r'\bmitigated\b', r'\bensured\b'
]

# Quantifiable metric patterns (% numbers, latency, throughput, scale)
METRIC_PATTERNS = [
    r'\b\d+%\b', r'\b\d+\s*percent\b', r'\b\d+\s*ms\b', r'\b\d+\s*seconds?\b',
    r'\b\d+\s*users?\b', r'\b\d+\s*x\b', r'\b\d+k\b', r'\b\d+m\b',
    r'\bincreased by\b', r'\breduced by\b', r'\bsaved\b', r'\bimproved by\b'
]

# Technical domain keywords
GENERIC_TECH_TERMS = [
    "algorithm", "architecture", "api", "database", "latency", "throughput", "scalability",
    "optimization", "bottleneck", "framework", "concurrency", "asynchronous", "refactoring",
    "deployment", "pipeline", "cache", "caching", "query", "indexes", "schema", "microservices",
    "monolith", "memory", "cpu", "overhead", "trade-off", "protocol", "security", "encryption"
]


def analyze_technical_depth(answer: str, category: str = "Technical") -> Dict[str, Any]:
    """
    Analyzes depth of technical terminology, analytical reasoning, metric usage, and practical detail.
    Adapts expectations based on question category.
    """
    if not answer.strip():
        return {
            "score": 0.0,
            "reasoning_count": 0,
            "metrics_count": 0,
            "tech_terms_found": [],
            "depth_level": "none",
            "feedback": "No answer provided to analyze technical depth."
        }

    answer_clean = answer.strip()
    answer_lower = answer_clean.lower()
    words = answer_lower.split()
    word_count = len(words)

    # 1. Reasoning count
    reasoning_found = []
    for pat in REASONING_PATTERNS:
        if re.search(pat, answer_lower):
            reasoning_found.append(pat.replace(r'\b', ''))
    reasoning_count = len(reasoning_found)

    # 2. Metric / Quantification count
    metrics_found = []
    for pat in METRIC_PATTERNS:
        matches = re.findall(pat, answer_lower)
        if matches:
            metrics_found.extend(matches)
    metrics_count = len(metrics_found)

    # 3. Technical vocabulary density
    tech_terms_found = []
    for term in GENERIC_TECH_TERMS:
        if term in answer_lower:
            tech_terms_found.append(term)
    
    tech_term_count = len(tech_terms_found)

    # Scoring adaptation by category
    is_technical = category.lower() in ["technical", "problem solving", "project experience"]
    
    score = 50.0  # Baseline

    if is_technical:
        # Tech term bonus (up to 30 pts)
        score += min(30.0, tech_term_count * 6.0)
        # Analytical reasoning bonus (up to 25 pts)
        score += min(25.0, reasoning_count * 8.0)
        # Metrics bonus (up to 15 pts)
        score += min(15.0, metrics_count * 7.5)
        
        # Keyword dumping check: if 5+ tech terms in under 30 words, slight penalty for buzzword dumping
        if word_count < 35 and tech_term_count >= 5:
            score -= 15.0
            keyword_dumping_flag = True
        else:
            keyword_dumping_flag = False
    else:
        # Non-technical (Behavioral, HR, Leadership): Focus on depth of context & metric evidence
        score += min(30.0, reasoning_count * 10.0)
        score += min(25.0, metrics_count * 12.5)
        score += min(15.0, tech_term_count * 5.0)
        keyword_dumping_flag = False

    score = round(float(max(0.0, min(100.0, score))), 1)

    # Depth level classification
    if score >= 85:
        depth_level = "high"
        feedback = f"Strong technical depth! Good use of analytical reasoning ('{', '.join(reasoning_found[:2])}') and technical vocabulary."
    elif score >= 65:
        depth_level = "moderate"
        feedback = "Moderate depth. Consider explaining cause-and-effect trade-offs more explicitly or adding specific metrics."
    else:
        depth_level = "basic"
        feedback = "Basic depth. To strengthen your answer, explain the 'why' behind decisions and include measurable outcomes."

    if keyword_dumping_flag:
        feedback += " Note: Avoid listing technical buzzwords without full explanatory context."

    return {
        "score": score,
        "reasoning_count": reasoning_count,
        "metrics_count": metrics_count,
        "tech_terms_found": list(set(tech_terms_found)),
        "depth_level": depth_level,
        "feedback": feedback
    }
