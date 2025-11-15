# Script para iniciar el servidor y probar los endpoints
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚕 Iniciando API InfoTaxi" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Verificar si el servidor ya está corriendo
$port = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($port) {
    Write-Host "⚠️  El puerto 5000 ya está en uso" -ForegroundColor Yellow
    Write-Host "Deteniendo procesos en el puerto 5000..." -ForegroundColor Yellow
    $processId = $port.OwningProcess
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Iniciar el servidor en segundo plano
Write-Host "`n📡 Iniciando servidor Flask..." -ForegroundColor Green
$job = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python infotaxi_api.py
}

# Esperar a que el servidor inicie
Write-Host "⏳ Esperando 8 segundos para que el servidor inicie..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Probar el endpoint de health
Write-Host "`n🔍 Probando endpoint /api/health..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Health Check OK!" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5 | Write-Host
} catch {
    Write-Host "❌ Error al conectar con el servidor: $_" -ForegroundColor Red
    Write-Host "`nAsegúrate de que el servidor esté corriendo manualmente:" -ForegroundColor Yellow
    Write-Host "   python infotaxi_api.py" -ForegroundColor Yellow
    Stop-Job $job -ErrorAction SilentlyContinue
    Remove-Job $job -ErrorAction SilentlyContinue
    exit 1
}

# Probar crear usuario
Write-Host "`n👤 Probando POST /api/usuarios..." -ForegroundColor Cyan
$timestamp = [int][double]::Parse((Get-Date -UFormat %s))
$usuarioData = @{
    celular = "3006413771"
    nombres = "Juan Pérez Test"
    password = "contraseña123"
    username = "test_$timestamp@ejemplo.com"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/usuarios" -Method POST -Body $usuarioData -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ Usuario creado/verificado exitosamente!" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5 | Write-Host
} catch {
    Write-Host "⚠️  Respuesta: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Yellow
    if ($_.Exception.Response.StatusCode.value__ -eq 409) {
        Write-Host "   (Usuario ya existe - esto es esperado si ya se probó antes)" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✅ Pruebas completadas" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n📚 Swagger UI disponible en: http://localhost:5000/apidocs/" -ForegroundColor Cyan
Write-Host "`nPara detener el servidor, presiona Ctrl+C o ejecuta:" -ForegroundColor Yellow
Write-Host "   Stop-Job -Id $($job.Id); Remove-Job -Id $($job.Id)" -ForegroundColor Yellow

