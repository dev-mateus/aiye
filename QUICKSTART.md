"""
UMBANDA QA - GUIA DE INÍCIO RÁPIDO

✅ Todos os arquivos foram criados com sucesso!

Próximas etapas:
================

1. CONFIGURAR O AMBIENTE DO BACKEND

   a) Navegar para a pasta raiz do projeto:
      cd umbanda-qa

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

umbanda-qa/
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

✓ Backend FastAPI com endpoints /healthz e /ask
✓ RAG com FAISS (busca vetorial local)
✓ Embeddings HuggingFace (all-MiniLM-L6-v2)
✓ Parsing de PDFs com PyMuPDF
✓ Chunking com overlap
✓ Geração de respostas a partir dos contextos
✓ Frontend React + TypeScript + Tailwind
✓ Interface estilo Copilot/ChatGPT
✓ Visualização de fontes citadas
✓ Sistema de metadados em JSON
✓ Sem dependências externas (Docker, Postgres, LLM)
✓ Código tipado e comentado
✓ Tratamento de erros básico

NOTAS IMPORTANTES
=================

1. O arquivo .env não deve ser commitado (está no .gitignore)
2. Os índices FAISS também não são commitados (backend/data/index/)
3. PDFs de exemplo não precisam ser commitados
4. Para integrar com um LLM externo, edite a função generate_answer() em backend/rag.py
5. O sistema opera completamente local, sem serviços de terceiros
6. Consulte o README.md para mais informações e documentação

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

Boa sorte com o Umbanda QA! 🕯️✨
"""
