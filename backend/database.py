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

def get_filtered_feedbacks(
    rating: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
    order_by: str = "timestamp",
    order_dir: str = "DESC"
) -> Dict[str, Any]:
    """
    Retorna feedbacks filtrados com paginação avançada.
    
    Args:
        rating: Filtrar por rating específico (1-5)
        start_date: Data inicial (formato ISO: YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS)
        end_date: Data final (formato ISO)
        search: Busca por texto em question ou comment
        limit: Número máximo de resultados
        offset: Offset para paginação
        order_by: Campo para ordenação (timestamp, rating, id)
        order_dir: Direção da ordenação (ASC, DESC)
    
    Returns:
        Dict com total, feedbacks e informações de paginação
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Construir query dinâmica
        conditions = []
        params = []
        
        if rating is not None:
            conditions.append("rating = %s")
            params.append(rating)
        
        if start_date:
            conditions.append("timestamp >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("timestamp <= %s")
            params.append(end_date)
        
        if search:
            conditions.append("(question ILIKE %s OR comment ILIKE %s)")
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern])
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Validar order_by e order_dir para evitar SQL injection
        valid_order_by = ["timestamp", "rating", "id", "created_at"]
        valid_order_dir = ["ASC", "DESC"]
        
        if order_by not in valid_order_by:
            order_by = "timestamp"
        if order_dir.upper() not in valid_order_dir:
            order_dir = "DESC"
        
        # Contar total de resultados
        count_query = f"SELECT COUNT(*) as total FROM feedbacks WHERE {where_clause}"
        cursor.execute(count_query, params)
        count_result = cursor.fetchone()
        total = count_result['total'] if count_result else 0
        
        # Buscar feedbacks
        query = f"""
            SELECT id, timestamp, question, answer, rating, comment, created_at
            FROM feedbacks
            WHERE {where_clause}
            ORDER BY {order_by} {order_dir}
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        cursor.execute(query, params)
        feedbacks = [dict(row) for row in cursor.fetchall()]
        
        return {
            "total": total,
            "feedbacks": feedbacks,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }

def get_feedback_stats_by_period(period: str = "7d") -> Dict[str, Any]:
    """
    Retorna estatísticas de feedbacks por período.
    
    Args:
        period: Período para análise (7d, 30d, 90d, all)
    
    Returns:
        Dict com estatísticas agregadas
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Construir cláusula de período
        period_clause = ""
        if period == "7d":
            period_clause = "WHERE timestamp >= NOW() - INTERVAL '7 days'"
        elif period == "30d":
            period_clause = "WHERE timestamp >= NOW() - INTERVAL '30 days'"
        elif period == "90d":
            period_clause = "WHERE timestamp >= NOW() - INTERVAL '90 days'"
        
        # Estatísticas gerais
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total,
                AVG(rating) as avg_rating,
                COUNT(CASE WHEN rating = 5 THEN 1 END) as rating_5,
                COUNT(CASE WHEN rating = 4 THEN 1 END) as rating_4,
                COUNT(CASE WHEN rating = 3 THEN 1 END) as rating_3,
                COUNT(CASE WHEN rating = 2 THEN 1 END) as rating_2,
                COUNT(CASE WHEN rating = 1 THEN 1 END) as rating_1,
                COUNT(CASE WHEN comment IS NOT NULL AND comment != '' THEN 1 END) as with_comments
            FROM feedbacks
            {period_clause}
        """)
        result = cursor.fetchone()
        stats = dict(result) if result else {
            "total": 0,
            "avg_rating": 0,
            "rating_5": 0,
            "rating_4": 0,
            "rating_3": 0,
            "rating_2": 0,
            "rating_1": 0,
            "with_comments": 0
        }
        
        # Feedbacks recentes (últimos 10)
        cursor.execute(f"""
            SELECT id, timestamp, question, rating, comment
            FROM feedbacks
            {period_clause}
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        recent = [dict(row) for row in cursor.fetchall()]
        
        return {
            "period": period,
            "stats": stats,
            "recent_feedbacks": recent
        }
