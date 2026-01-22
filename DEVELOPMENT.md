# DESENVOLVIMENTO

## Estrutura do Projeto

```
umbanda-qa/
├── backend/                          # FastAPI + RAG
│   ├── main.py                      # App FastAPI (endpoints /healthz, /ask)
│   ├── rag.py                       # Lógica RAG (embeddings, busca, resposta)
│   ├── models.py                    # Modelos Pydantic (AskRequest, AskResponse)
│   ├── settings.py                  # Configurações (carrega .env)
│   ├── ingest.py                    # Script CLI para ingerir PDFs
│   ├── requirements.txt              # Dependências Python
│   ├── __init__.py                  # Init do package
│   └── data/
│       ├── pdfs/                    # PDFs para ingestão
│       └── index/                   # Índices FAISS + metadata.json
│
├── frontend/                        # React + Vite + TypeScript
│   ├── src/
│   │   ├── main.tsx                # Entrada React
│   │   ├── App.tsx                 # Componente raiz
│   │   ├── api.ts                  # Client HTTP
│   │   ├── styles.css              # Tailwind + custom
│   │   └── components/
│   │       ├── ChatBox.tsx         # Input + botão
│   │       ├── AnswerCard.tsx      # Exibe resposta
│   │       └── SourceList.tsx      # Lista de fontes
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── index.html
│
├── .env.example                     # Variáveis de exemplo
├── .gitignore
├── README.md                        # Documentação principal
├── QUICKSTART.md                    # Guia de início rápido
└── DEVELOPMENT.md                   # Este arquivo
```

## Fluxo de RAG

### 1. Ingestão (backend/ingest.py)

```python
python backend/ingest.py
```

- Lê PDFs de `backend/data/pdfs/`
- Extrai texto com PyMuPDF
- Divide em chunks (~1200 chars, overlap ~150 chars)
- Gera embeddings com SentenceTransformer
- Salva índice FAISS: `backend/data/index/index.faiss`
- Salva metadados: `backend/data/index/metadata.json`

### 2. Query (backend/main.py POST /ask)

```python
POST /ask
{
  "question": "O que é Umbanda?"
}
```

- Recebe pergunta do usuário
- Valida (mínimo 3 caracteres)
- Embeda pergunta
- Busca top-5 chunks mais similares no FAISS
- Filtra por min_similarity (0.25)
- Expansão de query: por padrão usa apenas sinônimos controlados (LLM desativado)
- Chama `generate_answer()` com contextos
- Retorna resposta + fontes + metadados

### 3. Resposta (backend/rag.py generate_answer)

```python
def generate_answer(question: str, contexts: list[dict]) -> str:
    # Atualmente: concatena contextos + aviso ético
    # TODO: Integrar com LLM externo (Copilot/M365/OpenAI)
```

Placeholder que:
- Agrupa contextos por documento
- Monta resposta legível
- Adiciona aviso ético
- Retorna string formatada

## Modificações Comuns

### Adicionar novo endpoint

Em `backend/main.py`:

```python
@app.post("/novo-endpoint")
async def novo_endpoint(request: SomeRequest) -> SomeResponse:
    # Implementar lógica
    return response
```

### Integrar com LLM

Em `backend/rag.py`, substitua `generate_answer()`:

```python
def generate_answer(question: str, contexts: list[dict]) -> str:
    # Montar prompt
    prompt = f"Pergunta: {question}\n\nContextos:\n"
    for ctx in contexts:
        prompt += f"- {ctx['content']}\n"
    
    # Chamar LLM externo
    # response = call_copilot_api(prompt)
    # response = call_openai_api(prompt)
    # return response
    
    # Por enquanto, placeholder
    return gerar_resposta_placeholder(contexts)

### Feature Flag: Expansão de Query via LLM

- Estado atual (jan/2026): DESATIVADA por padrão para reforçar grounding no acervo.
- Controle via `.env`:

```
ENABLE_LLM_EXPANSION=false  # padrão
```

- Comportamento:
    - `false`: apenas `expand_query_with_synonyms()` é usado
    - `true`: `expand_query_with_llm()` é habilitado com prompt restritivo e filtros locais
- Código:
    - `backend/settings.py`: lê `ENABLE_LLM_EXPANSION`
    - `backend/rag.py`: `get_query_expander(use_llm=settings.ENABLE_LLM_EXPANSION, use_synonyms=True)`
    - `backend/query_expansion.py`: default `use_llm=settings.ENABLE_LLM_EXPANSION`
```

### Mudar tamanho de chunks

Em `backend/rag.py`, função `chunk_text()`:

```python
def chunk_text(
    pages: list[str],
    chunk_size: int = 1500,  # Aumentar de 1200
    overlap: int = 200       # Aumentar de 150
) -> list[dict]:
    # ...
```

### Mudar modelo de embedding

Em `.env`:

```
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

Nota: Modelos diferentes têm dimensionalidades diferentes. Verifique antes de usar!

### Ajustar TOP_K e MIN_SIM

Em `.env`:

```
TOP_K=10              # Buscar top-10 ao invés de 5
MIN_SIM=0.35          # Aumentar threshold de similaridade
```

## Testing & Debugging

### Verificar saúde do backend

```bash
curl http://localhost:8000/healthz
```

### Acessar documentação automática

```
http://localhost:8000/docs       # Swagger UI
http://localhost:8000/redoc      # ReDoc
```

### Testar endpoint /ask

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é Umbanda?"}'

Logs esperados (com LLM expansion desativada):
- `🔄 Query Expansion: 1 query → N queries` (sinônimos apenas)
- `🔍 Dense Search: X resultados únicos`
```

### Verificar índice FAISS

```python
# Em Python REPL
import faiss
index = faiss.read_index("backend/data/index/index.faiss")
print(f"Vetores no índice: {index.ntotal}")
```

### Verificar metadados

```python
import json
with open("backend/data/index/metadata.json") as f:
    meta = json.load(f)
    print(f"Docs: {len(meta['documents'])}")
    print(f"Chunks: {len(meta['chunks'])}")
```

## Performance & Optimization

### Índices FAISS
- `IndexFlatIP`: O mais simples, busca exaustiva (atual)
- `IndexIVF`: Mais rápido para grandes datasets
- `IndexHNSW`: Aproximado, muito rápido

### Modelos de Embedding
- `all-MiniLM-L6-v2`: 384 dims, leve, rápido (atual)
- `all-mpnet-base-v2`: 768 dims, melhor qualidade
- `all-distilroberta-v1`: 768 dims, bom custo-benefício

### Otimizações
1. Cache do embedder (já implementado)
2. Normalização L2 para cosine similarity
3. Filtro min_sim para reduzir ruído
4. Chunk overlap para continuidade

## Dependências & Versões

### Backend
- FastAPI 0.115.0 - Framework web
- Uvicorn 0.30.0 - ASGI server
- Pydantic 2.9.2 - Validação
- FAISS 1.8.0 - Busca vetorial
- SentenceTransformers 3.0.1 - Embeddings
- PyMuPDF 1.24.9 - PDF parsing
- Python-dotenv 1.0.1 - .env loader

### Frontend
- React 18.2 - UI library
- TypeScript 5.0 - Type safety
- Vite 5.0 - Build tool
- Tailwind 3.3 - Styling
- TanStack Query 5.0 - State management

## Git Workflow

```bash
# Clone
git clone <repo>
cd umbanda-qa

# Create .env
cp .env.example .env

# Backend setup
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt

# Frontend setup
cd frontend
npm install
cd ..

# Run
# Terminal 1:
uvicorn backend.main:app --reload

# Terminal 2:
cd frontend && npm run dev
```

## Contributing

1. Fork/Clone
2. Create feature branch
3. Make changes
4. Test locally
5. Commit & push
6. Open PR

## Resources

- FastAPI: https://fastapi.tiangolo.com/
- FAISS: https://github.com/facebookresearch/faiss
- SentenceTransformers: https://www.sbert.net/
- React: https://react.dev/
- Vite: https://vitejs.dev/
- Tailwind: https://tailwindcss.com/

## License

MIT (ou conforme preferir)

---

**Last Updated:** Novembro 2025
