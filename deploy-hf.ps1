# Script para configurar e fazer push para Hugging Face
# Execute este script para fazer deploy no HF Spaces

Write-Host "🚀 Deploy Aiye para Hugging Face Spaces" -ForegroundColor Green
Write-Host ""

# Verificar se está na pasta correta
$currentDir = Get-Location
if (-not (Test-Path "backend/app.py")) {
    Write-Host "❌ Execute este script da raiz do projeto aiye" -ForegroundColor Red
    exit 1
}

# Verificar se git-xet está instalado
$xetInstalled = git xet 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Git-Xet não está instalado. Instalando..." -ForegroundColor Yellow
    iwr https://xetdata.com/install.ps1 -useb | iex
    git xet install
}

# Verificar se Hugging Face CLI está instalado
$hfInstalled = huggingface-cli --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Hugging Face CLI não está instalado. Instalando..." -ForegroundColor Yellow
    pip install huggingface_hub
}

# Verificar autenticação HF
Write-Host "🔑 Verificando autenticação Hugging Face..." -ForegroundColor Cyan
$whoami = huggingface-cli whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Não autenticado. Fazendo login..." -ForegroundColor Yellow
    huggingface-cli login
}

# Verificar se remote HF já existe
$remotes = git remote
if ($remotes -notcontains "hf") {
    Write-Host "📡 Adicionando remote Hugging Face..." -ForegroundColor Cyan
    git remote add hf https://huggingface.co/spaces/dev-mateus/backend-aiye
} else {
    Write-Host "✅ Remote Hugging Face já configurado" -ForegroundColor Green
}

Write-Host ""
Write-Host "📂 Arquivos que serão enviados:" -ForegroundColor Cyan
Write-Host "  - Dockerfile"
Write-Host "  - backend/app.py"
Write-Host "  - backend/requirements.txt"
Write-Host "  - backend/*.py (todos módulos)"
Write-Host "  - backend/data/pdfs/*.pdf (via Xet storage)"
Write-Host "  - .gitattributes (config Xet)"
Write-Host ""

# Confirmação
$confirm = Read-Host "Deseja continuar com o push para Hugging Face? (s/n)"
if ($confirm -ne "s") {
    Write-Host "❌ Deploy cancelado" -ForegroundColor Red
    exit 0
}

# Status atual
Write-Host ""
Write-Host "📊 Status do repositório:" -ForegroundColor Cyan
git status --short

# Adicionar arquivos
Write-Host ""
Write-Host "➕ Adicionando arquivos..." -ForegroundColor Cyan
git add .

# Commit
$commitMsg = Read-Host "Mensagem do commit (Enter para usar padrão)"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Update: Deploy Aiye backend to Hugging Face"
}

Write-Host "💾 Fazendo commit..." -ForegroundColor Cyan
git commit -m $commitMsg

# Push para GitHub primeiro (backup)
Write-Host ""
Write-Host "⬆️  Push para GitHub (backup)..." -ForegroundColor Cyan
git push origin master

# Push para Hugging Face
Write-Host ""
Write-Host "🚀 Push para Hugging Face Spaces..." -ForegroundColor Cyan
Write-Host "   Isso pode demorar alguns minutos (PDFs são grandes)..." -ForegroundColor Yellow

$pushHF = Read-Host "Usar --force? (s/n) - Use 's' apenas na primeira vez"
if ($pushHF -eq "s") {
    git push hf master --force
} else {
    git push hf master
}

# Resultado
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 Links úteis:" -ForegroundColor Cyan
    Write-Host "   Space: https://huggingface.co/spaces/dev-mateus/backend-aiye" -ForegroundColor Blue
    Write-Host "   App: https://dev-mateus-backend-aiye.hf.space" -ForegroundColor Blue
    Write-Host "   Logs: https://huggingface.co/spaces/dev-mateus/backend-aiye/logs" -ForegroundColor Blue
    Write-Host ""
    Write-Host "⏳ Aguarde 5-10 minutos para o build completar" -ForegroundColor Yellow
    Write-Host "   Você pode acompanhar em tempo real nos Logs acima" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🧪 Teste a API:" -ForegroundColor Cyan
    Write-Host "   curl https://dev-mateus-backend-aiye.hf.space/healthz" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "❌ Erro no deploy. Verifique as mensagens acima." -ForegroundColor Red
    Write-Host "   Dica: Certifique-se que está autenticado e tem permissões no Space" -ForegroundColor Yellow
}
