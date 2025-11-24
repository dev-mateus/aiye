# 🚀 Deploy no Hugging Face Spaces

Este guia explica como fazer deploy do backend Aiye no Hugging Face Spaces usando Xet storage para os PDFs.

## 📋 Pré-requisitos

1. Conta no Hugging Face: https://huggingface.co/join
2. Git instalado
3. Hugging Face CLI instalado: `pip install huggingface_hub`
4. Git-Xet instalado para large files (recomendado)

## 🔧 Instalar Git-Xet

```bash
# Windows (via PowerShell)
iwr https://xetdata.com/install.ps1 -useb | iex

# macOS/Linux
curl -L https://xetdata.com/install.sh | sh
```

Após instalar, configure:
```bash
git xet install
```

## 📦 Passo 1: Criar Space no Hugging Face

1. Acesse: https://huggingface.co/new-space
2. Preencha:
   - **Owner:** `dev-mateus`
   - **Space name:** `backend-aiye`
   - **License:** Apache 2.0 (ou sua preferência)
   - **Select the Space SDK:** Docker
   - **Space hardware:** CPU basic (free)
3. Clique em **Create Space**

## 🔑 Passo 2: Autenticar com Hugging Face

```bash
# Login no Hugging Face
huggingface-cli login

# Cole seu token de acesso quando solicitado
# Token: https://huggingface.co/settings/tokens
```

## 📂 Passo 3: Adicionar Remote do Hugging Face

```bash
cd c:\Users\mateus\Documents\Projetos\aiye

# Adicionar remote do Hugging Face
git remote add hf https://huggingface.co/spaces/dev-mateus/backend-aiye

# Verificar remotes
git remote -v
```

## 🎯 Passo 4: Preparar Arquivos

Certifique-se que você tem:
- ✅ `Dockerfile` (já existe)
- ✅ `backend/app.py` (já existe)
- ✅ `.gitattributes` configurado com Xet
- ✅ PDFs em `backend/data/pdfs/`

## 📤 Passo 5: Fazer Push para Hugging Face

```bash
# Certificar que está na branch master
git checkout master

# Adicionar todos os arquivos (incluindo PDFs)
git add .

# Commit com mensagem descritiva
git commit -m "Deploy backend com PDFs usando Xet storage"

# Push para Hugging Face (primeira vez usa força para sobrescrever)
git push hf master --force

# Pushes futuros (sem --force)
git push hf master
```

## ⚙️ Passo 6: Configurar Variáveis de Ambiente

No Hugging Face Space:

1. Vá para **Settings** do seu Space
2. Em **Repository secrets**, adicione:
   - `GOOGLE_API_KEY`: Sua chave da API Google Gemini

## 🔍 Passo 7: Verificar Deploy

1. Aguarde o build completar (5-10 minutos primeira vez)
2. Acesse: `https://dev-mateus-backend-aiye.hf.space/healthz`
3. Teste: `https://dev-mateus-backend-aiye.hf.space/docs`

## 🧪 Testar API

```bash
# Health check
curl https://dev-mateus-backend-aiye.hf.space/healthz

# Warmup (carregar modelo)
curl https://dev-mateus-backend-aiye.hf.space/warmup

# Fazer pergunta
curl -X POST https://dev-mateus-backend-aiye.hf.space/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Quem fundou a Umbanda?"}'
```

## 🔄 Atualizações Futuras

Para updates do código:

```bash
# Fazer mudanças no código local
git add .
git commit -m "Descrição das mudanças"

# Push para GitHub
git push origin master

# Push para Hugging Face
git push hf master
```

Para adicionar novos PDFs:

```bash
# Adicionar PDF em backend/data/pdfs/
# O Xet storage vai lidar com o arquivo grande automaticamente

git add backend/data/pdfs/*.pdf
git commit -m "Add novo PDF: Nome do arquivo"
git push hf master
```

## 📝 Notas Importantes

### Sobre Xet Storage
- **Xet** é o sistema recomendado do Hugging Face para large files
- Substitui Git LFS e é otimizado para ML/AI workflows
- Não há custos adicionais para Spaces públicos
- PDFs são versionados mas não duplicam espaço

### Limites do Free Tier
- **Storage:** 5GB total
- **RAM:** 16GB
- **CPU:** 2 cores
- **Disk:** 50GB
- Se precisar mais, upgrade para paid tier

### Troubleshooting

**Erro: "Git LFS"**
- Certifique-se de usar `filter=xet` no `.gitattributes`
- Não use `filter=lfs`

**Erro: "Authentication failed"**
- Refaça login: `huggingface-cli login`
- Verifique token em https://huggingface.co/settings/tokens

**Build timeout:**
- Primeira build pode demorar
- Verifique logs em: Space → Logs

**Out of memory:**
- Considere usar `EMBEDDING_PROVIDER=remote` na env
- Ou faça upgrade do hardware do Space

## 🔗 Links Úteis

- Space: https://huggingface.co/spaces/dev-mateus/backend-aiye
- Docs Xet: https://xetdata.com/docs/
- HF Spaces Docs: https://huggingface.co/docs/hub/spaces
- HF Docker Spaces: https://huggingface.co/docs/hub/spaces-sdks-docker

## ✅ Checklist Final

Antes de fazer push:
- [ ] `.gitattributes` configurado com Xet
- [ ] `Dockerfile` presente na raiz
- [ ] `backend/app.py` criado
- [ ] `GOOGLE_API_KEY` configurada no Space
- [ ] PDFs estão em `backend/data/pdfs/`
- [ ] `git xet install` executado
- [ ] Remote `hf` adicionado
- [ ] Autenticado com `huggingface-cli login`

Boa sorte com o deploy! 🎉
