import pytest
from analyzer.embeddings import compute_semantic_similarity
from analyzer.relevance import analyze_relevance
from analyzer.keyword_analysis import analyze_keyword_coverage, extract_keywords_from_question
from analyzer.clarity import analyze_clarity
from analyzer.conciseness import analyze_conciseness
from analyzer.structure import analyze_structure
from analyzer.technical_depth import analyze_technical_depth
from analyzer.scoring import calculate_overall_score
from analyzer.suggestions import generate_strengths_and_weaknesses, analyze_sentences


def test_empty_answer_handling():
    empty_ans = ""
    rel = analyze_relevance("Explain REST APIs", empty_ans)
    assert rel["score"] == 0.0
    
    cla = analyze_clarity(empty_ans)
    assert cla["score"] == 0.0
    
    con = analyze_conciseness(empty_ans)
    assert con["score"] == 0.0
    
    struct = analyze_structure(empty_ans, "technical")
    assert struct["score"] == 0.0


def test_semantic_similarity_range():
    q = "What is overfitting in machine learning?"
    ans_good = "Overfitting occurs when a machine learning model learns noise in the training set and fails to generalize to unseen test data. Regularization can prevent it."
    ans_irrelevant = "I enjoy cooking pasta with marinara sauce on Sunday evenings."

    sim_good = compute_semantic_similarity(q, ans_good)
    sim_bad = compute_semantic_similarity(q, ans_irrelevant)

    assert 0.0 <= sim_good <= 1.0
    assert 0.0 <= sim_bad <= 1.0
    assert sim_good > sim_bad

    rel_good = analyze_relevance(q, ans_good)
    rel_bad = analyze_relevance(q, ans_irrelevant)

    assert rel_good["score"] > rel_bad["score"]
    assert 0.0 <= rel_good["score"] <= 100.0
    assert 0.0 <= rel_bad["score"] <= 100.0


test_preset_kws = ["HTTP", "REST API", "endpoint", "JSON"]

def test_keyword_coverage():
    q = "Explain REST APIs"
    ans = "A REST API uses HTTP methods like GET and POST to communicate with endpoints using JSON format."
    
    res = analyze_keyword_coverage(q, ans, preset_keywords=test_preset_kws)
    assert res["score"] == 100.0
    assert len(res["covered_keywords"]) == 4
    assert len(res["missing_keywords"]) == 0

    ans_partial = "A REST API uses endpoints for web services."
    res_part = analyze_keyword_coverage(q, ans_partial, preset_keywords=test_preset_kws)
    assert res_part["score"] < 100.0
    assert "JSON" in res_part["missing_keywords"]


def test_clarity_and_filler_detection():
    ans_clean = "We refactored the legacy system by modularizing the codebase into microservices."
    ans_filler = "Basically, um, like we kind of, you know, refactored the legacy system actually."

    cla_clean = analyze_clarity(ans_clean)
    cla_filler = analyze_clarity(ans_filler)

    assert cla_clean["score"] > cla_filler["score"]
    assert cla_filler["filler_count"] > 0
    assert 0.0 <= cla_clean["score"] <= 100.0


def test_structure_star_detection():
    star_ans = (
        "When I was a lead developer at Acme Corp, our database queries were taking 10 seconds. "
        "My goal was to reduce query latency by 50%. "
        "I implemented database indexes and cached frequent results using Redis. "
        "As a result, latency dropped to 200ms and saved $20k in cloud computing costs."
    )

    struct_res = analyze_structure(star_ans, "behavioral")
    assert struct_res["score"] >= 80.0
    assert "Situation" in struct_res["found_elements"]
    assert "Action" in struct_res["found_elements"]
    assert "Result" in struct_res["found_elements"]
    assert len(struct_res["missing_elements"]) == 0


def test_technical_depth():
    tech_ans = (
        "We optimized query latency because index scans were causing high CPU utilization. "
        "This resulted in a 45% reduction in database response time."
    )
    depth_res = analyze_technical_depth(tech_ans, "Technical")
    assert depth_res["reasoning_count"] >= 2
    assert depth_res["metrics_count"] >= 1
    assert depth_res["score"] >= 70.0


def test_scoring_weights_boundary():
    score_res = calculate_overall_score(
        relevance_score=85.0,
        clarity_score=90.0,
        structure_score=75.0,
        technical_depth_score=80.0,
        conciseness_score=95.0,
        concept_coverage_score=70.0,
        category="Behavioral"
    )

    overall = score_res["overall_score"]
    assert 0.0 <= overall <= 100.0
    assert isinstance(overall, float)
    assert score_res["category_used"] == "Behavioral"


def test_sentence_analysis():
    ans = "Basically, I kind of worked on the system. It was really hard."
    sents = analyze_sentences(ans, filler_words=["basically"], hedging_words=["kind of"])
    assert len(sents) == 2
    assert sents[0]["index"] == 1
    assert len(sents[0]["issues"]) > 0
