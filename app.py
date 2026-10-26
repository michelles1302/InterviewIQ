import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
import os
from datetime import datetime

from database import init_db, save_attempt, get_all_attempts, get_attempt_by_id, delete_attempt
from report_generator import generate_pdf_report
from analyzer.relevance import analyze_relevance
from analyzer.keyword_analysis import analyze_keyword_coverage
from analyzer.clarity import analyze_clarity
from analyzer.conciseness import analyze_conciseness
from analyzer.structure import analyze_structure
from analyzer.technical_depth import analyze_technical_depth
from analyzer.scoring import calculate_overall_score
from analyzer.suggestions import (
    generate_strengths_and_weaknesses,
    analyze_sentences,
    get_answer_strengthening_template
)

# Page Configuration
st.set_page_config(
    page_title="InterviewIQ — AI Interview Answer Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB on start
init_db()

# Load Questions
@st.cache_data
def load_questions_library():
    path = os.path.join(os.path.dirname(__file__), "data", "questions.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

QUESTIONS_DATA = load_questions_library()

# Custom CSS for Modern SaaS Aesthetic
st.markdown("""
<style>
    /* Main Layout & Dark Theme Palette */
    .main {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header & Typography */
    h1, h2, h3, h4 {
        color: #F8FAFC !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-top: -10px;
        margin-bottom: 25px;
    }
    
    /* Card Styles */
    .iq-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .iq-card-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #818CF8;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    /* Custom Badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-easy { background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-medium { background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.4); }
    .badge-hard { background: rgba(239, 68, 68, 0.2); color: #FCA5A5; border: 1px solid rgba(239, 68, 68, 0.4); }
    .badge-category { background: rgba(99, 102, 241, 0.2); color: #A5B4FC; border: 1px solid rgba(99, 102, 241, 0.4); }
    
    /* Metrics display */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #818CF8;
    }
    
    .strength-item {
        background: rgba(16, 185, 129, 0.1);
        border-left: 3px solid #10B981;
        padding: 10px 14px;
        border-radius: 4px;
        margin-bottom: 8px;
        font-size: 0.92rem;
    }
    
    .improvement-item {
        background: rgba(245, 158, 11, 0.1);
        border-left: 3px solid #F59E0B;
        padding: 10px 14px;
        border-radius: 4px;
        margin-bottom: 8px;
        font-size: 0.92rem;
    }
    
    /* Text Area custom styling */
    .stTextArea textarea {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
    }

    /* Sidebar adjustments */
    section[data-testid="stSidebar"] {
        background-color: #0B1120 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)


# Plotly Radar Chart Helper
def create_score_radar_chart(scores_dict: dict):
    categories = list(scores_dict.keys())
    values = list(scores_dict.values())
    
    # Close polygon
    categories.append(categories[0])
    values.append(values[0])
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(99, 102, 241, 0.3)',
        line=dict(color='#6366F1', width=2),
        marker=dict(size=6, color='#818CF8')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color='#94A3B8', size=10),
                gridcolor='rgba(255,255,255,0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(color='#F8FAFC', size=11, weight='bold'),
                gridcolor='rgba(255,255,255,0.1)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=20),
        height=320
    )
    return fig


# Plotly Gauge Chart for Overall Score
def create_gauge_chart(score: float):
    if score >= 80:
        bar_color = "#10B981"
    elif score >= 60:
        bar_color = "#F59E0B"
    else:
        bar_color = "#EF4444"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'suffix': "/100", 'font': {'size': 32, 'color': '#F8FAFC'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#64748B"},
            'bar': {'color': bar_color, 'thickness': 0.75},
            'bgcolor': "rgba(30, 41, 59, 0.8)",
            'borderwidth': 1,
            'bordercolor': "rgba(255,255,255,0.1)",
            'steps': [
                {'range': [0, 60], 'color': 'rgba(239, 68, 68, 0.1)'},
                {'range': [60, 80], 'color': 'rgba(245, 158, 11, 0.1)'},
                {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
            ]
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=20),
        height=240
    )
    return fig


# Sidebar Navigation
st.sidebar.markdown("""
<div style="text-align: center; padding: 10px 0 20px 0;">
    <h2 style="color: #6366F1 !important; margin: 0; font-size: 1.8rem;">🎯 INTERVIEWIQ</h2>
    <p style="color: #94A3B8; font-size: 0.8rem; margin: 0;">AI Answer Analyzer</p>
</div>
""", unsafe_allow_html=True)

nav_option = st.sidebar.radio(
    "Navigation",
    ["🎯 Practice", "📚 Question Library", "📜 History", "📈 Progress & Analytics", "ℹ️ About & Methodology"],
    index=0
)

# Active Question Session State Management
if "selected_q_id" not in st.session_state:
    st.session_state["selected_q_id"] = "tech_01"


# ==========================================
# 1. PRACTICE PAGE
# ==========================================
if nav_option == "🎯 Practice":
    st.markdown("# 🎯 AI Interview Answer Analyzer")
    st.markdown("<p class='subtitle'>Practice smarter. Understand your answers. Improve with every interview.</p>", unsafe_allow_html=True)

    # Category Selection
    categories = list(set([q["category"] for q in QUESTIONS_DATA]))
    categories.sort()

    col_cat, col_q = st.columns([1, 2])

    with col_cat:
        selected_category = st.selectbox("Select Category", categories, index=0)

    # Filter questions for category + add Custom Question option
    filtered_qs = [q for q in QUESTIONS_DATA if q["category"] == selected_category]
    q_options = [q["question"] for q in filtered_qs] + ["Custom Question..."]

    # Pre-select matching session state question if available
    default_q_index = 0
    for idx, q_item in enumerate(filtered_qs):
        if q_item["id"] == st.session_state.get("selected_q_id"):
            default_q_index = idx
            break

    with col_q:
        selected_question_str = st.selectbox("Select Question", q_options, index=default_q_index)

    # Retrieve full active question details
    current_q_obj = None
    if selected_question_str == "Custom Question...":
        custom_question_text = st.text_input("Enter your custom interview question:", "Explain how you troubleshoot a performance issue in a system.")
        current_q_obj = {
            "id": "custom",
            "category": selected_category,
            "difficulty": "Medium",
            "question": custom_question_text,
            "keywords": [],
            "structure_type": selected_category.lower()
        }
    else:
        for q in filtered_qs:
            if q["question"] == selected_question_str:
                current_q_obj = q
                break

    if current_q_obj:
        st.session_state["selected_q_id"] = current_q_obj.get("id")

        # Question Display Card
        diff = current_q_obj.get("difficulty", "Medium")
        diff_class = f"badge-{diff.lower()}"

        st.markdown(f"""
        <div class="iq-card">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <span class="badge badge-category">{current_q_obj['category']}</span>
                <span class="badge {diff_class}">{diff} Difficulty</span>
            </div>
            <h3 style="margin: 5px 0 0 0; font-size: 1.2rem; font-weight: 600;">{current_q_obj['question']}</h3>
        </div>
        """, unsafe_allow_html=True)

        # Answer Input Area
        answer_input = st.text_area(
            "Your Interview Answer",
            height=200,
            placeholder="Type your detailed interview answer here... (Tip: Include background context, specific actions taken, technical details, and measurable outcomes)",
            help="Aim for 80-250 words with clear structure."
        )

        # Live Character and Word Count Metrics
        words_cnt = len(answer_input.strip().split()) if answer_input.strip() else 0
        char_cnt = len(answer_input)

        col_m1, col_m2, col_btn = st.columns([1, 1, 2])
        with col_m1:
            st.caption(f"**Word Count:** {words_cnt} words")
        with col_m2:
            st.caption(f"**Character Count:** {char_cnt} chars")

        with col_btn:
            analyze_click = st.button("✨ Analyze Answer", type="primary", use_container_width=True)

        if analyze_click:
            if not answer_input.strip():
                st.error("Please enter an answer before analyzing.")
            elif words_cnt < 8:
                st.warning("Your answer is extremely short (under 8 words). Please elaborate to enable meaningful NLP analysis.")
            else:
                with st.spinner("Running deep NLP analysis (Semantic Embedding, Structure Detection, Clarity, Technical Depth)..."):
                    # 1. Relevance Analysis
                    rel_res = analyze_relevance(current_q_obj["question"], answer_input)

                    # 2. Keyword Coverage
                    kw_res = analyze_keyword_coverage(
                        current_q_obj["question"],
                        answer_input,
                        preset_keywords=current_q_obj.get("keywords")
                    )

                    # 3. Clarity / Language Strength
                    cla_res = analyze_clarity(answer_input)

                    # 4. Conciseness
                    con_res = analyze_conciseness(answer_input, category=current_q_obj["category"])

                    # 5. Structure (STAR / Technical framework)
                    struct_res = analyze_structure(answer_input, structure_type=current_q_obj.get("structure_type", "technical"))

                    # 6. Technical Depth / Analytical Reasoning
                    depth_res = analyze_technical_depth(answer_input, category=current_q_obj["category"])

                    # 7. Weighted Scoring Calculation
                    score_res = calculate_overall_score(
                        relevance_score=rel_res["score"],
                        clarity_score=cla_res["score"],
                        structure_score=struct_res["score"],
                        technical_depth_score=depth_res["score"],
                        conciseness_score=con_res["score"],
                        concept_coverage_score=kw_res["score"],
                        category=current_q_obj["category"]
                    )

                    # 8. Strengths & Improvements Generation
                    feedback_res = generate_strengths_and_weaknesses(
                        rel_res, cla_res, struct_res, depth_res, con_res, kw_res
                    )

                    # 9. Sentence-level breakdown
                    sentence_analysis = analyze_sentences(
                        answer_input,
                        filler_words=cla_res["filler_words_found"],
                        hedging_words=cla_res["hedging_words_found"]
                    )

                    # 10. Guidance Template
                    template_guidance = get_answer_strengthening_template(
                        category=current_q_obj["category"],
                        framework=struct_res["framework_used"]
                    )

                    # Store full analysis object
                    full_analysis = {
                        "relevance": rel_res,
                        "keyword_coverage": kw_res,
                        "clarity": cla_res,
                        "conciseness": con_res,
                        "structure": struct_res,
                        "technical_depth": depth_res,
                        "scoring": score_res,
                        "feedback": feedback_res,
                        "sentence_analysis": sentence_analysis,
                        "template_guidance": template_guidance
                    }

                    # Save to DB
                    attempt_id = save_attempt(
                        question_id=current_q_obj["id"],
                        question_text=current_q_obj["question"],
                        category=current_q_obj["category"],
                        difficulty=current_q_obj.get("difficulty", "Medium"),
                        answer_text=answer_input,
                        overall_score=score_res["overall_score"],
                        relevance_score=rel_res["score"],
                        clarity_score=cla_res["score"],
                        structure_score=struct_res["score"],
                        technical_depth_score=depth_res["score"],
                        conciseness_score=con_res["score"],
                        concept_coverage_score=kw_res["score"],
                        strengths=feedback_res["strengths"],
                        improvements=feedback_res["improvements"],
                        full_analysis=full_analysis
                    )

                    st.session_state["latest_attempt"] = get_attempt_by_id(attempt_id)
                    st.success("Analysis complete! Results saved to practice history.")

        # DISPLAY RESULTS IF AVAILABLE
        if "latest_attempt" in st.session_state and st.session_state["latest_attempt"]:
            attempt = st.session_state["latest_attempt"]
            fa = attempt["full_analysis"]

            st.markdown("---")
            st.markdown("## 📊 Analysis Dashboard")

            # Top Row: Overall Gauge + Score Radar Chart
            col_g, col_r = st.columns([1, 1])

            with col_g:
                st.markdown("<div class='iq-card-title'>Overall Evaluation Score</div>", unsafe_allow_html=True)
                st.plotly_chart(create_gauge_chart(attempt["overall_score"]), use_container_width=True)

            with col_r:
                st.markdown("<div class='iq-card-title'>Competency Breakdown Radar</div>", unsafe_allow_html=True)
                component_scores = fa["scoring"]["component_scores"]
                st.plotly_chart(create_score_radar_chart(component_scores), use_container_width=True)

            # Component Score Metric Grid Cards
            st.markdown("### Component Scores")
            col1, col2, col3, col4, col5, col6 = st.columns(6)

            metrics_list = [
                ("Relevance", attempt["relevance_score"], col1),
                ("Clarity", attempt["clarity_score"], col2),
                ("Structure", attempt["structure_score"], col3),
                ("Tech Depth", attempt["technical_depth_score"], col4),
                ("Conciseness", attempt["conciseness_score"], col5),
                ("Concepts", attempt["concept_coverage_score"], col6)
            ]

            for label, val, col in metrics_list:
                with col:
                    color = "#10B981" if val >= 75 else "#F59E0B" if val >= 55 else "#EF4444"
                    st.markdown(f"""
                    <div class="iq-card" style="text-align: center; padding: 12px 6px;">
                        <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 700;">{label.upper()}</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: {color}; margin-top: 4px;">{val:.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Strengths & Improvement Areas Side by Side
            col_s, col_i = st.columns(2)

            with col_s:
                st.markdown("<div class='iq-card'>", unsafe_allow_html=True)
                st.markdown("<h4 style='color: #10B981 !important;'>✓ Concrete Strengths</h4>", unsafe_allow_html=True)
                for s in attempt["strengths"]:
                    st.markdown(f"<div class='strength-item'>✓ {s}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_i:
                st.markdown("<div class='iq-card'>", unsafe_allow_html=True)
                st.markdown("<h4 style='color: #F59E0B !important;'>⚠ Key Improvement Areas</h4>", unsafe_allow_html=True)
                for imp in attempt["improvements"]:
                    st.markdown(f"<div class='improvement-item'>⚠ {imp}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # Expandable Deep-Dive Feedback Sections
            st.markdown("### 🔍 Detailed Feedback & Sentence Diagnostics")

            with st.expander("📌 Relevance & Concept Coverage Details", expanded=False):
                st.write(f"**Semantic Relevance:** {fa['relevance']['explanation']}")
                st.write(f"**Concept Coverage:** {fa['keyword_coverage']['summary']}")
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.markdown("**Covered Concepts:**")
                    if fa['keyword_coverage']['covered_keywords']:
                        for c in fa['keyword_coverage']['covered_keywords']:
                            st.markdown(f"- <font color='#10B981'>✓ {c}</font>", unsafe_allow_html=True)
                    else:
                        st.caption("None detected.")
                with col_c2:
                    st.markdown("**Missing Concepts:**")
                    if fa['keyword_coverage']['missing_keywords']:
                        for m in fa['keyword_coverage']['missing_keywords']:
                            st.markdown(f"- <font color='#EF4444'>✗ {m}</font>", unsafe_allow_html=True)
                    else:
                        st.caption("None missing!")

            with st.expander("🧩 Structural Framework & Technical Depth", expanded=False):
                st.write(f"**Framework Evaluated:** {fa['structure']['framework_used']}")
                st.write(f"**Structure Assessment:** {fa['structure']['feedback']}")
                
                st.markdown("**Detected Structural Elements:**")
                found_el = fa['structure']['found_elements']
                if found_el:
                    for el, text in found_el.items():
                        st.markdown(f"- **{el}:** *\"{text}\"*")
                else:
                    st.caption("No clear structural components recognized.")
                
                st.write(f"**Technical Depth Observations:** {fa['technical_depth']['feedback']}")
                st.caption(f"Reasoning Phrases: {fa['technical_depth']['reasoning_count']} | Metric Mentions: {fa['technical_depth']['metrics_count']}")

            with st.expander("💬 Sentence-Level Diagnostics", expanded=False):
                st.write("Detailed sentence-by-sentence NLP evaluation:")
                sents = fa.get("sentence_analysis", [])
                if sents:
                    for sent_item in sents:
                        s_color = "#10B981" if sent_item["score"] >= 80 else "#F59E0B" if sent_item["score"] >= 60 else "#EF4444"
                        st.markdown(f"""
                        <div style="background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid {s_color};">
                            <div><strong>Sentence {sent_item['index']}:</strong> <em>"{sent_item['sentence']}"</em></div>
                            <div style="font-size: 0.82rem; color: #94A3B8; margin-top: 4px;">
                                <strong>Issues:</strong> {', '.join(sent_item['issues'])} | <strong>Suggestion:</strong> {sent_item['suggestion']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No sentence breakdown available.")

            with st.expander("💡 How to Strengthen Your Answer (Template Guidance)", expanded=False):
                tpl = fa.get("template_guidance", {})
                st.markdown(f"#### {tpl.get('title', 'Answer Template')}")
                st.write(tpl.get('description', ''))
                for sec in tpl.get('sections', []):
                    st.markdown(f"- **{sec['name']}:** {sec['guide']}")

            # PDF Download Button
            st.markdown("---")
            pdf_data = generate_pdf_report(attempt)
            st.download_button(
                label="📥 Download Official PDF Evaluation Report",
                data=pdf_data,
                file_name=f"InterviewIQ_Report_Attempt_{attempt['id']}.pdf",
                mime="application/pdf",
                type="primary"
            )


# ==========================================
# 2. QUESTION LIBRARY PAGE
# ==========================================
elif nav_option == "📚 Question Library":
    st.markdown("# 📚 Interview Question Library")
    st.markdown("<p class='subtitle'>Browse and search over 30+ categorized technical, behavioral, and leadership questions.</p>", unsafe_allow_html=True)

    col_s, col_f, col_d = st.columns([2, 1, 1])

    with col_s:
        search_query = st.text_input("🔍 Search Questions or Keywords", "")

    all_cats = ["All Categories"] + sorted(list(set([q["category"] for q in QUESTIONS_DATA])))
    with col_f:
        cat_filter = st.selectbox("Category Filter", all_cats, index=0)

    diff_options = ["All Difficulties", "Easy", "Medium", "Hard"]
    with col_d:
        diff_filter = st.selectbox("Difficulty Filter", diff_options, index=0)

    # Filtering logic
    filtered = QUESTIONS_DATA
    if cat_filter != "All Categories":
        filtered = [q for q in filtered if q["category"] == cat_filter]
    if diff_filter != "All Difficulties":
        filtered = [q for q in filtered if q["difficulty"] == diff_filter]
    if search_query.strip():
        sq = search_query.lower()
        filtered = [
            q for q in filtered
            if sq in q["question"].lower() or any(sq in kw.lower() for kw in q.get("keywords", []))
        ]

    st.write(f"Showing **{len(filtered)}** question(s):")

    for q in filtered:
        diff_class = f"badge-{q['difficulty'].lower()}"
        col_q_card, col_btn_p = st.columns([4, 1])

        with col_q_card:
            st.markdown(f"""
            <div class="iq-card" style="margin-bottom: 10px; padding: 14px 18px;">
                <div style="margin-bottom: 6px;">
                    <span class="badge badge-category">{q['category']}</span>
                    <span class="badge {diff_class}">{q['difficulty']}</span>
                </div>
                <div style="font-size: 1.05rem; font-weight: 600; color: #F8FAFC;">{q['question']}</div>
                <div style="font-size: 0.8rem; color: #64748B; margin-top: 6px;">
                    Keywords: {', '.join(q.get('keywords', [])[:5])}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_btn_p:
            if st.button("Practice 🎯", key=f"btn_p_{q['id']}", use_container_width=True):
                st.session_state["selected_q_id"] = q["id"]
                st.info("Question selected! Switch to Practice tab to enter your answer.")


# ==========================================
# 3. HISTORY PAGE
# ==========================================
elif nav_option == "📜 History":
    st.markdown("# 📜 Practice History")
    st.markdown("<p class='subtitle'>Review all previous interview attempts, saved scores, and detailed reports.</p>", unsafe_allow_html=True)

    attempts = get_all_attempts()

    if not attempts:
        st.info("No practice attempts recorded yet. Go to Practice to complete your first analysis!")
    else:
        st.write(f"Total Saved Attempts: **{len(attempts)}**")

        for att in attempts:
            score = att["overall_score"]
            s_color = "#10B981" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"

            with st.expander(f"Attempt #{att['id']} | {att['timestamp']} | Score: {score:.1f}/100 — {att['question_text'][:60]}..."):
                col_h1, col_h2 = st.columns([3, 1])

                with col_h1:
                    st.write(f"**Question:** {att['question_text']}")
                    st.write(f"**Category:** {att['category']} | **Difficulty:** {att['difficulty']}")
                    st.markdown(f"**Submitted Answer:** *\"{att['answer_text']}\"*")

                with col_h2:
                    st.markdown(f"""
                    <div style="text-align: center; background: rgba(30, 41, 59, 0.8); padding: 15px; border-radius: 8px;">
                        <div style="font-size: 0.8rem; color: #94A3B8;">SCORE</div>
                        <div style="font-size: 2.2rem; font-weight: 800; color: {s_color};">{score:.1f}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("#### Component Scores")
                c1, c2, c3, c4, c5, c6 = st.columns(6)
                c1.metric("Relevance", f"{att['relevance_score']:.0f}")
                c2.metric("Clarity", f"{att['clarity_score']:.0f}")
                c3.metric("Structure", f"{att['structure_score']:.0f}")
                c4.metric("Tech Depth", f"{att['technical_depth_score']:.0f}")
                c5.metric("Conciseness", f"{att['conciseness_score']:.0f}")
                c6.metric("Concepts", f"{att['concept_coverage_score']:.0f}")

                col_dl, col_del = st.columns([3, 1])
                with col_dl:
                    pdf_bytes = generate_pdf_report(att)
                    st.download_button(
                        f"Download PDF Report #{att['id']}",
                        data=pdf_bytes,
                        file_name=f"InterviewIQ_Report_Attempt_{att['id']}.pdf",
                        mime="application/pdf",
                        key=f"pdf_dl_{att['id']}"
                    )
                with col_del:
                    if st.button(f"Delete Attempt", key=f"del_{att['id']}", type="secondary"):
                        delete_attempt(att['id'])
                        st.warning("Attempt deleted. Refreshing page...")
                        st.rerun()


# ==========================================
# 4. PROGRESS & ANALYTICS PAGE
# ==========================================
elif nav_option == "📈 Progress & Analytics":
    st.markdown("# 📈 Score Progress & Performance Analytics")
    st.markdown("<p class='subtitle'>Track your score trajectory over time and evaluate strengths by category.</p>", unsafe_allow_html=True)

    attempts = get_all_attempts()

    if len(attempts) < 1:
        st.info("Complete at least 1 practice attempt to unlock score analytics and progress charts.")
    else:
        df = pd.DataFrame(attempts)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # KPI Summary Cards
        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        col_k1.metric("Total Attempts", len(df))
        col_k2.metric("Average Overall Score", f"{df['overall_score'].mean():.1f}")
        col_k3.metric("Highest Score", f"{df['overall_score'].max():.1f}")
        col_k4.metric("Latest Score", f"{df['overall_score'].iloc[-1]:.1f}")

        st.markdown("---")

        # Score Trajectory Line Chart
        st.markdown("### 📉 Score Trajectory Over Time")
        fig_line = px.line(
            df,
            x='timestamp',
            y='overall_score',
            markers=True,
            title='Overall Practice Score Evolution',
            labels={'timestamp': 'Date & Time', 'overall_score': 'Overall Score (0-100)'},
            color_discrete_sequence=['#6366F1']
        )
        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(30, 41, 59, 0.4)',
            font=dict(color='#F8FAFC'),
            yaxis=dict(range=[0, 105], gridcolor='rgba(255,255,255,0.1)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # Performance by Category
        col_cat_chart, col_radar_avg = st.columns(2)

        with col_cat_chart:
            st.markdown("### 🏷️ Average Score by Category")
            cat_df = df.groupby('category')['overall_score'].mean().reset_index()
            fig_bar = px.bar(
                cat_df,
                x='category',
                y='overall_score',
                color='overall_score',
                color_continuous_scale=['#EF4444', '#F59E0B', '#10B981'],
                range_color=[40, 95]
            )
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(30, 41, 59, 0.4)',
                font=dict(color='#F8FAFC'),
                yaxis=dict(range=[0, 100], gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_radar_avg:
            st.markdown("### 🕸️ Overall Competency Profile")
            avg_components = {
                "Relevance": df['relevance_score'].mean(),
                "Clarity": df['clarity_score'].mean(),
                "Structure": df['structure_score'].mean(),
                "Tech Depth": df['technical_depth_score'].mean(),
                "Conciseness": df['conciseness_score'].mean(),
                "Concepts": df['concept_coverage_score'].mean()
            }
            st.plotly_chart(create_score_radar_chart(avg_components), use_container_width=True)


# ==========================================
# 5. ABOUT & METHODOLOGY PAGE
# ==========================================
elif nav_option == "ℹ️ About & Methodology":
    st.markdown("# ℹ️ About InterviewIQ & NLP Methodology")
    st.markdown("<p class='subtitle'>Transparent, local, zero-API AI engineering for real interview practice.</p>", unsafe_allow_html=True)

    st.markdown("""
    ### 🛡️ Core Architecture Principles
    1. **100% Deterministic & Empirical NLP**: Every score is derived from actual mathematical computations (embeddings, cosine similarity, lexical statistics, readability formulas, and linguistic patterns).
    2. **Zero Paid APIs / Privacy First**: Runs completely locally on CPU using `sentence-transformers/all-MiniLM-L6-v2`. No data leaves your machine. No OpenAI or Claude API keys required.
    3. **Transparent Weighting**: Adapts component weights based on the interview question category (e.g., STAR structure is weighted higher for Behavioral questions; Technical Depth is weighted higher for Technical questions).

    ---

    ### 📐 Scoring Metric Breakdown
    - **Semantic Relevance (20-30%)**: Cosine similarity between question and answer dense vector embeddings calculated via MiniLM-L6-v2.
    - **Concept & Keyword Coverage (10%)**: Extracted technical concepts matched against response vocabulary.
    - **Clarity / Language Strength (15-25%)**: Readability metrics (Flesch Reading Ease), sentence length variance, filler word penalties (`um`, `basically`, `actually`), and hedging phrase penalties (`maybe`, `I guess`).
    - **Structure Framework (15-30%)**: Automated detection of STAR framework (Situation, Task, Action, Result) for behavioral questions, or Definition-Explanation-Example-Application for technical questions.
    - **Technical Depth & Reasoning (5-25%)**: Quantitative metric count, analytical reasoning patterns (`because`, `led to`, `trade-off`), and technical vocabulary density.
    - **Conciseness (10%)**: Target word count boundaries (80-240 words optimal) and n-gram repetition detection.

    ---

    ### ⚠️ Limitations Notice
    InterviewIQ provides computational feedback on textual content and structure.
    It does **NOT** measure psychological confidence, human vocal tone, personality traits, or actual hiring probability. Use it as an objective practice tool to hone answer structure and depth.
    """)
