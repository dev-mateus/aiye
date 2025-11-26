"""
Database module for PostgreSQL (Neon) integration.
Handles feedback storage in persistent database.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import List, Dict, Any

DATABASE_URL = os.getenv("DATABASE_URL")

@contextmanager
def get_db_connection():
    """Context manager para conexão com PostgreSQL."""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def init_database():
    """Cria a tabela de feedbacks se não existir."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT NOW(),
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_feedbacks_timestamp ON feedbacks(timestamp);
            CREATE INDEX IF NOT EXISTS idx_feedbacks_rating ON feedbacks(rating);
        """)
        print("✓ Tabela de feedbacks criada/verificada com sucesso")

def save_feedback(question: str, answer: str, rating: int, comment: str | None = None) -> Dict[str, Any]:
    """Salva um feedback no banco de dados."""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            INSERT INTO feedbacks (question, answer, rating, comment)
            VALUES (%s, %s, %s, %s)
            RETURNING id, timestamp
        """, (question, answer, rating, comment))
        result = cursor.fetchone()
        return dict(result) if result else {}

def get_all_feedbacks(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """Retorna todos os feedbacks com paginação."""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, timestamp, question, answer, rating, comment
            FROM feedbacks
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        return [dict(row) for row in cursor.fetchall()]

def get_feedback_stats() -> Dict[str, Any]:
    """Retorna estatísticas dos feedbacks."""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(rating) as avg_rating,
                COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive,
                COUNT(CASE WHEN rating <= 2 THEN 1 END) as negative
            FROM feedbacks
        """)
        result = cursor.fetchone()
        return dict(result) if result else {"total": 0, "avg_rating": 0, "positive": 0, "negative": 0}
