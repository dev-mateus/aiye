"""
FastAPI application.
Define endpoints:
  - GET /healthz - health check
  - POST /ask - responde pergunta com RAG
"""

import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models import AskRequest, AskResponse, Source
from backend.rag import search, generate_answer, load_embedder
from backend import settings


# Inicializa FastAPI
app = FastAPI(
    title="Umbanda QA API",
    description="Plataforma de tira-dúvidas sobre Umbanda baseada em RAG local-first",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Carrega embedder ao iniciar a app
@app.on_event("startup")
async def startup_event():
    """Carrega o modelo de embedding na memória ao iniciar."""
    print("🚀 Iniciando servidor...")
    try:
        load_embedder()
        print("✓ Modelo de embedding carregado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao carregar embedding: {e}")


@app.get("/healthz")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    """
    Responde uma pergunta usando RAG.
    
    Query Parameters:
      - question: a pergunta do usuário (mínimo 3 caracteres)
    
    Returns:
      - answer: resposta gerada a partir dos contextos
      - sources: lista de fontes citadas
      - meta: metadados (latência, top_k, etc.)
    """
    start_time = time.time()
    
    try:
        # Validação básica
        question = request.question.strip()
        if len(question) < 3:
            raise HTTPException(
                status_code=400,
                detail="A pergunta deve ter pelo menos 3 caracteres"
            )
        
        # Busca contextos relevantes
        contexts = search(
            query=question,
            top_k=settings.TOP_K,
            min_sim=settings.MIN_SIM
        )
        
        # Gera resposta
        answer = generate_answer(question, contexts)
        
        # Se resposta padrão de não encontrado, não retorna fontes
        resposta_padrao = "Não encontrei essa informação no acervo, entre em contato com o administrador da plataforma."
        if answer.strip() == resposta_padrao:
            sources = []
        else:
            # Monta lista de fontes únicas normalmente
            sources_dict = {}
            for ctx in contexts:
                key = (ctx["title"], ctx["page_start"], ctx["page_end"], ctx["uri"])
                if key not in sources_dict:
                    sources_dict[key] = ctx["score"]
            sources = [
                Source(
                    title=title,
                    page_start=page_start,
                    page_end=page_end,
                    uri=uri,
                    score=score
                )
                for (title, page_start, page_end, uri), score in sources_dict.items()
            ]
        # Metadados
        elapsed = time.time() - start_time
        meta = {
            "latency_ms": round(elapsed * 1000, 2),
            "top_k": settings.TOP_K,
            "min_sim": settings.MIN_SIM,
            "num_contexts": len(contexts)
        }
        return AskResponse(
            answer=answer,
            sources=sources,
            meta=meta
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ Erro ao processar pergunta: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar pergunta: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info"
    )
