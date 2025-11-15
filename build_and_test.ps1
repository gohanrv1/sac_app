# Script PowerShell para construir y probar el contenedor Docker

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🐳 Construyendo imagen Docker..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Construir la imagen
docker build -t infotaxi-api .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al construir la imagen" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Imagen construida exitosamente" -ForegroundColor Green
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Iniciando contenedor..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Detener contenedor existente si existe
docker stop infotaxi-api 2>$null
docker rm infotaxi-api 2>$null

# Ejecutar el contenedor
docker run -d `
  --name infotaxi-api `
  -p 5000:5000 `
  -e FLASK_ENV=production `
  -e DOCKER_ENV=true `
  infotaxi-api

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al iniciar el contenedor" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Contenedor iniciado" -ForegroundColor Green
Write-Host ""
Write-Host "⏳ Esperando 10 segundos para que el servidor inicie..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🧪 Probando endpoints..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Probar health check
Write-Host "1. Probando /api/health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Health check OK" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5 | Write-Host
} catch {
    Write-Host "❌ Health check falló: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Logs del contenedor:" -ForegroundColor Yellow
    docker logs infotaxi-api --tail 50
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Todo funcionando correctamente!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Swagger UI: http://localhost:5000/apidocs/" -ForegroundColor Cyan
Write-Host "🔍 Health Check: http://localhost:5000/api/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para ver los logs:" -ForegroundColor Yellow
Write-Host "  docker logs -f infotaxi-api" -ForegroundColor White
Write-Host ""
Write-Host "Para detener el contenedor:" -ForegroundColor Yellow
Write-Host "  docker stop infotaxi-api" -ForegroundColor White
Write-Host "  docker rm infotaxi-api" -ForegroundColor White

