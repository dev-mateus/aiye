"""
Script para verificar tamanho real da tabela feedbacks no PostgreSQL.
"""
import psycopg2
import os
from typing import Optional

DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://***REDACTED***"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("ANÁLISE DE TAMANHO DO BANCO DE DADOS")
    print("="*60 + "\n")
    
    # Tamanho total do banco
    cursor.execute("""
        SELECT pg_size_pretty(pg_database_size(current_database())) as size;
    """)
    result = cursor.fetchone()
    db_size = result[0] if result else "Desconhecido"
    print(f"📊 Tamanho total do banco: {db_size}")
    
    # Tamanho da tabela feedbacks
    cursor.execute("""
        SELECT 
            pg_size_pretty(pg_total_relation_size('feedbacks')) as total_size,
            pg_size_pretty(pg_relation_size('feedbacks')) as table_size,
            pg_size_pretty(pg_indexes_size('feedbacks')) as indexes_size
    """)
    result = cursor.fetchone()
    if result:
        print(f"\n📋 Tabela 'feedbacks':")
        print(f"   Total (tabela + índices): {result[0]}")
        print(f"   Apenas dados da tabela: {result[1]}")
        print(f"   Apenas índices: {result[2]}")
    else:
        print("\n⚠️ Tabela 'feedbacks' não encontrada")
    
    # Número de linhas
    cursor.execute("SELECT COUNT(*) FROM feedbacks")
    result = cursor.fetchone()
    count = result[0] if result else 0
    print(f"   Número de registros: {count}")
    
    # Listar todas as tabelas e seus tamanhos
    cursor.execute("""
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
        FROM pg_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
    """)
    
    print(f"\n📁 Todas as tabelas no banco:")
    for row in cursor.fetchall():
        print(f"   {row[0]}.{row[1]}: {row[2]}")
    
    # Tamanho médio por feedback
    if count > 0:
        cursor.execute("SELECT pg_relation_size('feedbacks')")
        result = cursor.fetchone()
        if result and result[0]:
            table_bytes = result[0]
            avg_bytes = table_bytes / count
            print(f"\n💾 Tamanho médio por feedback: {avg_bytes:.0f} bytes ({avg_bytes/1024:.2f} KB)")
            print(f"   Capacidade com 500 MB: ~{int(500*1024*1024/avg_bytes):,} feedbacks")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60 + "\n")
    
except Exception as e:
    print(f"Erro: {e}")
