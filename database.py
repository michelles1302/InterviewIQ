import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "interviewiq.db"

def get_connection():
    """
    Returns a SQLite connection object.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the SQLite database and creates tables if they do not exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            question_id TEXT,
            question_text TEXT,
            category TEXT,
            difficulty TEXT,
            answer_text TEXT,
            overall_score REAL,
            relevance_score REAL,
            clarity_score REAL,
            structure_score REAL,
            technical_depth_score REAL,
            conciseness_score REAL,
            concept_coverage_score REAL,
            strengths_json TEXT,
            improvements_json TEXT,
            full_analysis_json TEXT
        );
    """)
    conn.commit()
    conn.close()


def save_attempt(
    question_id: str,
    question_text: str,
    category: str,
    difficulty: str,
    answer_text: str,
    overall_score: float,
    relevance_score: float,
    clarity_score: float,
    structure_score: float,
    technical_depth_score: float,
    conciseness_score: float,
    concept_coverage_score: float,
    strengths: List[str],
    improvements: List[str],
    full_analysis: Dict[str, Any]
) -> int:
    """
    Saves an interview practice attempt into SQLite database.
    Returns inserted attempt ID.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO attempts (
            timestamp, question_id, question_text, category, difficulty, answer_text,
            overall_score, relevance_score, clarity_score, structure_score,
            technical_depth_score, conciseness_score, concept_coverage_score,
            strengths_json, improvements_json, full_analysis_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp, question_id, question_text, category, difficulty, answer_text,
        overall_score, relevance_score, clarity_score, structure_score,
        technical_depth_score, conciseness_score, concept_coverage_score,
        json.dumps(strengths), json.dumps(improvements), json.dumps(full_analysis)
    ))
    
    conn.commit()
    attempt_id = cursor.lastrowid
    conn.close()
    return attempt_id


def get_all_attempts() -> List[Dict[str, Any]]:
    """
    Fetches all historical attempts sorted by timestamp descending.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attempts ORDER BY id DESC")
    rows = cursor.fetchall()
    
    attempts = []
    for r in rows:
        d = dict(r)
        d["strengths"] = json.loads(d.get("strengths_json", "[]"))
        d["improvements"] = json.loads(d.get("improvements_json", "[]"))
        d["full_analysis"] = json.loads(d.get("full_analysis_json", "{}"))
        attempts.append(d)
        
    conn.close()
    return attempts


def get_attempt_by_id(attempt_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetches a single attempt by ID.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attempts WHERE id = ?", (attempt_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        d = dict(row)
        d["strengths"] = json.loads(d.get("strengths_json", "[]"))
        d["improvements"] = json.loads(d.get("improvements_json", "[]"))
        d["full_analysis"] = json.loads(d.get("full_analysis_json", "{}"))
        return d
    return None


def delete_attempt(attempt_id: int) -> bool:
    """
    Deletes an attempt by ID.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attempts WHERE id = ?", (attempt_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0
