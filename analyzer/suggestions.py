import re
from typing import Dict, Any, List, Optional

def analyze_sentences(answer: str, filler_words: List[str], hedging_words: List[str]) -> List[Dict[str, Any]]:
    """
    Performs sentence-level analysis, highlighting sentence length, filler words,
    hedging language, and actionable sentence improvement suggestions.
    """
    if not answer.strip():
        return []

    raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', answer.strip()) if s.strip()]
    sentence_feedbacks = []

    for i, sent in enumerate(raw_sentences):
        words = sent.split()
        w_len = len(words)
        sent_lower = sent.lower()

        issues = []
        suggestions = []

        # Filler check
        sent_fillers = [f for f in filler_words if f in sent_lower]
        if sent_fillers:
            issues.append(f"Contains filler words: {', '.join(set(sent_fillers))}")
            suggestions.append("Remove filler words or replace with a short pause.")

        # Hedging check
        sent_hedging = [h for h in hedging_words if h in sent_lower]
        if sent_hedging:
            issues.append(f"Uses hedging language: {', '.join(set(sent_hedging))}")
            suggestions.append("Replace vague/hedging phrasing with direct active statements.")

        # Length check
        if w_len > 32:
            issues.append(f"Run-on sentence ({w_len} words)")
            suggestions.append("Split this long thought into two shorter, clearer sentences.")
        elif w_len < 5 and len(raw_sentences) > 2:
            issues.append("Very short fragment")
            suggestions.append("Elaborate slightly to connect this point smoothly.")

        # Sentence score (100 base, deductions for issues)
        sent_score = 100 - (len(issues) * 20)
        sent_score = max(40, min(100, sent_score))

        sentence_feedbacks.append({
            "index": i + 1,
            "sentence": sent,
            "word_count": w_len,
            "score": sent_score,
            "issues": issues if issues else ["Clear sentence structure."],
            "suggestion": " ".join(suggestions) if suggestions else "No major sentence-level changes required."
        })

    return sentence_feedbacks


def generate_strengths_and_weaknesses(
    relevance_res: Dict[str, Any],
    clarity_res: Dict[str, Any],
    structure_res: Dict[str, Any],
    depth_res: Dict[str, Any],
    conciseness_res: Dict[str, Any],
    keyword_res: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generates strengths, improvement areas, detailed feedback, and answer template guidance.
    """
    strengths = []
    improvements = []
    detailed = []

    # Relevance
    if relevance_res["score"] >= 80:
        strengths.append("Strong semantic relevance directly addressing the question prompt.")
    elif relevance_res["score"] < 60:
        improvements.append("Answer drifts away from the primary question topic.")
        detailed.append({
            "area": "Relevance",
            "observation": relevance_res["explanation"],
            "action": "Ensure your first sentence directly defines or addresses the question's core subject before diving into details."
        })

    # Keyword Coverage
    if keyword_res["score"] >= 80:
        strengths.append(f"Excellent concept coverage (addressed {len(keyword_res['covered_keywords'])} key concepts).")
    elif keyword_res["score"] < 60:
        missing_sample = ", ".join(keyword_res["missing_keywords"][:3])
        improvements.append(f"Missing key domain concepts: {missing_sample}.")
        detailed.append({
            "area": "Concept Coverage",
            "observation": f"You missed important concepts related to this topic: {missing_sample}.",
            "action": f"Incorporate relevant terms like {missing_sample} into your explanation."
        })

    # Clarity / Language Strength
    if clarity_res["score"] >= 80:
        strengths.append("Clear language strength with minimal filler words and hedging phrases.")
    else:
        if clarity_res["filler_count"] > 0:
            improvements.append(f"Contains {clarity_res['filler_count']} filler word(s) (e.g., '{', '.join(clarity_res['filler_words_found'][:2])}').")
        if clarity_res["hedging_count"] > 0:
            improvements.append(f"Uses hedging language (e.g., '{', '.join(clarity_res['hedging_words_found'][:2])}').")
        if len(clarity_res["long_sentences"]) > 0:
            improvements.append("Contains long run-on sentences that impede readability.")

    # Structure
    if len(structure_res["missing_elements"]) == 0:
        strengths.append(f"Complete {structure_res['framework_used']} structural framework flow.")
    else:
        missing_str = ", ".join(structure_res["missing_elements"])
        improvements.append(f"Missing structural elements in answer: {missing_str}.")
        detailed.append({
            "area": "Structure",
            "observation": structure_res["feedback"],
            "action": f"Explicitly structure your answer to include {missing_str}."
        })

    # Technical Depth
    if depth_res["score"] >= 75:
        strengths.append("Strong technical depth and cause-and-effect analytical reasoning.")
    elif depth_res["score"] < 55:
        improvements.append("Lacks specific technical depth, reasoning keywords, or measurable outcomes.")
        detailed.append({
            "area": "Depth & Evidence",
            "observation": depth_res["feedback"],
            "action": "Add specific metrics (e.g., latency numbers, team size, percentage improvement) or cause-and-effect reasoning ('because...', 'resulting in...')."
        })

    # Conciseness
    if conciseness_res["status"] == "optimal":
        strengths.append(f"Well balanced word count ({conciseness_res['word_count']} words).")
    elif conciseness_res["status"] in ["too_short", "slightly_short"]:
        improvements.append(f"Answer is relatively short ({conciseness_res['word_count']} words).")
    elif conciseness_res["status"] in ["too_long", "slightly_long"]:
        improvements.append(f"Answer is overly verbose ({conciseness_res['word_count']} words) with potential filler/repetition.")

    # Fallback strengths/improvements if empty
    if not strengths:
        strengths.append("Answer contains understandable basic English communication.")
    if not improvements:
        improvements.append("Minor polish on sentence rhythm and vocal confidence.")

    return {
        "strengths": strengths,
        "improvements": improvements,
        "detailed_feedback": detailed
    }


def get_answer_strengthening_template(category: str, framework: str) -> Dict[str, Any]:
    """
    Provides structural guidance template without fabricating fake user experiences.
    """
    cat_lower = category.lower()
    
    if "behavioral" in cat_lower or "leadership" in cat_lower or framework.lower() == "behavioral":
        return {
            "title": "STAR Method Structural Guidance",
            "description": "Use the STAR method to structure your behavioral response clearly without leaving out key details:",
            "sections": [
                {"name": "Situation (15-20%)", "guide": "Briefly set the scene, role, company context, and initial problem."},
                {"name": "Task (10-15%)", "guide": "State your exact personal responsibility and what outcome was required."},
                {"name": "Action (50-60%)", "guide": "Explain the specific steps YOU personally took. Highlight decisions, tools, and collaboration."},
                {"name": "Result (15-20%)", "guide": "Conclude with measurable metrics or clear impact (e.g. 'reduced downtime by 35%', 'delivered on schedule')."}
            ]
        }
    elif "technical" in cat_lower or "problem solving" in cat_lower or framework.lower() == "technical":
        return {
            "title": "Technical Answer Structural Guidance",
            "description": "Structure technical answers logically from high-level definition down to practical usage:",
            "sections": [
                {"name": "Definition (20%)", "guide": "Provide a clean 1-2 sentence core definition of the concept or technology."},
                {"name": "How It Works / Mechanics (40%)", "guide": "Explain key underlying mechanics, data flow, or architectural components."},
                {"name": "Concrete Example (25%)", "guide": "Give a practical code or system architecture scenario illustrating its usage."},
                {"name": "Trade-offs & Best Practices (15%)", "guide": "Mention when to use it, limitations, or performance trade-offs."}
            ]
        }
    else:  # Project Experience / HR
        return {
            "title": "Structured Response Guidance",
            "description": "Ensure your answer follows a persuasive narrative structure:",
            "sections": [
                {"name": "Core Position / Context", "guide": "State your main point directly and provide relevant background."},
                {"name": "Key Strategy & Execution", "guide": "Outline the technical choices, personal contributions, or philosophy applied."},
                {"name": "Value & Future Impact", "guide": "Summarize the value added and how it aligns with the role or company."}
            ]
        }
