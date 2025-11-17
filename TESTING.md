"""
EXEMPLO DE USO - TESTE RÁPIDO

Este arquivo demonstra como usar o sistema sem PDFs reais.
"""

# ============================================================================
# 1. TESTE RÁPIDO (sem PDFs)
# ============================================================================

# Opção A: Testar apenas o backend (sem frontend)

# Terminal 1:
# cd umbanda-qa
# .venv\Scripts\activate
# uvicorn backend.main:app --reload --port 8000

# Terminal 2:
# curl -X POST http://localhost:8000/ask \
#   -H "Content-Type: application/json" \
#   -d '{"question": "O que e Umbanda?"}'

# Resultado esperado:
# {
#   "answer": "Desculpe, não encontrei informações...",
#   "sources": [],
#   "meta": {...}
# }


# ============================================================================
# 2. TESTE COM PDFs
# ============================================================================

# 1. Colocar PDFs em: backend/data/pdfs/
#    Ex: backend/data/pdfs/introducao_umbanda.pdf

# 2. Executar ingestão:
# python backend/ingest.py

# Esperado:
# ✓ Extraído texto de N páginas: backend/data/pdfs/introducao_umbanda.pdf
#   → M chunks criados
#   → M embeddings adicionados ao índice
# ✓ Índice FAISS salvo: backend/data/index/index.faiss
# ✓ Metadados salvos: backend/data/index/metadata.json
#
# ============════════════════════════════════════════════
# ✅ INGESTÃO CONCLUÍDA
# ============════════════════════════════════════════════
#   📚 Documentos: 1
#   📦 Chunks: M
#   📍 Índice: backend/data/index/index.faiss
#   📋 Metadados: backend/data/index/metadata.json

# 3. Testar novamente:
# curl -X POST http://localhost:8000/ask \
#   -H "Content-Type: application/json" \
#   -d '{"question": "O que e Umbanda?"}'

# Esperado:
# {
#   "answer": "Segundo o acervo... [resposta baseada no PDF]",
#   "sources": [
#     {
#       "title": "introducao_umbanda",
#       "page_start": 1,
#       "page_end": 3,
#       "uri": "backend/data/pdfs/introducao_umbanda.pdf",
#       "score": 0.75
#     }
#   ],
#   "meta": {
#     "latency_ms": 145,
#     "top_k": 5,
#     "min_sim": 0.25,
#     "num_contexts": 2
#   }
# }


# ============================================================================
# 3. TESTE COM FRONTEND
# ============================================================================

# Terminal 1: Backend (já rodando)
# uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend
# cd frontend
# npm run dev

# Abrir: http://localhost:5173
# Digitar pergunta e enviar


# ============================================================================
# 4. TESTE COM CURL (backend)
# ============================================================================

# Health check:
# curl http://localhost:8000/healthz
# {"status":"ok"}

# Pergunta:
# curl -X POST http://localhost:8000/ask \
#   -H "Content-Type: application/json" \
#   -d '{"question": "Como funciona a Umbanda?"}'

# Pergunta curta (erro):
# curl -X POST http://localhost:8000/ask \
#   -H "Content-Type: application/json" \
#   -d '{"question": "Oi"}'
# {"detail":"A pergunta deve ter pelo menos 3 caracteres"}

# Documentação interativa:
# http://localhost:8000/docs


# ============================================================================
# 5. TESTE DE PERFORMANCE
# ============================================================================

import time
import requests

API_URL = "http://localhost:8000"

def test_latency():
    """Testa latência do sistema"""
    questions = [
        "O que é Umbanda?",
        "Quem são os Orixás?",
        "Como fazer uma ofenda?",
    ]
    
    for q in questions:
        start = time.time()
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": q}
        )
        latency = (time.time() - start) * 1000
        
        if response.ok:
            data = response.json()
            print(f"✓ {q}")
            print(f"  Latência: {latency:.0f}ms")
            print(f"  Contextos: {data['meta']['num_contexts']}")
            print(f"  Fontes: {len(data['sources'])}")
        else:
            print(f"✗ {q}: {response.status_code}")
        print()

# Rodar teste:
# python backend/test_example.py


# ============================================================================
# 6. INTEGRAÇÃO COM LLM (Exemplo - não implementado)
# ============================================================================

# Para integrar com OpenAI, edite backend/rag.py:

# import openai
# 
# def generate_answer(question: str, contexts: list[dict]) -> str:
#     # Montar prompt
#     context_text = "\n\n".join([ctx['content'] for ctx in contexts])
#     
#     prompt = f"""
#     Baseado nos seguintes trechos de um acervo sobre Umbanda, responda à pergunta.
#     Mantenha a resposta concisa e cite as fontes.
#     
#     Contextos:
#     {context_text}
#     
#     Pergunta: {question}
#     
#     Responda em português do Brasil.
#     """
#     
#     # Chamar OpenAI
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.7
#     )
#     
#     return response.choices[0].message.content


# ============================================================================
# 7. ADICIONAR MAIS PDFs
# ============================================================================

# Processo:
# 1. Colocar novos PDFs em backend/data/pdfs/
# 2. Executar novamente: python backend/ingest.py
# 3. O sistema automaticamente:
#    - Extrai texto
#    - Cria chunks
#    - Gera embeddings
#    - Adiciona ao índice existente
#    - Atualiza metadados

# Resultado:
# ✓ Extraído texto de N páginas: backend/data/pdfs/novo_pdf.pdf
#   → M chunks criados
#   → M embeddings adicionados ao índice


# ============================================================================
# 8. CUSTOMIZAÇÕES
# ============================================================================

# Editar .env para:
# - TOP_K: quantos chunks buscar (default 5)
# - MIN_SIM: threshold de similaridade (default 0.25)
# - EMBEDDING_MODEL: modelo diferente
# - PORT: porta do servidor

# Editar backend/rag.py para:
# - CHUNK_SIZE: tamanho dos chunks (default 1200)
# - OVERLAP: overlap entre chunks (default 150)
# - Lógica de geração de resposta


# ============================================================================
# 9. ESTRUTURA DE ERRO COMUM
# ============================================================================

# ImportError: No module named 'fastapi'
# → Confirmar que .venv está ativado
# → pip install -r backend/requirements.txt

# Port already in use
# → Mudar PORT em .env
# → Ou matar processo na porta: taskkill /PID <pid> /F

# No such file: backend/data/pdfs
# → Pasta será criada automaticamente

# FAISS index is empty
# → Executar python backend/ingest.py com PDFs em backend/data/pdfs/

# CORS error in frontend
# → Verificar VITE_API_BASE em frontend/.env.local
# → Confirmar que backend está rodando


print("Tudo pronto para testar! 🎉")
print("\nPróximos passos:")
print("1. python -m venv .venv")
print("2. .venv\\Scripts\\activate")
print("3. pip install -r backend/requirements.txt")
print("4. uvicorn backend.main:app --reload")
print("5. cd frontend && npm install && npm run dev")
