import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("⚠️ ERRO: DATABASE_URL não configurada!")
    print("")
    print("Configure a variável de ambiente DATABASE_URL no arquivo .env:")
    print("DATABASE_URL=postgresql://user:password@host.region.neon.tech/db?sslmode=require")
    print("")
    print("Obtenha a connection string em: https://console.neon.tech")
    exit(1)

# Testar conexão com a configuração do .env
configs = [
    ("Configuração do .env", DATABASE_URL),
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
