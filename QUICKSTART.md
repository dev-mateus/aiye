"""
AIYE - GUIA DE INÍCIO RÁPIDO

✅ Plataforma de perguntas sobre Umbanda

Próximas etapas:
================

1. CONFIGURAR O AMBIENTE DO BACKEND

   a) Navegar para a pasta raiz do projeto:
      cd aiye

   b) Criar arquivo .env (copiar de .env.example):
      cp .env.example .env
      # ou no Windows:
      copy .env.example .env

   c) Criar ambiente virtual Python:
      python -m venv .venv
      # Ativar:
      # Windows:
      .venv\Scripts\activate
      # macOS/Linux:
      source .venv/bin/activate

   d) Instalar dependências do backend:
      pip install -r backend/requirements.txt

2. INGERIR PDFS (OPCIONAL - Para Testar)

   a) Colocar alguns arquivos PDF em:
      backend/data/pdfs/

   b) Executar script de ingestão (recomendado usar como módulo):
      # recomendado (preserva imports de pacote)
      python -m backend.ingest

      # alternativa (há fallback no script que adiciona a raiz ao PYTHONPATH):
      python backend/ingest.py

   Isto criará:
   - backend/data/index/index.faiss
   - backend/data/index/metadata.json

3. INICIAR O BACKEND

   Na pasta raiz com .venv ativado:
   uvicorn backend.main:app --reload --port 8000

   O servidor estará em: http://localhost:8000
   Documentação interativa: http://localhost:8000/docs

4. CONFIGURAR E INICIAR O FRONTEND

   a) Abrir outro terminal na pasta raiz

   b) Navegar para pasta frontend:
      cd frontend

   c) Criar arquivo .env.local:
      # Windows (PowerShell):
      echo "VITE_API_BASE=http://localhost:8000" > .env.local
      # ou macOS/Linux:
      echo "VITE_API_BASE=http://localhost:8000" > .env.local

   d) Instalar dependências:
      npm install

   e) Iniciar servidor de desenvolvimento:
      npm run dev

   O frontend estará em: http://localhost:5173

5. TESTAR O SISTEMA

   - Abra http://localhost:5173 no navegador
   - Digite uma pergunta (mínimo 3 caracteres)
   - Pressione "Perguntar" ou Ctrl+Enter
   - A resposta será exibida com as fontes

ESTRUTURA DO PROJETO
====================

aiye/
├── backend/                     # API FastAPI
│   ├── main.py                 # Servidor FastAPI
│   ├── rag.py                  # Lógica de RAG
│   ├── models.py               # Modelos Pydantic
│   ├── settings.py             # Configurações
│   ├── ingest.py               # Script de ingestão
│   ├── requirements.txt         # Dependências Python
│   └── data/
│       ├── pdfs/               # PDFs para processar
│       └── index/              # Índice FAISS + metadados
├── frontend/                    # App React + Vite
│   ├── src/
│   │   ├── main.tsx            # Entrada React
│   │   ├── App.tsx             # Componente principal
│   │   ├── api.ts              # Cliente HTTP
│   │   ├── styles.css          # Estilos Tailwind
│   │   └── components/         # Componentes React
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── index.html
├── .env.example                 # Variáveis de exemplo
├── .gitignore
└── README.md

FEATURES IMPLEMENTADAS
======================

✓ Backend FastAPI com endpoints /healthz, /warmup e /ask
✓ RAG com FAISS (busca vetorial local)
✓ Embeddings HuggingFace (all-MiniLM-L6-v2)
✓ Integração com Google Gemini 2.5 Flash para respostas
✓ Parsing de PDFs com PyMuPDF
✓ Chunking com overlap (1500 chars)
✓ Frontend React + TypeScript + Tailwind
✓ Interface personalizada "Aiye" com tema verde
✓ Visualização de fontes citadas
✓ Sistema de metadados em JSON
✓ Deploy em Render (backend) + Vercel (frontend)
✓ Código tipado e comentado
✓ Tratamento de erros robusto

DEPLOY EM PRODUÇÃO
==================

1. Backend (Render.com):
   - Criar Web Service conectado ao GitHub (dev-mateus/aiye)
   - Configurar variável: GOOGLE_API_KEY=<sua-chave>
   - Deploy automático a cada push no master
   - URL: https://aiye.onrender.com

2. Frontend (Vercel):
   - Importar projeto do GitHub
   - Configurar variável: VITE_API_BASE=https://aiye.onrender.com
   - Deploy automático a cada push

3. Embeddings Remotos (Opcional - economiza RAM):
   - Adicionar no Render: EMBEDDING_PROVIDER=remote
   - Usa API Google para embeddings ao invés de modelo local

NOTAS IMPORTANTES
=================

1. O arquivo .env não deve ser commitado (está no .gitignore)
2. Os índices FAISS são gerados automaticamente no deploy
3. Configure GOOGLE_API_KEY para usar o Gemini
4. PDFs devem estar em backend/data/pdfs/ e commitados no repo
5. Consulte o README.md para mais informações

ERROS COMUNS
============

❌ "Backend não está disponível"
   → Certifique-se que uvicorn está rodando em http://localhost:8000

❌ "ModuleNotFoundError: No module named 'fastapi'"
   → Verifique se .venv está ativado e pip install -r backend/requirements.txt foi executado

❌ "npm: command not found"
   → Instale Node.js em https://nodejs.org/

❌ "Nenhum arquivo PDF encontrado"
   → Coloque PDFs em backend/data/pdfs/ e execute python backend/ingest.py

SUPORTE
=======

Consulte o README.md para documentação completa:
cat README.md

Boa sorte com o Aiye! 🕯️✨
"""
