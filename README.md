# Umbanda QA – Plataforma de Tira-Dúvidas Baseada em PDFs

Uma plataforma **local-first**, sem dependências externas de LLM ou banco de dados, para responder perguntas sobre Umbanda utilizando **RAG (Retrieval-Augmented Generation)** com embeddings vetoriais locais.

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
umbanda-qa/
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

## 🔧 Integração com LLM Futuro

O arquivo `backend/rag.py` contém a função `generate_answer()`, que atualmente é um placeholder. Para integrar com um LLM externo (Copilot, M365, OpenAI, etc.), basta substituir a implementação interna e adicionar a chamada à API:

```python
def generate_answer(question: str, contexts: list[dict]) -> str:
    # TODO: Integrar com Copilot/M365 ou outra API de LLM
    # prompt = f"Responda baseado nos contextos abaixo:\n\n{contextos}\n\nPergunta: {question}"
    # return call_to_llm_api(prompt)
    
    # Por enquanto: gera resposta a partir dos contextos
    ...
```

## ⚠️ Aviso Ético

- Este sistema é um **complemento informativo**, não substitui orientação de um dirigente espiritual
- As tradições da Umbanda **variam** entre terreiros e regiões
- Sempre cite as fontes e recomende consultar um dirigente para questões específicas
- O conteúdo ingerido deve ser confiável e autorizado

## 🔐 Dados Locais

- Nenhum dado é enviado para serviços externos
- Tudo roda localmente: embeddings, busca, índices
- Os PDFs e índices ficam em `backend/data/`

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
