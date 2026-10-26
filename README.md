# 🎯 InterviewIQ — AI Interview Answer Analyzer

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B)
![SentenceTransformers](https://img.shields.io/badge/NLP-all--MiniLM--L6--v2-indigo)
![License](https://img.shields.io/badge/License-MIT-green)

**InterviewIQ** is a complete, local, privacy-first AI application for analyzing and coaching interview responses. Built using **Streamlit** and local **NLP/ML models**, InterviewIQ evaluates interview answers empirically across 6 core competencies without relying on external paid APIs or cloud dependencies.

---

## 🌟 Key Features

- **Built-in Question Library**: 36+ realistic interview questions across 6 categories (Behavioral, Technical, HR, Leadership, Project Experience, Problem Solving) with Easy/Medium/Hard difficulties.
- **Custom Question Support**: Practice any user-defined interview question.
- **Deep Empirical Analysis Engine**:
  - 🎯 **Semantic Relevance**: Measures exact alignment between prompt and response using `sentence-transformers/all-MiniLM-L6-v2` dense vector cosine similarity.
  - 💡 **Concept / Keyword Coverage**: Evaluates domain-specific key term density.
  - 🗣️ **Language Strength & Clarity**: Detects filler words (`um`, `basically`, `actually`), hedging language (`maybe`, `I guess`), and readability scores via `textstat`.
  - 🧩 **Structural Framework Analysis**: Detects **STAR method** (Situation, Task, Action, Result) for behavioral questions and Definition-Explanation-Example-Application for technical questions.
  - ⚙️ **Technical Depth & Analytical Reasoning**: Identifies cause-and-effect reasoning (`because`, `led to`, `trade-off`) and metric mentions.
  - 📏 **Conciseness**: Evaluates word density and flags n-gram repetition.
- **Category-Adaptive Scoring**: Dynamically adjusts metric weights based on question category (e.g., STAR structure is prioritized for Behavioral questions; Technical Depth for Technical questions).
- **Interactive Visual Dashboard**: Plotly score gauges, radar charts, and trend analytics over time.
- **Sentence-Level Diagnostics**: Inspects each sentence individually for clarity and length.
- **PDF Report Generation**: Download evaluation reports generated locally via ReportLab.
- **SQLite History & Progress Tracking**: Persists attempts and tracks progress trends without database setup.

---

## 🛠️ Technology Stack

- **Core Frontend & App Layer**: Python 3.10+ & Streamlit
- **Semantic Model**: `sentence-transformers/all-MiniLM-L6-v2` (CPU lightweight)
- **Machine Learning & Text Analytics**: `scikit-learn`, `textstat`, `NumPy`, `pandas`
- **Data Visualization**: `Plotly`
- **Report Generation**: `ReportLab`
- **Database**: `SQLite3` (Built-in)
- **Testing**: `pytest`

> 🔒 **100% Free & Offline**: Requires NO OpenAI API keys, NO Claude API keys, NO cloud subscriptions, and NO GPU.

---

## 📐 How Scoring Works

InterviewIQ avoids random numbers or fake AI metrics. Every score (0–100) is derived from documented calculations:

$$\text{Overall Score} = \sum (\text{Component Score}_i \times \text{Category Weight}_i)$$

### Category Weight Distribution Matrix

| Category | Relevance | Clarity | Structure | Tech Depth | Conciseness | Concepts |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Behavioral** | 20% | 15% | **30% (STAR)** | 10% | 15% | 10% |
| **Technical** | 25% | 15% | 15% | **25%** | 10% | 10% |
| **Project Experience** | 20% | 15% | 25% | 20% | 10% | 10% |
| **Leadership** | 25% | 20% | 25% | 10% | 10% | 10% |
| **HR** | **30%** | 25% | 20% | 5% | 10% | 10% |
| **Problem Solving** | 20% | 15% | 25% | 20% | 10% | 10% |

---

## 🚀 Quick Start & Installation

### Option 1: Automated Launch (Windows)
Double-click `run.bat` or run in terminal:
```cmd
run.bat
```
This script will automatically:
1. Verify Python installation.
2. Create virtual environment `.venv`.
3. Activate environment and install dependencies from `requirements.txt`.
4. Launch `streamlit run app.py`.

### Option 2: Manual Setup

```bash
# 1. Clone or navigate to directory
cd InterviewIQ

# 2. Create virtual environment
python -m venv .venv

# 3. Activate environment
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run Streamlit app
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 📁 Project Structure

```
InterviewIQ/
│
├── app.py                  # Main Streamlit application and UI layout
├── database.py             # SQLite persistence layer
├── report_generator.py     # ReportLab PDF report builder
├── requirements.txt        # Lightweight Python dependencies
├── README.md               # Documentation
├── run.bat                 # Windows automated startup batch file
│
├── analyzer/               # Modular NLP & ML Analysis Package
│   ├── __init__.py
│   ├── embeddings.py       # SentenceTransformer MiniLM model loader & TF-IDF fallback
│   ├── relevance.py        # Semantic similarity & drift detection
│   ├── keyword_analysis.py # Domain concept & keyword coverage analyzer
│   ├── clarity.py          # Readability, filler word & hedging detection
│   ├── structure.py        # STAR & technical framework pattern matching
│   ├── technical_depth.py  # Reasoning keywords & metric density analyzer
│   ├── conciseness.py      # Word count optimality & repetition detection
│   ├── scoring.py          # Category-adaptive weighted scoring engine
│   └── suggestions.py      # Sentence diagnostics & template guidance generator
│
├── data/
│   └── questions.json      # Built-in question library (36 questions across 6 categories)
│
└── tests/
    └── test_analyzer.py    # Pytest unit test suite
```

---

## 🧪 Running Unit Tests

Run the test suite to verify scoring boundaries and analysis logic:

```bash
pytest tests/test_analyzer.py -v
```

---

## ⚠️ Limitations & Disclaimers

InterviewIQ provides automated natural language indicators and coaching feedback to help structure interview answers.

**What InterviewIQ Does NOT Measure:**
- It does **NOT** measure actual intelligence or cognitive capability.
- It does **NOT** assess human voice inflection, tone, or physical body language.
- It does **NOT** guarantee employment or predict job offer probability.
- It does **NOT** claim to assess psychological confidence (metrics are labeled as **Language Strength**).

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
