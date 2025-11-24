# PROJETO AIYE - SUMÁRIO TÉCNICO

# PROJETO AIYE - SUMÁRIO TÉCNICO

## ✅ Status: EM PRODUÇÃO - v1.0.0

**Frontend (Vercel):** https://aiye-chat.vercel.app  
**Backend (Hugging Face Spaces):** https://dev-mateus-backend-aiye.hf.space  
**Repositório GitHub:** https://github.com/dev-mateus/aiye

### Arquitetura de Deploy
- **Frontend:** React 18.2 + Vite 5.0 + TypeScript 5.0 na Vercel (deploy automático via GitHub)
- **Backend:** FastAPI 0.115.0 + Docker (Python 3.11-slim) no Hugging Face Spaces (deploy via git push)
- **Storage:** PDFs (~20MB) e índice FAISS (133KB) + metadata.json (22MB) via Git LFS
- **LLM:** Google Gemini 2.5 Flash API
- **Vetores:** 11.799 chunks de 7 PDFs indexados
- **Branch:** `main` (standardized)

---

## 📁 Arquivos Criados (45+ arquivos)

### Raiz do Projeto
```
✓ README.md              - Documentação principal
✓ QUICKSTART.md          - Guia de início rápido (5 min)
✓ DEVELOPMENT.md         - Documentação técnica
✓ PROJECT_SUMMARY.md     - Este arquivo (sumário completo)
✓ TESTING.md             - Exemplos e testes
✓ DEPLOY_HUGGINGFACE.md  - Guia de deploy HF Spaces
✓ 00_LEIA_PRIMEIRO.txt   - Guia completo em português
✓ START.txt              - Sumário visual
✓ .env.example           - Variáveis de ambiente (exemplo)
✓ .gitignore             - Git ignore configurado
✓ .gitattributes         - Git LFS config (PDFs e índices)
✓ Dockerfile             - Container para HF Spaces
✓ test_api.py            - Script de teste da API
✓ run_backend.py         - Helper para rodar backend
✓ build.sh               - Script de build Unix
✓ deploy-hf.ps1          - Script de deploy PowerShell
```

### Backend (11 arquivos principais)
```
✓ backend/__init__.py              - Package init
✓ backend/app.py                   - Entry point HF Spaces (porta 7860)
✓ backend/main.py                  - Entry point local (porta 8000)
✓ backend/rag.py                   - Lógica RAG + Gemini
✓ backend/models.py                - Modelos Pydantic
✓ backend/settings.py              - Configurações + .env
✓ backend/ingest.py                - Script de ingestão PDFs
✓ backend/init_index.py            - Validação índices no deploy
✓ backend/warmup.py                - Pré-carregamento de modelos
✓ backend/requirements.txt         - Dependências Python
✓ backend/data/pdfs/               - 7 PDFs (~20MB via LFS)
✓ backend/data/index/index.faiss   - Índice FAISS (133KB via LFS)
✓ backend/data/index/metadata.json - 11.799 chunks (22MB via LFS)
```

### Frontend (15 arquivos)
```
✓ frontend/package.json             - Dependências npm
✓ frontend/vite.config.ts          - Config Vite
✓ frontend/tsconfig.json           - Config TypeScript
✓ frontend/tsconfig.node.json      - Config TypeScript Node
✓ frontend/tailwind.config.js      - Config Tailwind
✓ frontend/postcss.config.js       - Config PostCSS
✓ frontend/postcss.config.cjs      - Config PostCSS (CommonJS)
✓ frontend/index.html              - HTML entry
✓ frontend/src/main.tsx            - React entry
✓ frontend/src/App.tsx             - Componente raiz + footer
✓ frontend/src/api.ts              - Client HTTP
✓ frontend/src/styles.css          - Estilos Tailwind
✓ frontend/src/components/ChatBox.tsx       - Input de perguntas
✓ frontend/src/components/AnswerCard.tsx    - Display de resposta
✓ frontend/src/components/SourceList.tsx    - Lista de fontes (sem download)
```

---

## 🎯 Funcionalidades Implementadas

### Backend FastAPI (Hugging Face Spaces)
✅ Endpoint `GET /healthz` - Health check
✅ Endpoint `POST /ask` - Pergunta com RAG + Gemini
✅ CORS configurado para https://aiye-chat.vercel.app
✅ Tratamento de erros completo
✅ Documentação automática (Swagger UI em /docs)
✅ Validação com Pydantic 2.10.5
✅ Logging detalhado para debugging
✅ Warmup automático de modelos no boot
✅ Docker com Python 3.11-slim
✅ Git LFS para assets grandes

### RAG (Retrieval-Augmented Generation)
✅ Extração de PDFs com PyMuPDF 1.24.14
✅ Chunking com overlap (1500 chars, 200 overlap)
✅ Embeddings HuggingFace (sentence-transformers/all-MiniLM-L6-v2, 384 dims)
✅ Índice FAISS 1.13.0 (IndexFlatIP - cosine similarity)
✅ Busca top-8 com threshold 0.30
✅ Integração Google Gemini 2.5 Flash (google-generativeai 0.8.3)
✅ Persistência em JSON (11.799 chunks, 22MB)
✅ Sistema de fontes com páginas e scores
✅ 7 PDFs versionados (~20MB total via LFS)

### Frontend React + TypeScript (Vercel)
✅ Interface similar ChatGPT/Copilot
✅ Textarea para perguntas
✅ Validação (mínimo 3 caracteres)
✅ Loading state com spinner animado
✅ Exibição de respostas formatadas
✅ Lista de fontes SEM download (proteção copyright)
✅ Aviso ético automático
✅ Tailwind CSS 3.3 para styling responsivo
✅ Error handling com mensagens amigáveis
✅ Health check do backend
✅ Responsive design (mobile-first)
✅ Keyboard shortcuts (Enter para enviar)
✅ Footer com autor e GitHub link

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

## 📝 Roadmap

### ✅ Concluído (v1.0.0)
1. ✅ Deploy produção (Vercel + HF Spaces)
2. ✅ Integração Gemini 2.5 Flash
3. ✅ Git LFS para assets grandes
4. ✅ Interface responsiva completa
5. ✅ Documentação completa (8 arquivos)
6. ✅ 11.799 vetores indexados de 7 PDFs
7. ✅ Proteção copyright (sem download PDFs)

### 📋 Próximas Features (v1.1.0+)
1. □ Sistema de feedback de respostas
2. □ Filtros por documento/categoria
3. □ Histórico de conversas (localStorage)
4. □ Modo dark/light theme
5. □ API rate limiting (HF Spaces)
6. □ Cache de queries frequentes

### 🚀 Longo Prazo (v2.0.0+)
1. □ Dashboard de analytics/admin
2. □ Suporte a mais formatos (DOCX, TXT, EPUB)
3. □ Indexação incremental (add PDFs sem rebuild)
4. □ Sistema de permissões/roles
5. □ Testes automatizados (CI/CD)
6. □ Multilíngue (i18n)

---

## 📚 Documentação

- **README.md** - Visão geral, requisitos, como rodar
- **QUICKSTART.md** - Guia passo-a-passo
- **DEVELOPMENT.md** - Detalhes técnicos, arquitetura
- **Code Comments** - Docstrings em todas as funções

---

## ✨ Destaques

✓ **Em Produção** - v1.0.0 rodando em Vercel + HF Spaces
✓ **Type-Safe** - TypeScript no frontend, type hints em Python
✓ **Bem Documentado** - 8 guias + docstrings em todo código
✓ **Estruturado** - Separação clara de responsabilidades (MVC)
✓ **Escalável** - Fácil adicionar endpoints, componentes ou features
✓ **RAG Completo** - 11.799 vetores de 7 PDFs indexados
✓ **LLM Integrado** - Google Gemini 2.5 Flash API
✓ **Deploy Automático** - Git push → build → produção
✓ **Ético** - Avisos sobre variações entre terreiros
✓ **User-Friendly** - Interface intuitiva estilo ChatGPT
✓ **Git LFS** - Versionamento eficiente de assets grandes
✓ **Copyright Protection** - PDFs não downloadáveis

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
