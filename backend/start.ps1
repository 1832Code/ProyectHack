# ================================================
# Script de Inicio Rápido - Backend Flask
# ================================================

Write-Host "🚀 Iniciando Backend Flask..." -ForegroundColor Cyan
Write-Host ""

# Verificar si existe el archivo .env
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  ADVERTENCIA: No se encontró el archivo .env" -ForegroundColor Yellow
    Write-Host "   Por favor, crea el archivo .env con tus credenciales" -ForegroundColor Yellow
    Write-Host "   Puedes usar .env.example como plantilla" -ForegroundColor Yellow
    Write-Host ""
    
    $continue = Read-Host "¿Deseas continuar de todas formas? (s/n)"
    if ($continue -ne "s") {
        Write-Host "❌ Inicio cancelado" -ForegroundColor Red
        exit
    }
}

# Verificar dependencias
Write-Host "📦 Verificando dependencias..." -ForegroundColor Green
try {
    python -c "import flask, flask_cors, mysql.connector, openai, decouple"
    Write-Host "✓ Todas las dependencias están instaladas" -ForegroundColor Green
} catch {
    Write-Host "❌ Faltan dependencias. Instalando..." -ForegroundColor Red
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Backend Flask - Puerto 5000" -ForegroundColor Cyan
Write-Host "  http://localhost:5000" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar el servidor
python main.py
