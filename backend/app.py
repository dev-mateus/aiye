"""
FastAPI application for Hugging Face Spaces.
Define endpoints:
  - GET /healthz - health check
  - POST /ask - responde pergunta com RAG
  - GET /warmup - pre-loads embedding model
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.models import AskRequest, AskResponse, Source, FeedbackRequest
from backend.rag import ask_with_cache, load_embedder
from backend.cache import get_response_cache
from backend import settings
from backend.database import init_database, save_feedback, get_all_feedbacks, get_feedback_stats, get_filtered_feedbacks, get_feedback_stats_by_period

# Lifespan para inicialização
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        init_database()
        print("✓ Banco de dados inicializado")
    except Exception as e:
        print(f"⚠️ Erro ao inicializar banco: {e}")
        print("Sistema continuará funcionando, mas feedbacks podem não ser salvos")
    yield
    # Shutdown (se necessário)

# Inicializa FastAPI
app = FastAPI(
    title="Aiye API",
    description="Plataforma de perguntas sobre Umbanda baseada em RAG com Google Gemini",
    version="1.0.0",
    lifespan=lifespan
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

@app.get("/cache/stats")
async def cache_stats():
    """Retorna estatísticas do cache de respostas."""
    cache = get_response_cache()
    return cache.stats()

@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    """Responde uma pergunta usando RAG com cache e re-ranking."""
    start_time = time.time()
    try:
        question = request.question.strip()
        if len(question) < 3:
            raise HTTPException(status_code=400, detail="A pergunta deve ter pelo menos 3 caracteres")

        # Usa a função integrada com cache e re-ranking
        answer, contexts = ask_with_cache(
            question=question,
            top_k=settings.TOP_K,
            min_sim=settings.MIN_SIM,
            use_cache=True,
            use_reranking=True
        )

        resposta_padrao = "Não encontrei essa informação no acervo, entre em contato com o administrador da plataforma."
        resposta_nao_encontrada = "Os documentos disponíveis tratam de"
        
        # Não retorna fontes quando não houver resposta válida
        if answer.strip() == resposta_padrao or resposta_nao_encontrada in answer:
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
    """Fallback endpoint que lê JSON bruto com cache e re-ranking."""
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

        # Usa a função integrada com cache e re-ranking
        answer, contexts = ask_with_cache(
            question=question,
            top_k=settings.TOP_K,
            min_sim=settings.MIN_SIM,
            use_cache=True,
            use_reranking=True
        )

        resposta_padrao = "Não encontrei essa informação no acervo, entre em contato com o administrador da plataforma."
        resposta_nao_encontrada = "Os documentos disponíveis tratam de"
        
        # Não retorna fontes quando não houver resposta válida
        if answer.strip() == resposta_padrao or resposta_nao_encontrada in answer:
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

@app.post("/feedback", status_code=200)
async def submit_feedback(feedback: FeedbackRequest):
    """Endpoint para receber avaliações (1-5 estrelas) das respostas."""
    try:
        result = save_feedback(
            question=feedback.question,
            answer=feedback.answer,
            rating=feedback.rating,
            comment=feedback.comment
        )
        print(f"✓ Feedback recebido: {feedback.rating} estrelas (ID: {result.get('id')})")
        return {"status": "success", "message": "Feedback salvo com sucesso", "id": result.get('id')}
    except Exception as e:
        print(f"✗ Erro ao salvar feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar feedback: {str(e)}"
        )

@app.get("/feedbacks")
async def list_feedbacks(limit: int = 100, offset: int = 0):
    """Lista todos os feedbacks salvos (apenas para admin/debug)."""
    try:
        feedbacks = get_all_feedbacks(limit=limit, offset=offset)
        stats = get_feedback_stats()
        
        return {
            "total": stats.get('total', 0),
            "avg_rating": round(float(stats.get('avg_rating', 0)), 2),
            "positive": stats.get('positive', 0),
            "negative": stats.get('negative', 0),
            "feedbacks": feedbacks,
            "pagination": {
                "limit": limit,
                "offset": offset
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/feedbacks")
async def admin_feedbacks(
    rating: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
    order_by: str = "timestamp",
    order_dir: str = "DESC"
):
    """
    Endpoint admin com filtros avançados para análise de feedbacks.
    
    Query params:
        - rating: Filtrar por rating específico (1-5)
        - start_date: Data inicial (YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS)
        - end_date: Data final (YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS)
        - search: Busca por texto em pergunta ou comentário
        - limit: Número de resultados por página (default: 50)
        - offset: Offset para paginação (default: 0)
        - order_by: Campo para ordenar (timestamp, rating, id, created_at)
        - order_dir: Direção (ASC, DESC)
    """
    try:
        result = get_filtered_feedbacks(
            rating=rating,
            start_date=start_date,
            end_date=end_date,
            search=search,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_dir=order_dir
        )
        return result
    except Exception as e:
        print(f"✗ Erro ao buscar feedbacks filtrados: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/feedbacks/stats")
async def admin_feedback_stats(period: str = "7d"):
    """
    Retorna estatísticas detalhadas de feedbacks por período.
    
    Query params:
        - period: Período para análise (7d, 30d, 90d, all)
    """
    try:
        valid_periods = ["7d", "30d", "90d", "all"]
        if period not in valid_periods:
            raise HTTPException(
                status_code=400,
                detail=f"Período inválido. Use: {', '.join(valid_periods)}"
            )
        
        stats = get_feedback_stats_by_period(period=period)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        print(f"✗ Erro ao buscar estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Ajuste para Hugging Face Spaces: porta padrão 7860
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")
