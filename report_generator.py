import io
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_pdf_report(attempt_data: Dict[str, Any]) -> bytes:
    """
    Generates a sleek, professional PDF evaluation report for an interview attempt using ReportLab.
    Returns PDF content as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#4F46E5")  # Indigo accent
    dark_bg = colors.HexColor("#0F172A")        # Deep slate
    text_dark = colors.HexColor("#1E293B")
    card_bg = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        alignment=TA_LEFT
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
        alignment=TA_LEFT
    )

    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=text_dark
    )

    bold_body_style = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    story = []

    # Title & Header
    story.append(Paragraph("<b>INTERVIEWIQ</b> — AI Answer Analysis Report", title_style))
    story.append(Paragraph(f"Generated on {attempt_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))} | Automated NLP Diagnostics", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=12))

    # Meta Table: Question info & Overall Score Box
    q_text = attempt_data.get('question_text', 'N/A')
    cat = attempt_data.get('category', 'N/A')
    diff = attempt_data.get('difficulty', 'N/A')
    overall_score = float(attempt_data.get('overall_score', 0.0))

    meta_content = [
        [
            Paragraph(f"<b>Category:</b> {cat} | <b>Difficulty:</b> {diff}<br/><br/><b>Question:</b><br/>{q_text}", body_style),
            Paragraph(f"<font size=10 color='#64748B'>OVERALL SCORE</font><br/><font size=28 color='#4F46E5'><b>{overall_score:.1f}</b></font><font size=14 color='#94A3B8'>/100</font>", ParagraphStyle('ScoreBox', parent=body_style, alignment=TA_CENTER))
        ]
    ]

    meta_table = Table(meta_content, colWidths=[380, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), card_bg),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # Component Scores Table
    story.append(Paragraph("Metric Breakdown", h2_style))

    rel = float(attempt_data.get('relevance_score', 0))
    cla = float(attempt_data.get('clarity_score', 0))
    str_s = float(attempt_data.get('structure_score', 0))
    dep = float(attempt_data.get('technical_depth_score', 0))
    con = float(attempt_data.get('conciseness_score', 0))
    cov = float(attempt_data.get('concept_coverage_score', 0))

    comp_data = [
        [Paragraph("<b>Metric</b>", bold_body_style), Paragraph("<b>Score</b>", bold_body_style), Paragraph("<b>Benchmark / Status</b>", bold_body_style)],
        [Paragraph("Relevance (Semantic Alignment)", body_style), f"{rel:.1f} / 100", "Strong" if rel >= 75 else "Needs Focus"],
        [Paragraph("Clarity & Language Strength", body_style), f"{cla:.1f} / 100", "Clear" if cla >= 75 else "Contains Fillers/Hedging"],
        [Paragraph("Structure (Framework Alignment)", body_style), f"{str_s:.1f} / 100", "Structured" if str_s >= 75 else "Missing Components"],
        [Paragraph("Technical Depth & Reasoning", body_style), f"{dep:.1f} / 100", "Rigorous" if dep >= 75 else "Basic Depth"],
        [Paragraph("Conciseness & Word Density", body_style), f"{con:.1f} / 100", "Optimal" if con >= 75 else "Short/Verbose"],
        [Paragraph("Concept & Keyword Coverage", body_style), f"{cov:.1f} / 100", "Comprehensive" if cov >= 75 else "Incomplete Concepts"]
    ]

    comp_table = Table(comp_data, colWidths=[240, 120, 180])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEF2FF")),
        ('TEXTCOLOR', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 14))

    # User's Answer Text Box
    story.append(Paragraph("Submitted Response", h2_style))
    user_answer = attempt_data.get('answer_text', '')
    answer_p = Paragraph(f"<i>\"{user_answer}\"</i>", ParagraphStyle('AnsItalic', parent=body_style, textColor=colors.HexColor("#334155")))
    ans_table = Table([[answer_p]], colWidths=[540])
    ans_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(ans_table)
    story.append(Spacer(1, 14))

    # Strengths & Improvement Areas
    strengths = attempt_data.get('strengths', [])
    improvements = attempt_data.get('improvements', [])

    story.append(Paragraph("Key Strengths", h2_style))
    for st in strengths:
        story.append(Paragraph(f"• <b>{st}</b>", body_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Actionable Improvement Areas", h2_style))
    for imp in improvements:
        story.append(Paragraph(f"• {imp}", body_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=0, spaceAfter=8))
    story.append(Paragraph("InterviewIQ Engine — Pure NLP & ML Analysis | CPU Local Processing | No Data Shared Externally", subtitle_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
