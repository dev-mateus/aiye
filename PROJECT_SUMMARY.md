# 🕯️ PROJETO AIYE - SUMÁRIO TÉCNICO

> Plataforma RAG de Perguntas sobre Umbanda com IA

## ✅ Status: EM PRODUÇÃO - v1.0.0

| Componente | URL | Status |
|------------|-----|--------|
| 🌐 **Frontend** | https://aiye-chat.vercel.app | ✅ Online |
| 📡 **Backend API** | https://dev-mateus-backend-aiye.hf.space | ✅ Online |
| 📚 **Docs API** | https://dev-mateus-backend-aiye.hf.space/docs | ✅ Online |
| 💾 **Repositório** | https://github.com/dev-mateus/aiye | 🔓 Público |

### 🏗️ Arquitetura de Deploy

```mermaid
Frontend (Vercel)          Backend (HF Spaces)          Serviços Externos
┌─────────────────┐        ┌────────────────────┐       ┌──────────────┐
│  React 18.2     │───────▶│  FastAPI 0.115.0   │──────▶│   Gemini     │
│  TypeScript 5.0 │        │  Python 3.11       │       │  2.5 Flash   │
│  Vite 5.0       │◀───────│  Docker            │       └──────────────┘
│  Tailwind 3.3   │        │  Uvicorn 0.30.0    │
└─────────────────┘        └────────────────────┘
                                     │
                           ┌─────────┴─────────┐
                           │   Git LFS Storage │
                           ├───────────────────┤
                           │ • 7 PDFs (~20MB)  │
                           │ • FAISS (133KB)   │
                           │ • metadata (22MB) │
                           │ • 11.799 vetores  │
                           └───────────────────┘
```

**Stack Completo:**
- **Frontend:** React 18.2 + Vite 5.0 + TypeScript 5.0 + Tailwind CSS 3.3 → Vercel
- **Backend:** FastAPI 0.115.0 + Python 3.11-slim + Docker → Hugging Face Spaces
- **Storage:** Git LFS para PDFs (7 arquivos, ~20MB) + FAISS index (133KB) + metadata.json (22MB)
- **LLM:** Google Gemini 2.5 Flash API (google-generativeai 0.8.3)
- **RAG:** 11.799 vetores indexados com FAISS 1.13.0 + Sentence Transformers 3.3.1
- **Branch:** `main` (padronizada, `master` removida)

---

## 📁 Estrutura do Projeto (45+ arquivos)

### 📄 Raiz do Projeto

| Arquivo | Descrição | Tipo |
|---------|-----------|------|
| `README.md` | Documentação principal com metadados HF | 📘 Docs |
| `QUICKSTART.md` | Guia de início rápido (5 minutos) | 🚀 Guia |
| `DEVELOPMENT.md` | Documentação técnica detalhada | 🔧 Técnico |
| `PROJECT_SUMMARY.md` | Este arquivo (sumário completo) | 📊 Sumário |
| `TESTING.md` | Exemplos e casos de teste | 🧪 Testes |
| `DEPLOY_HUGGINGFACE.md` | Guia de deploy HF Spaces | 🚢 Deploy |
| `00_LEIA_PRIMEIRO.txt` | Guia completo em português | 📖 Guia PT-BR |
| `START.txt` | Sumário visual ASCII art | 🎨 Visual |
| `.env.example` | Template de variáveis de ambiente | ⚙️ Config |
| `.gitignore` | Arquivos ignorados pelo Git | 🚫 Git |
| `.gitattributes` | Configuração Git LFS | 📦 Git LFS |
| `Dockerfile` | Container para HF Spaces (Python 3.11) | 🐳 Docker |
| `test_api.py` | Script de teste da API | 🧪 Script |
| `run_backend.py` | Helper para iniciar backend | 🔧 Helper |
| `build.sh` | Script de build Unix/Linux | 🛠️ Build |
| `deploy-hf.ps1` | Script de deploy PowerShell | 🚀 Deploy |

### 🐍 Backend (11 arquivos principais)

| Arquivo | Descrição | Linhas | Status |
|---------|-----------|--------|--------|
| `__init__.py` | Package initialization | ~5 | ✅ |
| `app.py` | Entry point HF Spaces (porta 7860) | ~100 | ✅ |
| `main.py` | Entry point local (porta 8000) | ~80 | ✅ |
| `rag.py` | Lógica RAG + Gemini (core) | ~600 | ✅ |
| `models.py` | Modelos Pydantic (validação) | ~50 | ✅ |
| `settings.py` | Configurações + carregamento .env | ~40 | ✅ |
| `ingest.py` | Script de ingestão de PDFs | ~300 | ✅ |
| `init_index.py` | Validação de índices no deploy | ~50 | ✅ |
| `warmup.py` | Pré-carregamento de modelos | ~30 | ✅ |
| `requirements.txt` | 15 dependências Python | ~15 | ✅ |

**Dados Armazenados (Git LFS):**

| Diretório/Arquivo | Conteúdo | Tamanho | Tipo |
|-------------------|----------|---------|------|
| `data/pdfs/` | 7 PDFs sobre Umbanda | ~20 MB | LFS |
| `data/index/index.faiss` | Índice FAISS (11.799 vetores) | 133 KB | LFS |
| `data/index/metadata.json` | Metadados dos 11.799 chunks | 22 MB | LFS |

### ⚛️ Frontend (15 arquivos)

**Configuração:**

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `package.json` | Dependências npm (15 pacotes) | ✅ |
| `vite.config.ts` | Configuração Vite 5.0 | ✅ |
| `tsconfig.json` | TypeScript config (strict mode) | ✅ |
| `tsconfig.node.json` | TypeScript config para Node | ✅ |
| `tailwind.config.js` | Tailwind CSS 3.3 (tema Aiye) | ✅ |
| `postcss.config.js` | PostCSS para Tailwind | ✅ |
| `postcss.config.cjs` | PostCSS CommonJS fallback | ✅ |
| `index.html` | HTML entry point | ✅ |

**Código Fonte:**

| Arquivo | Descrição | Linhas | Status |
|---------|-----------|--------|--------|
| `src/main.tsx` | React entry + setup | ~15 | ✅ |
| `src/App.tsx` | Componente raiz + footer | ~150 | ✅ |
| `src/api.ts` | Cliente HTTP (Axios) | ~50 | ✅ |
| `src/styles.css` | Estilos Tailwind + custom | ~30 | ✅ |

**Componentes:**

| Componente | Descrição | Linhas | Features |
|------------|-----------|--------|----------|
| `ChatBox.tsx` | Input de perguntas | ~80 | Validação, Enter to submit |
| `AnswerCard.tsx` | Display de resposta Gemini | ~60 | Markdown, loading states |
| `SourceList.tsx` | Lista de fontes (sem download) | ~70 | Scores, páginas, copyright |

---

## 🎯 Funcionalidades Implementadas

### 🔌 Backend FastAPI (Hugging Face Spaces)

| Endpoint | Método | Descrição | Status |
|----------|--------|-----------|--------|
| `/healthz` | GET | Health check da API | ✅ |
| `/warmup` | GET | Pré-carregamento de modelos | ✅ |
| `/ask` | POST | Pergunta com RAG + Gemini | ✅ |
| `/docs` | GET | Documentação Swagger UI | ✅ |

**Features Backend:**
- ✅ CORS configurado para `https://aiye-chat.vercel.app`
- ✅ Validação de dados com Pydantic 2.10.5
- ✅ Logging detalhado (debug, info, error)
- ✅ Tratamento de erros com mensagens amigáveis
- ✅ Warmup automático de modelos no boot
- ✅ Docker otimizado (Python 3.11-slim, multi-stage)
- ✅ Git LFS para assets grandes (>100KB)

### 🧠 RAG (Retrieval-Augmented Generation)

**Pipeline Completo:**

```
PDFs → Extração → Chunking → Embeddings → FAISS Index → Busca → Gemini → Resposta
```

| Etapa | Tecnologia | Configuração | Status |
|-------|------------|--------------|--------|
| **Extração** | PyMuPDF 1.24.14 | 7 PDFs (~20MB) | ✅ |
| **Chunking** | Custom | 1500 chars, overlap 200 | ✅ |
| **Embeddings** | sentence-transformers | all-MiniLM-L6-v2 (384 dim) | ✅ |
| **Índice** | FAISS 1.13.0 | IndexFlatIP (11.799 vetores) | ✅ |
| **Busca** | Cosine similarity | Top-8, threshold 0.30 | ✅ |
| **LLM** | Gemini 2.5 Flash | google-generativeai 0.8.3 | ✅ |
| **Persistência** | JSON | metadata.json (22MB, LFS) | ✅ |

**Metadados:**
- 📄 7 documentos PDF indexados
- 🔢 11.799 chunks de texto
- 📊 Cada chunk: conteúdo, documento_id, páginas, score
- 💾 Armazenamento: Git LFS (versionamento eficiente)

### 🎨 Frontend React + TypeScript (Vercel)

**Interface:**
- ✅ Design moderno estilo ChatGPT/Copilot
- ✅ Tema personalizado "Aiye" (verde/azul)
- ✅ Responsive design mobile-first
- ✅ Tailwind CSS 3.3 utility-first

**Funcionalidades:**
- ✅ Textarea com validação (mín. 3 caracteres)
- ✅ Loading state com spinner animado
- ✅ Exibição de respostas formatadas (Markdown)
- ✅ Lista de fontes **sem download** (proteção copyright)
- ✅ Aviso ético sobre variações regionais
- ✅ Error handling com mensagens user-friendly
- ✅ Health check automático do backend
- ✅ Keyboard shortcuts (Enter para enviar)
- ✅ Footer com autor e link GitHub

**UX:**
- ⌨️ **Enter** envia pergunta
- 🔄 Loading states em todas as ações
- ❌ Mensagens de erro claras
- 📱 Otimizado para mobile e desktop

---

## 🚀 Como Começar

### Acesso Produção (Recomendado)
```
🌐 Frontend: https://aiye-chat.vercel.app
📡 API: https://dev-mateus-backend-aiye.hf.space
📚 Docs: https://dev-mateus-backend-aiye.hf.space/docs
```

### Desenvolvimento Local

#### 1. Clonar Repositório
```bash
git clone https://github.com/dev-mateus/aiye.git
cd aiye
```

#### 2. Configurar Backend
```bash
cp .env.example .env
# Editar .env e adicionar: GOOGLE_API_KEY=sua_chave_aqui
# Obter chave em: https://aistudio.google.com/app/apikey

python -m venv .venv
.venv\Scripts\activate  # Windows
# ou: source .venv/bin/activate  # Linux/Mac

pip install -r backend/requirements.txt
```

#### 3. Primeira Vez - Ingerir PDFs (Opcional)
```bash
# PDFs já estão incluídos via Git LFS
# Para adicionar novos PDFs:
# 1. Coloque em backend/data/pdfs/
# 2. Execute:
python backend/ingest.py
```

#### 4. Iniciar Backend
```bash
uvicorn backend.main:app --reload --port 8000
# Acesso: http://localhost:8000
# Docs: http://localhost:8000/docs
```

#### 5. Configurar Frontend
```bash
cd frontend
npm install
# Criar .env.local:
echo "VITE_API_BASE=http://localhost:8000" > .env.local
npm run dev
# Acesso: http://localhost:5173
```

---

## 📊 Estrutura de Dados

### Metadata JSON
```json
{
  "documents": [
    {
      "document_id": "uuid",
      "title": "Título do PDF",
      "source_uri": "backend/data/pdfs/arquivo.pdf",
      "pages": 10
    }
  ],
  "chunks": [
    {
      "document_id": "uuid",
      "chunk_id": "uuid",
      "page_start": 1,
      "page_end": 2,
      "content": "texto do chunk..."
    }
  ]
}
```

### API Request/Response

**POST /ask**
```json
Request:
{
  "question": "O que é Umbanda?"
}

Response:
{
  "answer": "Resposta coerente...",
  "sources": [
    {
      "title": "Título do Doc",
      "page_start": 1,
      "page_end": 2,
      "uri": "backend/data/pdfs/arquivo.pdf",
      "score": 0.85
    }
  ],
  "meta": {
    "latency_ms": 234,
    "top_k": 5,
    "min_sim": 0.25,
    "num_contexts": 3
  }
}
```

---

## 🔧 Tecnologias Utilizadas

### Backend
- **FastAPI 0.115.0** - Web framework moderno
- **Uvicorn 0.30.0** - ASGI server performático
- **FAISS 1.13.0** - Vector search (IndexFlatIP)
- **SentenceTransformers 3.3.1** - Embeddings (all-MiniLM-L6-v2)
- **Google-generativeai 0.8.3** - Gemini 2.5 Flash API
- **PyMuPDF 1.24.14** - PDF parsing otimizado
- **Pydantic 2.10.5** - Data validation
- **Python-dotenv 1.0.1** - Gerenciamento de .env
- **Python 3.11** - Linguagem base

### Frontend
- **React 18.2.0** - UI library declarativa
- **TypeScript 5.0.0** - Type safety
- **Vite 5.0.0** - Build tool ultrarrápido (HMR)
- **Tailwind CSS 3.3.0** - Utility-first CSS
- **TanStack Query 5.0.0** - State management async
- **Node.js 18+** - Runtime JavaScript

### Infraestrutura
- **Vercel** - Frontend hosting (deploy automático)
- **Hugging Face Spaces** - Backend hosting (Docker)
- **Git LFS** - Versionamento de PDFs e índices (>100KB)
- **Docker** - Containerização (Python 3.11-slim)
- **GitHub Actions** - CI/CD (implícito via Vercel)

---

## 📝 Roadmap & Versões

### ✅ v1.0.0 - Concluído (Novembro 2025)

| Feature | Status | Descrição |
|---------|--------|-----------|
| Deploy Produção | ✅ | Vercel (frontend) + HF Spaces (backend) |
| Integração Gemini | ✅ | Google Gemini 2.5 Flash API |
| Git LFS | ✅ | Versionamento de assets grandes (PDFs, índices) |
| Interface Responsiva | ✅ | Mobile-first, Tailwind CSS 3.3 |
| Documentação | ✅ | 8 arquivos completos (PT-BR + EN) |
| Vetores Indexados | ✅ | 11.799 chunks de 7 PDFs |
| Copyright Protection | ✅ | PDFs não downloadáveis (apenas consulta) |
| TypeScript | ✅ | 100% tipado (frontend + backend hints) |

### 📋 v1.1.0 - Próximas Features (Planejado)

| Feature | Prioridade | Complexidade | Estimativa |
|---------|------------|--------------|------------|
| Sistema de feedback | 🔴 Alta | Média | 2-3 dias |
| Filtros por documento | 🟡 Média | Baixa | 1-2 dias |
| Histórico conversas | 🟡 Média | Média | 2-3 dias |
| Modo dark/light | 🟢 Baixa | Baixa | 1 dia |
| API rate limiting | 🔴 Alta | Média | 2 dias |
| Cache de queries | 🟡 Média | Alta | 3-4 dias |

**Total estimado:** ~2 semanas

### 🚀 v2.0.0 - Longo Prazo (2026)

| Feature | Impacto | Esforço | Descrição |
|---------|---------|---------|-----------|
| Dashboard Analytics | 🔴 Alto | Alto | Painel admin com métricas de uso |
| Mais Formatos | 🟡 Médio | Médio | DOCX, TXT, EPUB, Markdown |
| Indexação Incremental | 🔴 Alto | Alto | Add PDFs sem rebuild completo |
| Permissões/Roles | 🟢 Baixo | Alto | Sistema de autenticação |
| Testes Automatizados | 🔴 Alto | Médio | CI/CD com GitHub Actions |
| Multilíngue (i18n) | 🟡 Médio | Médio | EN, ES além de PT-BR |
| Vector DB Cloud | 🟡 Médio | Alto | Pinecone/Weaviate para escalabilidade |

**Total estimado:** ~3-4 meses

---

## 📚 Documentação

- **README.md** - Visão geral, requisitos, como rodar
- **QUICKSTART.md** - Guia passo-a-passo
- **DEVELOPMENT.md** - Detalhes técnicos, arquitetura
- **Code Comments** - Docstrings em todas as funções

---

## ✨ Destaques do Projeto

### 🏆 Principais Diferenciais

| Categoria | Destaque | Detalhes |
|-----------|----------|----------|
| 🚀 **Produção** | Em produção v1.0.0 | Vercel (frontend) + HF Spaces (backend) |
| 🔒 **Type-Safe** | 100% tipado | TypeScript 5.0 + Python type hints |
| 📚 **Documentação** | Completa | 8 arquivos (3000+ linhas) |
| 🏗️ **Arquitetura** | MVC limpo | Separação clara de responsabilidades |
| 📈 **Escalável** | Modular | Fácil adicionar endpoints/componentes |
| 🧠 **RAG Completo** | 11.799 vetores | 7 PDFs indexados com FAISS |
| 🤖 **LLM** | Gemini 2.5 Flash | Respostas inteligentes em PT-BR |
| ⚡ **Deploy** | Automático | Git push → build → produção (1-2 min) |
| ⚖️ **Ético** | Avisos | Respeito a variações regionais |
| 🎨 **UX** | Intuitivo | Interface estilo ChatGPT |
| 💾 **Git LFS** | Otimizado | Versionamento eficiente (22MB) |
| 🔐 **Copyright** | Protegido | PDFs não downloadáveis |

### 🎯 Stack Tecnológico Moderno

**Frontend:**
- ⚛️ React 18.2 (Hooks, Context API)
- 📘 TypeScript 5.0 (Strict mode)
- ⚡ Vite 5.0 (HMR ultrarrápido)
- 🎨 Tailwind CSS 3.3 (Utility-first)

**Backend:**
- 🚀 FastAPI 0.115.0 (Async/await)
- 🐍 Python 3.11 (Type hints)
- 🔍 FAISS 1.13.0 (Vector search)
- 🤖 Gemini 2.5 Flash (LLM)

**Infraestrutura:**
- 🌐 Vercel (Edge network)
- 🤗 Hugging Face Spaces (Docker)
- 📦 Git LFS (Large files)
- 🔄 GitHub (CI/CD)

---

## 🛠️ Troubleshooting

### Backend não inicia
- Verifique se porta 8000 está livre: `netstat -ano | findstr :8000`
- Confirme Python 3.11+: `python --version`
- Atualize pip: `python -m pip install --upgrade pip`
- Reinstale deps: `pip install -r backend/requirements.txt`

### GOOGLE_API_KEY não configurada
- Crie arquivo `.env` na raiz: `copy .env.example .env`
- Obtenha chave em: https://aistudio.google.com/app/apikey
- Adicione no `.env`: `GOOGLE_API_KEY=sua_chave_aqui`

### PDFs não encontrados (dev local)
- Confirme que PDFs estão em `backend/data/pdfs/`
- Extensão `.pdf` (case-insensitive)
- Execute `python backend/ingest.py` novamente
- Verifique Git LFS instalado: `git lfs install`

### Frontend erro "Backend Offline"
- Verifique se uvicorn está rodando: `http://localhost:8000/healthz`
- Confirme VITE_API_BASE em `frontend/.env.local`
- Verifique CORS em `backend/settings.py`

### Lentidão na busca
- FAISS IndexFlatIP é exaustivo (busca em todos os 11.799 vetores)
- Para 100k+ chunks, considere IndexIVF ou HNSW
- Ajuste TOP_K (padrão: 8) ou MIN_SIM (padrão: 0.30)

### Deploy HF Spaces falha
- Verifique logs: https://huggingface.co/spaces/dev-mateus/backend-aiye/logs
- Confirme Git LFS files foram enviados: `git lfs ls-files`
- Verifique GOOGLE_API_KEY nos HF Secrets
- Rebuild manual: Settings → Factory reboot

### Vercel build error
- Verifique variável VITE_API_BASE nas env vars do Vercel
- Confirme TypeScript sem erros: `cd frontend && npm run build`
- Check logs no Vercel dashboard

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte README.md
2. Verifique DEVELOPMENT.md
3. Veja comentários no código
4. Teste com `curl` antes de testar no frontend

---

## 🎓 Estrutura de Aprendizado

Recomendado estudar na ordem:
1. `README.md` - Visão geral
2. `backend/models.py` - Modelos de dados
3. `backend/rag.py` - Lógica central
4. `backend/main.py` - Endpoints
5. `frontend/src/App.tsx` - Interface
6. `DEVELOPMENT.md` - Detalhes avançados

---

**Projeto em produção! 🎉**

Versão: 1.0.0 (Produção)
Status: ✅ Online  
Frontend: https://aiye-chat.vercel.app  
Backend: https://dev-mateus-backend-aiye.hf.space  
Repositório: https://github.com/dev-mateus/aiye

Desenvolvido com ❤️ por [Mateus](https://github.com/dev-mateus)  
Licença: MIT
