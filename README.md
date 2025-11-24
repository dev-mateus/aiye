---
title: Aiye
emoji: 🌿
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Plataforma RAG para perguntas sobre Umbanda
---

# Aiye – Plataforma de Perguntas sobre Umbanda

Uma plataforma **local-first** para responder perguntas sobre Umbanda utilizando **RAG (Retrieval-Augmented Generation)** com embeddings vetoriais e integração com Google Gemini.

## 🎯 Objetivo

Criar um espaço de conhecimento colaborativo onde perguntas sobre Umbanda são respondidas com base em um acervo de PDFs. As respostas são sempre citadas com as fontes, respeitando as variações entre diferentes terreiros e tradições.

## ⚙️ Requisitos

- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- ~2 GB de espaço em disco (para modelos de embedding e índices FAISS)

## 🚀 Como Rodar

### Backend

1. **Criar ambiente virtual:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

2. **Instalar dependências:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Criar arquivo `.env` (copiar de `.env.example`):**
   ```bash
   cp .env.example .env
   ```

4. **Ingerir PDFs:**
   - Coloque os PDFs em `backend/data/pdfs/`
   - Execute:
     ```bash
     python backend/ingest.py
     ```
   - Isso gerará `backend/data/index/index.faiss` e `metadata.json`

5. **Iniciar servidor:**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
   - Acesse: `http://localhost:8000`
   - Docs interativa: `http://localhost:8000/docs`

### Frontend

1. **Instalar dependências:**
   ```bash
   cd frontend
   npm install
   ```

2. **Criar `.env.local`:**
   ```
   VITE_API_BASE=http://localhost:8000
   ```

3. **Iniciar servidor de desenvolvimento:**
   ```bash
   npm run dev
   ```
   - Acesse: `http://localhost:5173`

## 📋 Estrutura de Pastas

```
aiye/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── ingest.py            # Script de ingestão de PDFs
│   ├── rag.py               # Lógica de RAG (embedding, search, answer generation)
│   ├── models.py            # Modelos Pydantic
│   ├── settings.py          # Configurações
│   ├── requirements.txt      # Dependências Python
│   └── data/
│       ├── pdfs/            # PDFs para ingestão
│       └── index/           # Índices FAISS e metadados
├── frontend/
│   ├── src/
│   │   ├── main.tsx         # Entrada React
│   │   ├── App.tsx          # Componente principal
│   │   ├── api.ts           # Cliente HTTP
│   │   ├── styles.css       # Estilos Tailwind
│   │   └── components/
│   │       ├── ChatBox.tsx      # Input e botão
│   │       ├── AnswerCard.tsx   # Resposta
│   │       └── SourceList.tsx   # Fontes
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── index.html
├── .env.example
├── .gitignore
└── README.md
```

## 📖 Fluxo de Uso

1. **Ingerir PDFs:** Execute `python backend/ingest.py` para processar PDFs em `backend/data/pdfs/`
2. **Fazer pergunta:** Digite no textarea do frontend
3. **Receber resposta:** O backend busca chunks relevantes no índice FAISS, gera uma resposta coerente e lista as fontes
4. **Consultar fontes:** Links para os PDFs originais

## 🧠 Como Funciona o RAG

- **Embeddings:** Utilizamos `sentence-transformers/all-MiniLM-L6-v2` para gerar embeddings vetoriais (384 dimensões)
- **Índice:** FAISS (CPU) armazena os embeddings localmente
- **Busca:** Busca coseno-similarity entre a pergunta e os chunks do acervo
- **Resposta:** Placeholder que gera uma resposta a partir dos contextos recuperados (sem LLM externo)
- **Metadados:** JSON com informações sobre documentos e chunks

## 🤖 Integração com Google Gemini

O projeto usa **Google Gemini 2.5 Flash** para gerar respostas inteligentes baseadas nos contextos recuperados:

- Configure `GOOGLE_API_KEY` no arquivo `.env` ou nas variáveis de ambiente do deploy
- O modelo sintetiza informações dos PDFs em respostas coerentes e bem estruturadas
- Respostas incluem citações das fontes e avisos sobre variações regionais da Umbanda

## ⚠️ Aviso Ético

- Este sistema é um **complemento informativo**, não substitui orientação de um dirigente espiritual
- As tradições da Umbanda **variam** entre terreiros e regiões
- Sempre cite as fontes e recomende consultar um dirigente para questões específicas
- O conteúdo ingerido deve ser confiável e autorizado

## 🚀 Deploy em Produção

### Backend (Hugging Face Spaces)
- **URL:** https://dev-mateus-backend-aiye.hf.space
- Deploy automático via Git push para branch `main`
- Usa **Docker SDK** com porta 7860
- PDFs e índices FAISS armazenados via **Git LFS**
- Configurar `GOOGLE_API_KEY` nas Repository secrets do Space

**Para fazer deploy:**
```bash
git push space main
```

Ver guia completo em [`DEPLOY_HUGGINGFACE.md`](./DEPLOY_HUGGINGFACE.md)

### Frontend (Vercel)
- **URL:** https://aiye.vercel.app
- Deploy automático via GitHub (branch `main`)
- Configurar `VITE_API_BASE=https://dev-mateus-backend-aiye.hf.space`
- Build automático com Vite a cada push

### Arquitetura de Deploy
```
┌─────────────┐      HTTPS/JSON      ┌──────────────────┐
│   Vercel    │ ───────────────────> │ Hugging Face     │
│  (Frontend) │                      │ Spaces (Backend) │
│  React+Vite │ <─────────────────── │  FastAPI+Docker  │
└─────────────┘                      └──────────────────┘
                                              │
                                              ├─ FAISS Index (LFS)
                                              ├─ PDFs (LFS)
                                              └─ Gemini API
```

## 📦 Dependências

### Backend
- FastAPI, Uvicorn
- FAISS (busca vetorial)
- Sentence Transformers (embeddings)
- PyMuPDF (parsing de PDFs)
- Pydantic (validação)

### Frontend
- React, React DOM
- Vite (bundler)
- TypeScript
- Tailwind CSS
- TanStack Query (gerenciamento de estado)

## 🤝 Contribuindo

1. Ingira novos PDFs em `backend/data/pdfs/`
2. Execute `python backend/ingest.py` para atualizar o índice
3. Envie feedback e melhore a plataforma

## 📄 Licença

MIT (ou conforme você preferir)

---

**Status:** MVP local-first, sem Docker, sem serviços pagos.
