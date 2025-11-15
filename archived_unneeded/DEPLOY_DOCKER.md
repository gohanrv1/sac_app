# 🐳 Guía de Despliegue con Docker

## ✅ El Dockerfile ya está configurado para instalar todo automáticamente

El Dockerfile está configurado para:
- ✅ Instalar todas las dependencias del sistema (MySQL, gcc, etc.)
- ✅ Instalar todas las dependencias de Python desde `requirements.txt`
- ✅ Instalar Gunicorn para producción
- ✅ Configurar el servidor automáticamente

## 🚀 Despliegue en el Servidor

### Opción 1: Usando Docker Compose (Recomendado)

```bash
# 1. Sube todos los archivos al servidor
# 2. En el servidor, ejecuta:
docker-compose up -d --build
```

### Opción 2: Usando Docker directamente

```bash
# 1. Construir la imagen (instala todo automáticamente)
docker build -t infotaxi-api .

# 2. Ejecutar el contenedor
docker run -d \
  --name infotaxi-api \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DOCKER_ENV=true \
  --restart unless-stopped \
  infotaxi-api
```

## 📋 Lo que se instala automáticamente

### Dependencias del Sistema:
- `gcc` - Compilador C
- `default-libmysqlclient-dev` - Cliente MySQL/MariaDB
- `pkg-config` - Herramientas de configuración
- `curl` - Para health checks

### Dependencias de Python (desde requirements.txt):
- `Flask>=3.0.0` - Framework web
- `flask-cors>=4.0.0` - Soporte CORS
- `mysql-connector-python>=8.3.0` - Conector MySQL
- `Flasgger>=0.9.7` - Swagger UI
- `pandas>=2.0.0` - Procesamiento de datos
- `openpyxl>=3.1.0` - Manejo de Excel
- `python-dotenv>=1.0.1` - Variables de entorno
- `gunicorn>=21.2.0` - Servidor WSGI para producción

## 🔧 Verificar que todo se instaló correctamente

```bash
# Ver logs de construcción
docker build -t infotaxi-api . 2>&1 | grep -i "installing\|installed\|success"

# Verificar paquetes instalados en el contenedor
docker run --rm infotaxi-api pip list

# Verificar que el servidor funciona
docker run --rm -p 5000:5000 infotaxi-api
# Luego en otra terminal:
curl http://localhost:5000/api/health
```

## 📝 Archivos necesarios en el servidor

Asegúrate de tener estos archivos en el servidor:

```
sac_app/
├── Dockerfile              ✅ (instala todo automáticamente)
├── requirements.txt        ✅ (lista de dependencias Python)
├── docker-compose.yml      ✅ (configuración opcional)
├── .dockerignore           ✅ (optimiza la construcción)
├── infotaxi_api.py         ✅ (aplicación principal)
└── (otros archivos del proyecto)
```

## 🎯 Comandos rápidos

```bash
# Construir e iniciar
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Reiniciar
docker-compose restart

# Ver estado
docker-compose ps
```

## ⚙️ Variables de Entorno (Opcional)

Si necesitas configurar variables de entorno, edita `docker-compose.yml`:

```yaml
environment:
  - FLASK_ENV=production
  - DOCKER_ENV=true
  - DB_HOST=tu_host
  - DB_PORT=4646
  # etc...
```

O pásalas al ejecutar:

```bash
docker run -d \
  -e DB_HOST=31.97.130.20 \
  -e DB_PORT=4646 \
  infotaxi-api
```

## 🔍 Solución de Problemas

### Error al construir la imagen

```bash
# Ver logs detallados
docker build -t infotaxi-api . --no-cache

# Verificar que requirements.txt existe
cat requirements.txt
```

### Error al iniciar el contenedor

```bash
# Ver logs del contenedor
docker logs infotaxi-api

# Verificar que el puerto no esté ocupado
netstat -tulpn | grep 5000
```

### Verificar instalación de dependencias

```bash
# Entrar al contenedor
docker exec -it infotaxi-api bash

# Dentro del contenedor:
pip list
python -c "from flask import Flask; print('Flask OK')"
python -c "from flask_cors import CORS; print('CORS OK')"
```

## ✅ Checklist de Despliegue

- [ ] Todos los archivos están en el servidor
- [ ] Docker está instalado en el servidor
- [ ] `requirements.txt` está actualizado
- [ ] `Dockerfile` está presente
- [ ] Ejecutar `docker-compose up -d --build`
- [ ] Verificar logs: `docker-compose logs -f`
- [ ] Probar endpoint: `curl http://localhost:5000/api/health`
- [ ] Probar Swagger: `http://tu-servidor:5000/apidocs/`

## 🎉 ¡Listo!

Una vez que ejecutes `docker-compose up -d --build` o `docker build`, **todo se instalará automáticamente**. No necesitas instalar nada manualmente en el servidor.

