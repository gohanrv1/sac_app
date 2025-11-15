# 🚀 Instrucciones Rápidas para el Servidor

## ⚡ Inicio Rápido

En el servidor, simplemente ejecuta:

```bash
docker-compose up -d --build
```

**¡Eso es todo!** Docker instalará automáticamente:
- ✅ Todas las dependencias del sistema
- ✅ Todas las dependencias de Python
- ✅ Gunicorn para producción
- ✅ Configurará y ejecutará el servidor

## 📋 Comandos Útiles

```bash
# Iniciar el servidor
docker-compose up -d --build

# Ver logs en tiempo real
docker-compose logs -f

# Detener el servidor
docker-compose down

# Reiniciar el servidor
docker-compose restart

# Ver estado
docker-compose ps
```

## 🔍 Verificar que Funciona

```bash
# Health check
curl http://localhost:5000/api/health

# O desde fuera del servidor
curl http://tu-servidor:5000/api/health
```

## 📚 Swagger UI

Una vez iniciado, accede a:
```
http://tu-servidor:5000/apidocs/
```

## ⚠️ Nota Importante

**NO necesitas instalar nada manualmente**. El Dockerfile se encarga de todo automáticamente cuando ejecutas `docker-compose up -d --build`.

