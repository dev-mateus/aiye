# Copilot Instructions for Aiye

Aiye é uma plataforma RAG (Retrieval-Augmented Generation) para perguntas sobre Umbanda que combina embeddings vetoriais, busca semântica e Google Gemini 2.5 Flash.

## 🏗️ Arquitetura

**Frontend (React 18.2 + TypeScript 5.0 + Vite 5.0 + Tailwind 3.3)**
- Deployed em Vercel
- Cliente HTTP via Axios (`src/api.ts`)
- Componentes: ChatBox, AnswerCard, SourceList
- Health check do backend no mount

**Backend (FastAPI 0.115.0 + Python 3.11 + Docker)**
- Deployed em Hugging Face Spaces (porta 7860)
- 3 endpoints: `/healthz`, `/warmup`, `/ask`
- RAG pipeline: Search (FAISS + BM25 híbrido) → Re-ranking → Gemini
- Local-first: Respostas APENAS baseadas em PDFs indexados

**Storage (Git LFS)**
- `backend/data/pdfs/`: 7 PDFs (~20MB)
- `backend/data/index/index.faiss`: Índice FAISS com 11.799 vetores
- `backend/data/index/metadata.json`: Metadados dos chunks (22MB)

## 🎯 Regra de Ouro do RAG

✅ **Respostas DEVEM ser baseadas APENAS no acervo de PDFs**
- Gemini é "tradutor de contextos" → reformula linguisticamente contextos recuperados
- **PROIBIDO**: Adicionar informações, deduzir, supor, inventar
- **Quando não há info**: Retornar "Não encontrei essa informação no acervo"

Ver comentário de filosofia em `backend/rag.py` linhas 1-40.

## 📋 Stack & Modelos

| Componente | Versão |
|-----------|--------|
| **Embedding** | sentence-transformers/all-MiniLM-L6-v2 (384 dimensões) |
| **LLM** | Google Gemini 2.5 Flash (google-generativeai 0.8.3) |
| **Vector DB** | FAISS 1.13.0 (CPU) |
| **FastAPI** | 0.115.0 + Uvicorn 0.30.0 |
| **React** | 18.2.0 + React Router 7.9.6 |
| **Busca Híbrida** | FAISS (dense) + BM25 (sparse) |

## 🔑 Configurações Críticas

Arquivo: `backend/settings.py`

```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 8                    # Número de chunks recuperados
MIN_SIM = 0.30              # Filtro mínimo de similaridade
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
```

Carregam de `.env` na raiz do projeto (via python-dotenv).

## 🔄 Fluxos Críticos

### 1. Ingestão de PDFs
```bash
# Coloca PDFs em backend/data/pdfs/
python backend/ingest.py
```
- Extrai texto com PyMuPDF (fitz)
- Chunking semântico respeitando sentenças/parágrafos
- Gera embeddings + FAISS + metadata.json
- Salva em Git LFS

### 2. Query do Usuário (POST /ask)
```
Pergunta → Embedar → Busca Híbrida (FAISS + BM25) → Re-ranking → 
Gemini (reformulação) → Agregação de fontes → Resposta
```

Implementado em `backend/rag.py:search()` e `generate_answer()`.

### 3. Deploy em HF Spaces
```dockerfile
# Docker automático, executa:
python backend/init_index.py  # Valida índices
uvicorn backend.app:app --port 7860
```

## 📁 Estrutura de Arquivos Essenciais

| Arquivo | Propósito |
|---------|-----------|
| `backend/rag.py` | Pipeline RAG completo (564 linhas, comentado) |
| `backend/main.py` | Endpoints FastAPI + CORS |
| `backend/ingest.py` | Script CLI de ingestão |
| `backend/models.py` | Validação Pydantic (AskRequest, AskResponse) |
| `backend/settings.py` | Carregamento de configurações .env |
| `frontend/src/api.ts` | Cliente HTTP (interface AskResponse) |
| `frontend/src/App.tsx` | Componente raiz + gerenciamento de chat |
| `.env.example` | Template de variáveis (copiar para .env) |

## 🛠️ Workflows de Desenvolvimento

### Local Backend
```bash
# 1. Setup
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r backend/requirements.txt

# 2. Criar .env (copiar de .env.example)
# 3. Ingerir PDFs (se necessário)
python backend/ingest.py

# 4. Rodar servidor
uvicorn backend.main:app --reload --port 8000
# Acesse: http://localhost:8000/docs (Swagger)
```

### Local Frontend
```bash
cd frontend
npm install
npm run dev  # Acesse http://localhost:5173
# Configura VITE_API_BASE=http://localhost:8000
```

### Testar Integração
```bash
python test_api.py  # Testa endpoints básicos
python test_db_connection.py  # Valida índices
```

### Build & Deploy
- **Frontend**: Vercel automaticamente ao push em main
- **Backend**: GitHub Actions → HF Spaces (Dockerfile)

## 🔌 Integrações Externas

1. **Google Gemini 2.5 Flash**
   - Chave em `GOOGLE_API_KEY`
   - Importado em `backend/rag.py:generate_answer()`
   - **Prompt crítico**: "Reformule usando APENAS os contextos. Não invente informação."

2. **Git LFS** para PDFs e índices
   - Configurado em `.gitattributes`
   - Essencial para deploy em HF Spaces

3. **CORS**: Whitelist explícita em `backend/main.py`
   - Localhost (dev): `http://localhost:5173`, `http://localhost:3000`
   - Produção: `https://aiye-chat.vercel.app`

## 🎨 Padrões do Projeto

### Backend
- **Logging**: `print()` com prefixos (✓, ✗, ℹ, 🔍, 📄, etc.)
- **Validação**: Pydantic models, min_length/max_length explícitos
- **Async**: FastAPI async endpoints, espera de I/O
- **Estrutura**: Modular, separação clara (rag.py, models.py, settings.py)

### Frontend
- **State**: React hooks (`useState`, `useEffect`)
- **HTTP**: Async/await com try-catch em `api.ts`
- **CSS**: Tailwind com classes customizadas (`.umbanda-primary`, `.umbanda-secondary`)
- **UI/UX**: Loading states, error messages, health check visual

### Ambos
- **Environment**: `.env` para secrets e configuração
- **CI/CD**: Git LFS para assets, Dockerfile otimizado
- **Documentação**: Markdown em `DEVELOPMENT.md`, `PROJECT_SUMMARY.md`

## ⚡ Tarefas Comuns

### Adicionar novo endpoint
```python
# backend/main.py
@app.post("/novo")
async def novo(request: SomeRequest) -> SomeResponse:
    # Implementar e adicionar modelo em models.py
```

### Ajustar RAG parameters
```python
# .env
TOP_K=10              # Aumentar chunks
MIN_SIM=0.25          # Lowering threshold
EMBEDDING_MODEL=...   # Mudar modelo (cuidado: dimensionalidade!)
```

### Mudar tamanho de chunks
```python
# backend/rag.py chunk_text_semantic()
chunk_size=1500       # Aumentado de 1200
overlap=200           # Aumentado de 150
```

### Debug de respostas
- Checar `metadata.json` para coverage de documentos
- Usar `/docs` para testar manualmente POST /ask
- Verificar GOOGLE_API_KEY se Gemini falhar
- Logs em `backend/rag.py` indicam search score e re-ranking

## ❌ Evitar

- ❌ Hardcoding de URLs (usar `.env`)
- ❌ Responder sem fontes (sempre incluir Source objects)
- ❌ Modificar índices manualmente (sempre via `ingest.py`)
- ❌ CORS aberto (`*`) em produção
- ❌ Conhecimento prévio do Gemini (sempre usar contextos recuperados)

## 📚 Referências Rápidas

- **RAG Philosophy**: `backend/rag.py` linhas 1-40
- **API Contracts**: `backend/models.py` (Pydantic schemas)
- **Config Loading**: `backend/settings.py`
- **Frontend API Client**: `frontend/src/api.ts`
- **Full Architecture**: `PROJECT_SUMMARY.md`
- **Setup Local**: `QUICKSTART.md`
