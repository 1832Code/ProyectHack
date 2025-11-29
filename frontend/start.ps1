# ================================================
# Script de Inicio Rápido - Frontend Next.js
# ================================================

Write-Host "🚀 Iniciando Frontend Next.js..." -ForegroundColor Cyan
Write-Host ""

# Verificar si existe node_modules
if (-Not (Test-Path "node_modules")) {
    Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
    npm install
    Write-Host ""
}

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Frontend Next.js - Puerto 3000" -ForegroundColor Cyan
Write-Host "  http://localhost:3000" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar el servidor de desarrollo
npm run dev
