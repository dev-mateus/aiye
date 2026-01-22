# Script para Limpar Credencial do Histórico do Git

## ⚠️ IMPORTANTE
# Este script usa BFG Repo-Cleaner para remover a credencial exposta de TODO o histórico do Git
# Execute este script DEPOIS de rotacionar a senha no Neon

## Pré-requisitos
# 1. Java instalado (para executar BFG)
# 2. BFG Repo-Cleaner baixado de: https://rtyley.github.io/bfg-repo-cleaner/

## Passos Manuais

# 1. Baixe BFG Repo-Cleaner
# Vá para: https://rtyley.github.io/bfg-repo-cleaner/
# Baixe o arquivo: bfg-1.14.0.jar (ou versão mais recente)
# Salve em: C:\Users\mateus\Downloads\

# 2. Crie arquivo com a senha a ser removida
Write-Host "Criando arquivo com senha comprometida..." -ForegroundColor Yellow
"npg_CHtQo6Uk9LEa" | Out-File -FilePath "$env:TEMP\passwords-to-remove.txt" -Encoding UTF8

# 3. Clone repositório como mirror
Write-Host "Clonando repositório como mirror..." -ForegroundColor Yellow
$tempDir = "$env:TEMP\aiye-cleanup"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
git clone --mirror https://github.com/dev-mateus/aiye.git $tempDir

# 4. Execute BFG para substituir a senha
Write-Host "Executando BFG para remover senha do histórico..." -ForegroundColor Yellow
Write-Host "NOTA: Certifique-se que bfg.jar está em C:\Users\mateus\Downloads\" -ForegroundColor Red
Push-Location $tempDir
java -jar C:\Users\mateus\Downloads\bfg.jar --replace-text "$env:TEMP\passwords-to-remove.txt"
Pop-Location

# 5. Limpe reflog e garbage collect
Write-Host "Limpando reflog e executando garbage collection..." -ForegroundColor Yellow
Push-Location $tempDir
git reflog expire --expire=now --all
git gc --prune=now --aggressive
Pop-Location

# 6. Force push para GitHub
Write-Host "" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Red
Write-Host "ATENÇÃO: O próximo comando fará FORCE PUSH!" -ForegroundColor Red
Write-Host "Isso REESCREVERÁ o histórico do repositório" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
$confirm = Read-Host "Deseja continuar? (digite 'SIM' em maiúsculas para confirmar)"

if ($confirm -eq "SIM") {
    Push-Location $tempDir
    git push --force
    Pop-Location
    
    Write-Host ""
    Write-Host "✅ Histórico limpo com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Yellow
    Write-Host "1. Clone novamente o repositório limpo: git clone https://github.com/dev-mateus/aiye.git" -ForegroundColor White
    Write-Host "2. Verifique que a senha não aparece mais: git log --all -S 'npg_CHtQo6Uk9LEa'" -ForegroundColor White
    Write-Host "3. Delete o diretório temporário: Remove-Item -Recurse -Force '$tempDir'" -ForegroundColor White
} else {
    Write-Host "Operação cancelada." -ForegroundColor Yellow
    Write-Host "Para executar manualmente:" -ForegroundColor Cyan
    Write-Host "  cd $tempDir" -ForegroundColor White
    Write-Host "  git push --force" -ForegroundColor White
}

Write-Host ""
Write-Host "Diretório temporário: $tempDir" -ForegroundColor Cyan
