from typing import Dict, Any

# Category specific weight distributions (summing to 1.0 / 100%)
CATEGORY_WEIGHTS = {
    "Behavioral": {
        "relevance": 0.20,
        "clarity": 0.15,
        "structure": 0.30,
        "technical_depth": 0.10,
        "conciseness": 0.15,
        "concept_coverage": 0.10
    },
    "Technical": {
        "relevance": 0.25,
        "clarity": 0.15,
        "structure": 0.15,
        "technical_depth": 0.25,
        "conciseness": 0.10,
        "concept_coverage": 0.10
    },
    "Project Experience": {
        "relevance": 0.20,
        "clarity": 0.15,
        "structure": 0.25,
        "technical_depth": 0.20,
        "conciseness": 0.10,
        "concept_coverage": 0.10
    },
    "Leadership": {
        "relevance": 0.25,
        "clarity": 0.20,
        "structure": 0.25,
        "technical_depth": 0.10,
        "conciseness": 0.10,
        "concept_coverage": 0.10
    },
    "HR": {
        "relevance": 0.30,
        "clarity": 0.25,
        "structure": 0.20,
        "technical_depth": 0.05,
        "conciseness": 0.10,
        "concept_coverage": 0.10
    },
    "Problem Solving": {
        "relevance": 0.20,
        "clarity": 0.15,
        "structure": 0.25,
        "technical_depth": 0.20,
        "conciseness": 0.10,
        "concept_coverage": 0.10
    }
}

DEFAULT_WEIGHTS = {
    "relevance": 0.25,
    "clarity": 0.20,
    "structure": 0.15,
    "technical_depth": 0.20,
    "conciseness": 0.10,
    "concept_coverage": 0.10
}


def calculate_overall_score(
    relevance_score: float,
    clarity_score: float,
    structure_score: float,
    technical_depth_score: float,
    conciseness_score: float,
    concept_coverage_score: float,
    category: str = "Technical"
) -> Dict[str, Any]:
    """
    Calculates weighted overall interview answer score based on question category weights.
    Returns overall score (0-100) and detailed weight breakdown.
    """
    weights = CATEGORY_WEIGHTS.get(category, DEFAULT_WEIGHTS)

    weighted_score = (
        (relevance_score * weights["relevance"]) +
        (clarity_score * weights["clarity"]) +
        (structure_score * weights["structure"]) +
        (technical_depth_score * weights["technical_depth"]) +
        (conciseness_score * weights["conciseness"]) +
        (concept_coverage_score * weights["concept_coverage"])
    )

    overall_score = round(float(max(0.0, min(100.0, weighted_score))), 1)

    return {
        "overall_score": overall_score,
        "category_used": category,
        "weights": {k: int(v * 100) for k, v in weights.items()},
        "component_scores": {
            "Relevance": relevance_score,
            "Clarity": clarity_score,
            "Structure": structure_score,
            "Technical Depth": technical_depth_score,
            "Conciseness": conciseness_score,
            "Concept Coverage": concept_coverage_score
        }
    }
