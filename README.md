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

Plataforma **RAG (Retrieval-Augmented Generation)** para responder perguntas sobre Umbanda, Espiritismo e temas afins utilizando inteligência artificial, embeddings vetoriais e LLM via Groq (endpoint OpenAI-compatible).

> Atualização (jan/2026): A expansão de consultas via LLM foi desativada por padrão para reforçar o grounding no acervo e evitar dependências quebradas. A busca continua usando sinônimos controlados do domínio de Umbanda. É possível reativar com a flag `ENABLE_LLM_EXPANSION=true` no `.env`.

## 🎯 Objetivo

Criar um espaço de conhecimento onde perguntas sobre Umbanda são respondidas com base em um acervo curado de PDFs. As respostas são geradas por IA e sempre citam as fontes consultadas, respeitando as variações entre diferentes terreiros e tradições.

## ⚙️ Requisitos

**Desenvolvimento Local:**
- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **Groq API Key** (obrigatório)
- **Google API Key** (opcional, para fallback futuro)
- ~2 GB de espaço em disco (para modelos de embedding e índices FAISS)

**Produção:**
- Conta Hugging Face (backend)
- Conta Vercel (frontend)
- Git LFS configurado (para PDFs e índices)

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

4. **Definir `GROQ_API_KEY` no `.env`**

5. **Ingerir PDFs:**
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

1. **Ingestão de PDFs:** Execute `python backend/ingest.py` para processar PDFs em `backend/data/pdfs/` e gerar o índice FAISS
2. **Fazer pergunta:** Digite sua pergunta no frontend (https://aiye-chat.vercel.app)
3. **Receber resposta:** O backend busca chunks relevantes no índice FAISS, envia para o Gemini sintetizar uma resposta coerente e retorna com as fontes consultadas
4. **Consultar fontes:** Visualize os documentos consultados (sem download de PDFs por questões de direitos autorais)

## 🧠 Como Funciona o RAG

- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` gera vetores de 384 dimensões para cada chunk de texto
- **Índice:** FAISS (IndexFlatIP) armazena os embeddings para busca eficiente por similaridade
- **Chunking:** PDFs divididos em chunks de 1500 caracteres com overlap de 200 para manter contexto
- **Busca:** Similaridade de cosseno entre a pergunta embedada e os chunks do acervo (top-8, threshold 0.30)
- **Geração:** LLM via Groq (cliente OpenAI) sintetiza a resposta final baseada nos contextos recuperados
- **Metadados:** JSON com informações sobre documentos, chunks, páginas e scores de relevância

## 🤖 Integração com Google Gemini
## 🤖 Integração com Groq (OpenAI-compatible)

O backend usa o cliente OpenAI apontando para o endpoint Groq:

- Configure `GROQ_API_KEY` no `.env` (dev) ou em Repository Secrets (HF Spaces)
- Variáveis suportadas: `GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_BASE_URL`
- Prompt reforça: “Reformule usando APENAS os contextos. Não invente informação.”

Gemini permanece opcional para futuro fallback (via `GOOGLE_API_KEY`).

### Expansão de Query (LLM) – Estado Atual
- Por padrão está DESATIVADA para garantir respostas estritamente baseadas no acervo.
- Somente sinônimos do domínio são usados para expandir queries (ex.: `orixá` → `orishas`, `divindades`).
- Para reativar: defina `ENABLE_LLM_EXPANSION=true` no `.env`. A lógica usa um prompt restritivo e aplica filtros locais para evitar drift.

## ⚠️ Aviso Ético

- Este sistema é um **complemento informativo**, não substitui orientação de um dirigente espiritual
- As tradições da Umbanda **variam** entre terreiros e regiões
- Sempre cite as fontes e recomende consultar um dirigente para questões específicas
- O conteúdo ingerido deve ser confiável e autorizado

## 🚀 Deploy em Produção

### Backend (Hugging Face Spaces)
- **URL Produção:** https://dev-mateus-backend-aiye.hf.space
- **Tecnologia:** Docker (Python 3.11-slim) com FastAPI + Uvicorn
- **Deploy:** Automático via `git push space main`
- **Armazenamento:** PDFs e índice FAISS via **Git LFS** (metadata.json ~22MB, index.faiss ~133KB)
- **Build:** Dockerfile executa `backend/init_index.py` para gerar índice se não existir
- **Secrets:** `GOOGLE_API_KEY` configurada em Repository secrets

**Comandos de deploy:**
```bash
git add .
git commit -m "mensagem"
git push origin main   # GitHub
git push space main    # Hugging Face Spaces (trigger rebuild)
```

Ver guia completo em [`DEPLOY_HUGGINGFACE.md`](./DEPLOY_HUGGINGFACE.md)

### Frontend (Vercel)
- **URL Produção:** https://aiye-chat.vercel.app
- **Tecnologia:** React 18 + TypeScript + Vite 5 + Tailwind CSS 3
- **Deploy:** Automático via GitHub (branch `main`)
- **Variável de Ambiente:** `VITE_API_BASE=https://dev-mateus-backend-aiye.hf.space`
- **Build:** Vite build com TypeScript check a cada push

### Arquitetura de Deploy
```
┌─────────────────┐      HTTPS/JSON      ┌────────────────────┐
│     Vercel      │ ──────────────────> │  Hugging Face      │
│   (Frontend)    │                      │  Spaces (Backend)  │
│ React+Vite+TS   │ <──────────────────  │  FastAPI+Docker    │
└─────────────────┘                      └────────────────────┘
                                                   │
                                                   ├─ FAISS Index (LFS)
                                                   ├─ PDFs (LFS)  
                                                   ├─ Sentence Transformers
                                                   └─ Groq API (OpenAI-compatible)
```

## 📦 Dependências

### Backend
- **FastAPI 0.115.0** - Framework web moderno e rápido
- **Uvicorn 0.30.0** - Servidor ASGI de alta performance
- **FAISS 1.13.0** - Busca vetorial eficiente (CPU)
- **Sentence Transformers 3.0.1** - Geração de embeddings
- **PyMuPDF 1.24.9** - Parsing e extração de texto de PDFs
- **OpenAI 1.55.3** - Cliente OpenAI (endpoint Groq)
- **Pydantic 2.x** - Validação de dados

### Frontend
- **React 18.2** - Biblioteca UI declarativa
- **TypeScript 5.0** - Type safety
- **Vite 5.0** - Build tool ultrarrápido
- **Tailwind CSS 3.3** - Framework CSS utility-first
- **Axios** - Cliente HTTP

## 🤝 Contribuindo

Este é um projeto educacional e informativo. Para contribuir:

1. Faça fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add: nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

**Sugestões de contribuição:**
- Adicionar novos PDFs ao acervo (com direitos autorais respeitados)
- Melhorar o prompt do Gemini para respostas mais precisas
- Implementar feature de visualização de trechos dos PDFs (similar ao Google Books)
- Adicionar suporte a outros idiomas
- Melhorar o design do frontend

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

## 👨‍💻 Autor

Desenvolvido com ❤️ por [Mateus](https://github.com/dev-mateus)

---

**Status:** ✅ Em produção  
**Versão:** 1.0.0  
**Última atualização:** Novembro 2025
