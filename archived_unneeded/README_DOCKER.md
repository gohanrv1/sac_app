# 🐳 Guía de Docker - API InfoTaxi

## 📋 Requisitos Previos

- Docker instalado
- Docker Compose instalado (opcional, pero recomendado)

## 🚀 Construcción y Ejecución

### Opción 1: Usando Docker Compose (Recomendado)

```bash
# Construir y ejecutar
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

### Opción 2: Usando Docker directamente

```bash
# Construir la imagen
docker build -t infotaxi-api .

# Ejecutar el contenedor
docker run -d \
  --name infotaxi-api \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DOCKER_ENV=true \
  infotaxi-api

# Ver logs
docker logs -f infotaxi-api

# Detener
docker stop infotaxi-api
docker rm infotaxi-api
```

## 🔧 Configuración

### Variables de Entorno

Puedes configurar variables de entorno editando `docker-compose.yml` o pasándolas al ejecutar:

```bash
docker run -d \
  --name infotaxi-api \
  -p 5000:5000 \
  -e DB_HOST=tu_host \
  -e DB_PORT=4646 \
  -e DB_DATABASE=tu_database \
  -e DB_USER=tu_usuario \
  -e DB_PASSWORD=tu_password \
  infotaxi-api
```

### Puerto

Por defecto, el contenedor expone el puerto 5000. Para cambiar el puerto:

```bash
docker run -d -p 8080:5000 infotaxi-api
```

## 🧪 Verificar que Funciona

### 1. Health Check

```bash
curl http://localhost:5000/api/health
```

### 2. Swagger UI

Abre en tu navegador: `http://localhost:5000/apidocs/`

### 3. Verificar logs

```bash
docker logs infotaxi-api
```

## 📊 Monitoreo

### Ver estado del contenedor

```bash
docker ps
```

### Ver uso de recursos

```bash
docker stats infotaxi-api
```

### Health Check

El contenedor incluye un health check automático. Verifica el estado:

```bash
docker inspect --format='{{.State.Health.Status}}' infotaxi-api
```

## 🔍 Solución de Problemas

### El contenedor no inicia

```bash
# Ver logs detallados
docker logs infotaxi-api

# Verificar que el puerto no esté ocupado
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac
```

### Error de conexión a la base de datos

1. Verifica las credenciales en `infotaxi_api.py` (líneas 103-109)
2. Asegúrate de que la base de datos sea accesible desde el contenedor
3. Si la BD está en otro servidor, verifica firewall/red

### Reconstruir desde cero

```bash
# Detener y eliminar contenedores
docker-compose down

# Eliminar imagen
docker rmi infotaxi-api

# Reconstruir
docker-compose up --build
```

## 🚀 Despliegue en Producción

### Recomendaciones

1. **Usar Gunicorn**: Ya está configurado en el Dockerfile
2. **Variables de entorno**: No hardcodear credenciales
3. **HTTPS**: Usar un reverse proxy (nginx) con SSL
4. **Logs**: Configurar rotación de logs
5. **Backups**: Configurar backups de la base de datos

### Ejemplo con Nginx (opcional)

```nginx
server {
    listen 80;
    server_name api.tudominio.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📝 Notas

- El contenedor usa **Gunicorn** en producción (4 workers, 2 threads)
- El health check verifica `/api/health` cada 30 segundos
- Los logs se muestran en stdout/stderr
- El usuario dentro del contenedor es `appuser` (no-root) para seguridad

