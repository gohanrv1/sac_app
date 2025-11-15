#!/bin/bash
# Script para construir y probar el contenedor Docker

echo "=========================================="
echo "🐳 Construyendo imagen Docker..."
echo "=========================================="

# Construir la imagen
docker build -t infotaxi-api .

if [ $? -ne 0 ]; then
    echo "❌ Error al construir la imagen"
    exit 1
fi

echo ""
echo "✅ Imagen construida exitosamente"
echo ""
echo "=========================================="
echo "🚀 Iniciando contenedor..."
echo "=========================================="

# Detener contenedor existente si existe
docker stop infotaxi-api 2>/dev/null
docker rm infotaxi-api 2>/dev/null

# Ejecutar el contenedor
docker run -d \
  --name infotaxi-api \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DOCKER_ENV=true \
  infotaxi-api

if [ $? -ne 0 ]; then
    echo "❌ Error al iniciar el contenedor"
    exit 1
fi

echo "✅ Contenedor iniciado"
echo ""
echo "⏳ Esperando 10 segundos para que el servidor inicie..."
sleep 10

echo ""
echo "=========================================="
echo "🧪 Probando endpoints..."
echo "=========================================="

# Probar health check
echo "1. Probando /api/health..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health)

if [ "$response" = "200" ]; then
    echo "✅ Health check OK (Status: $response)"
    curl -s http://localhost:5000/api/health | python -m json.tool
else
    echo "❌ Health check falló (Status: $response)"
    echo "Logs del contenedor:"
    docker logs infotaxi-api --tail 50
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Todo funcionando correctamente!"
echo "=========================================="
echo ""
echo "📚 Swagger UI: http://localhost:5000/apidocs/"
echo "🔍 Health Check: http://localhost:5000/api/health"
echo ""
echo "Para ver los logs:"
echo "  docker logs -f infotaxi-api"
echo ""
echo "Para detener el contenedor:"
echo "  docker stop infotaxi-api"
echo "  docker rm infotaxi-api"

