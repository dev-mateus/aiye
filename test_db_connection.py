import psycopg2
import os

# Testar várias configurações de conexão
configs = [
    ("Com sslmode=require", "postgresql://***REDACTED***"),
    ("Com sslmode=prefer", "postgresql://neondb_owner:npg_CHtQo6Uk9LEa@ep-polished-truth-ae0kk3zf.c-2.us-east-2.aws.neon.tech/neondb?sslmode=prefer"),
    ("Sem sslmode", "postgresql://neondb_owner:npg_CHtQo6Uk9LEa@ep-polished-truth-ae0kk3zf.c-2.us-east-2.aws.neon.tech/neondb"),
]

for name, url in configs:
    print(f"\n{'='*60}")
    print(f"Testando: {name}")
    print(f"{'='*60}")
    
    try:
        conn = psycopg2.connect(url, connect_timeout=10)
        print("✓ Conexão estabelecida!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✓ PostgreSQL: {version[0][:60]}...")
        
        # Testar criar tabela
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                message TEXT
            )
        """)
        print("✓ Tabela de teste criada!")
        
        cursor.execute("DROP TABLE test_connection")
        print("✓ Tabela de teste removida!")
        
        cursor.close()
        conn.close()
        print(f"\n✅ SUCESSO com: {name}\n")
        break
        
    except Exception as e:
        print(f"✗ Falhou: {str(e)[:100]}...")
        continue
