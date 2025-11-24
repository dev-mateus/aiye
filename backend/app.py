"""
FastAPI application for Hugging Face Spaces.
Define endpoints:
  - GET /healthz - health check
  - POST /ask - responde pergunta com RAG
  - GET /warmup - pre-loads embedding model
"""

import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.models import AskRequest, AskResponse, Source
from backend.rag import search, generate_answer, load_embedder
from backend import settings

# Inicializa FastAPI
app = FastAPI(
    title="Aiye API",
    description="Plataforma de perguntas sobre Umbanda baseada em RAG com Google Gemini",
    version="1.0.0"
)

# Configurar CORS (simplificado para evitar problemas)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite qualquer origem
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/warmup")
async def warmup():
    """Pre-loads the embedding model. Call this after deployment to warm up the backend."""
    try:
        load_embedder()
        return {"status": "ready", "message": "Embedding model loaded successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    """Responde uma pergunta usando RAG."""
    start_time = time.time()
    try:
        question = request.question.strip()
        if len(question) < 3:
            raise HTTPException(status_code=400, detail="A pergunta deve ter pelo menos 3 caracteres")

        contexts = search(query=question, top_k=settings.TOP_K, min_sim=settings.MIN_SIM)
        answer = generate_answer(question, contexts)

        resposta_padrao = "Não encontrei essa informação no acervo, entre em contato com o administrador da plataforma."
        if answer.strip() == resposta_padrao:
            sources = []
        else:
            sources_dict = {}
            for ctx in contexts:
                key = (ctx["title"], ctx["page_start"], ctx["page_end"], ctx["uri"])
                if key not in sources_dict:
                    sources_dict[key] = ctx["score"]
            sources = [
                Source(title=title, page_start=page_start, page_end=page_end, uri=uri, score=score)
                for (title, page_start, page_end, uri), score in sources_dict.items()
            ]

        elapsed = time.time() - start_time
        meta = {
            "latency_ms": round(elapsed * 1000, 2),
            "top_k": settings.TOP_K,
            "min_sim": settings.MIN_SIM,
            "num_contexts": len(contexts)
        }
        return AskResponse(answer=answer, sources=sources, meta=meta)

    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ Erro ao processar pergunta: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")

@app.post("/ask-raw", response_model=AskResponse)
async def ask_raw(request: Request) -> AskResponse:
    """Fallback endpoint que lê JSON bruto."""
    start_time = time.time()
    try:
        body = await request.json()
    except Exception as e:
        print(f"✗ Erro ao ler JSON bruto: {e}")
        raise HTTPException(status_code=400, detail=f"JSON inválido: {e}")

    try:
        question = str(body.get("question", "")).strip()
        if len(question) < 3:
            raise HTTPException(status_code=400, detail="A pergunta deve ter pelo menos 3 caracteres")

        contexts = search(query=question, top_k=settings.TOP_K, min_sim=settings.MIN_SIM)
        answer = generate_answer(question, contexts)

        resposta_padrao = "Não encontrei essa informação no acervo, entre em contato com o administrador da plataforma."
        if answer.strip() == resposta_padrao:
            sources = []
        else:
            sources_dict = {}
            for ctx in contexts:
                key = (ctx["title"], ctx["page_start"], ctx["page_end"], ctx["uri"])
                if key not in sources_dict:
                    sources_dict[key] = ctx.get("score")
            sources = [
                Source(title=title, page_start=page_start, page_end=page_end, uri=uri, score=score)
                for (title, page_start, page_end, uri), score in sources_dict.items()
            ]

        elapsed = time.time() - start_time
        meta = {
            "latency_ms": round(elapsed * 1000, 2),
            "top_k": settings.TOP_K,
            "min_sim": settings.MIN_SIM,
            "num_contexts": len(contexts)
        }

        return AskResponse(answer=answer, sources=sources, meta=meta)

    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ Erro ao processar pergunta (raw): {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {e}")

# Ajuste para Hugging Face Spaces: porta padrão 7860
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")
