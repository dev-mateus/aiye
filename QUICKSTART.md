# AIYE - GUIA DE INÍCIO RÁPIDO

✅ Plataforma RAG de perguntas sobre Umbanda usando IA

## Acesso Rápido à Aplicação em Produção

🌐 **Frontend:** https://aiye-chat.vercel.app  
🔧 **Backend API:** https://dev-mateus-backend-aiye.hf.space  
📚 **Docs da API:** https://dev-mateus-backend-aiye.hf.space/docs

---

## Desenvolvimento Local

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- Google API Key (Gemini)

### 1. CONFIGURAR O AMBIENTE DO BACKEND

**a) Navegar para a pasta raiz do projeto:**
```bash
cd aiye
```

**b) Criar arquivo `.env` com sua API key:**
```bash
# Windows:
copy .env.example .env

# macOS/Linux:
cp .env.example .env
```

Edite o `.env` e adicione sua chave:
```
GOOGLE_API_KEY=sua_chave_aqui
```

**c) Criar ambiente virtual Python:**
```bash
python -m venv .venv

# Ativar:
# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate
```

**d) Instalar dependências do backend:**
```bash
pip install -r backend/requirements.txt
```

### 2. INGERIR PDFS (Primeira vez ou ao adicionar novos PDFs)

**a) PDFs já incluídos:**
O projeto já contém 7 PDFs sobre Umbanda e Espiritismo em `backend/data/pdfs/`

**b) Gerar índice FAISS:**
```bash
python backend/ingest.py
```

Isto criará:
- `backend/data/index/index.faiss` (~133 KB)
- `backend/data/index/metadata.json` (~22 MB)

### 3. INICIAR O BACKEND

Na pasta raiz com `.venv` ativado:
```bash
uvicorn backend.main:app --reload --port 8000
```

✅ Servidor rodando em: http://localhost:8000  
📖 Documentação interativa: http://localhost:8000/docs

### 4. CONFIGURAR E INICIAR O FRONTEND

**a) Abrir outro terminal na pasta raiz**

**b) Navegar para pasta frontend:**
```bash
cd frontend
```

**c) Criar arquivo `.env.local`:**
```bash
# Windows (PowerShell):
echo "VITE_API_BASE=http://localhost:8000" > .env.local

# macOS/Linux:
echo "VITE_API_BASE=http://localhost:8000" > .env.local
```

**d) Instalar dependências:**
```bash
npm install
```

**e) Iniciar servidor de desenvolvimento:**
```bash
npm run dev
```

✅ Frontend rodando em: http://localhost:5173

### 5. TESTAR O SISTEMA

- Abra http://localhost:5173 no navegador
- Digite uma pergunta (ex: "O que é Umbanda?")
- Pressione "Perguntar" ou use Ctrl+Enter
- A resposta será exibida com os documentos consultados---

## ESTRUTURA DO PROJETO

```
aiye/
├── backend/                     # API FastAPI
│   ├── main.py                 # Servidor FastAPI (dev)
│   ├── app.py                  # Servidor FastAPI (produção HF)
│   ├── rag.py                  # Lógica de RAG
│   ├── models.py               # Modelos Pydantic
│   ├── settings.py             # Configurações
│   ├── ingest.py               # Script de ingestão
│   ├── init_index.py           # Inicialização do índice
│   ├── warmup.py               # Script de warmup
│   ├── requirements.txt        # Dependências Python
│   └── data/
│       ├── pdfs/               # PDFs para processar (7 arquivos)
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
├── Dockerfile                   # Container para HF Spaces
├── .gitattributes              # Config Git LFS
├── .env.example                # Variáveis de exemplo
└── *.md                        # Documentação
```

## FEATURES IMPLEMENTADAS

✅ **Backend:**
- FastAPI com endpoints `/healthz`, `/warmup` e `/ask`
- RAG completo com FAISS (busca vetorial local)
- Embeddings HuggingFace (all-MiniLM-L6-v2, 384 dim)
- Integração com Google Gemini 2.5 Flash
- Parsing de PDFs com PyMuPDF
- Chunking com overlap (1500 chars, 200 overlap)
- Metadados completos em JSON
- Logging detalhado para debug
- CORS configurado

✅ **Frontend:**
- Interface moderna estilo chat
- Tema personalizado "Aiye" (verde/azul)
- Visualização de fontes consultadas (sem download)
- Loading states e error handling
- Responsive design
- TypeScript para type safety

✅ **Deploy:**
- Backend no Hugging Face Spaces (Docker)
- Frontend na Vercel
- Git LFS para PDFs e índices
- Deploy automático via Git push
- Documentação completa

---

## DEPLOY EM PRODUÇÃO

### Arquitetura Atual

**Frontend (Vercel)** → **Backend (Hugging Face Spaces)** → **Gemini API**

### 1. Backend (Hugging Face Spaces)

**URL:** https://dev-mateus-backend-aiye.hf.space

**Passo a passo:**
1. Configure Git LFS: `git lfs install`
2. Adicione remote HF: `git remote add space https://huggingface.co/spaces/dev-mateus/backend-aiye`
3. Configure secrets no HF Space: `GOOGLE_API_KEY`
4. Faça deploy:
   ```bash
   git push space main
   ```

**Build automático:**
- Dockerfile executa `backend/init_index.py`
- PDFs e metadata.json baixados via Git LFS
- Container inicia na porta 7860
- Rebuild em ~5-10 minutos

Ver guia completo: [`DEPLOY_HUGGINGFACE.md`](./DEPLOY_HUGGINGFACE.md)

### 2. Frontend (Vercel)

**URL:** https://aiye-chat.vercel.app

**Passo a passo:**
1. Importe projeto do GitHub no Vercel
2. Configure variável de ambiente:
   - `VITE_API_BASE=https://dev-mateus-backend-aiye.hf.space`
3. Deploy automático a cada push na branch `main`

**Build automático:**
- Vite build com TypeScript check
- Deploy em ~1-2 minutos
- Preview deploys para cada PR

---

## NOTAS IMPORTANTES

1. O arquivo `.env` não deve ser commitado (está no `.gitignore`)
2. Os índices FAISS são gerados automaticamente no deploy do HF Spaces
3. Configure `GOOGLE_API_KEY` para usar o Gemini
4. PDFs já estão incluídos e versionados via Git LFS
5. Consulte o `README.md` para mais informações

---

## ERROS COMUNS

❌ **"Backend não está disponível"**  
→ Certifique-se que uvicorn está rodando em http://localhost:8000

❌ **"ModuleNotFoundError: No module named 'fastapi'"**  
→ Verifique se `.venv` está ativado e execute `pip install -r backend/requirements.txt`

❌ **"npm: command not found"**  
→ Instale Node.js em https://nodejs.org/

❌ **"Nenhum arquivo PDF encontrado"**  
→ Os PDFs já estão em `backend/data/pdfs/`. Execute `python backend/ingest.py`

❌ **"GOOGLE_API_KEY not configured"**  
→ Crie arquivo `.env` com `GOOGLE_API_KEY=sua_chave_aqui`

❌ **Build falha no HF Spaces**  
→ Verifique logs em https://huggingface.co/spaces/dev-mateus/backend-aiye/logs

---

## PRÓXIMOS PASSOS

1. ✅ Explore a aplicação em produção
2. 📚 Adicione novos PDFs em `backend/data/pdfs/`
3. 🔨 Execute `python backend/ingest.py` para atualizar índice
4. 🚀 Faça `git push space main` para deploy
5. 💡 Veja melhorias possíveis em `PROJECT_SUMMARY.md`

---

## SUPORTE

Consulte a documentação completa:
- **README.md** - Visão geral e instalação
- **DEVELOPMENT.md** - Detalhes técnicos
- **TESTING.md** - Testes e exemplos
- **PROJECT_SUMMARY.md** - Sumário completo

**Desenvolvido com ❤️ por [Mateus](https://github.com/dev-mateus)**

