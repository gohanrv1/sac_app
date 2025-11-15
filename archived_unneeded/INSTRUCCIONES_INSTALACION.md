# 📋 Instrucciones de Instalación y Uso

## 🔧 Instalación de Dependencias

### Opción 1: Instalación Automática (Recomendado)

Ejecuta el script de instalación:

```powershell
python instalar_dependencias.py
```

### Opción 2: Instalación Manual

```powershell
pip install -r requirements.txt
```

O instala cada paquete individualmente:

```powershell
pip install Flask flask-cors mysql-connector-python Flasgger pandas openpyxl python-dotenv
```

## 🚀 Iniciar el Servidor

Una vez instaladas las dependencias, inicia el servidor:

```powershell
python infotaxi_api.py
```

Deberías ver:

```
============================================================
🚕 API InfoTaxi iniciando...
============================================================
📡 Servidor: http://localhost:5000
📚 Documentación Swagger: http://localhost:5000/apidocs/
🔍 Health Check: http://localhost:5000/api/health
============================================================
 * Running on http://0.0.0.0:5000
```

## 🧪 Probar los Endpoints

### Opción 1: Usar Swagger UI (Recomendado)

1. Abre tu navegador en: `http://localhost:5000/apidocs/`
2. Prueba primero el endpoint `/api/health`
3. Luego prueba `/api/usuarios` con los datos de ejemplo

### Opción 2: Usar el Script de Pruebas

En otra terminal:

```powershell
python test_api.py
```

### Opción 3: Usar cURL

```powershell
# Health Check
curl http://localhost:5000/api/health

# Crear Usuario
curl -X POST http://localhost:5000/api/usuarios ^
  -H "Content-Type: application/json" ^
  -d "{\"celular\":\"3006413771\",\"nombres\":\"Juan Pérez\",\"password\":\"contraseña123\",\"username\":\"usuario@ejemplo.com\"}"
```

## ⚠️ Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'flask_cors'"

**Solución:**
```powershell
python -m pip install flask-cors --upgrade
```

### Error: "TypeError: Failed to fetch" en Swagger UI

**Causas posibles:**
1. El servidor no está corriendo
2. Las dependencias no están instaladas
3. Problema de CORS (ya está configurado en el código)

**Solución:**
1. Verifica que el servidor esté corriendo: `netstat -ano | findstr :5000`
2. Verifica que puedas acceder a: `http://localhost:5000/api/health`
3. Revisa la consola del servidor para ver errores

### Error: "No se puede conectar al servidor"

**Solución:**
1. Asegúrate de que el servidor esté corriendo
2. Verifica que no haya otro proceso usando el puerto 5000
3. Intenta cambiar el puerto en `infotaxi_api.py` (línea 1316)

## 📝 Notas Importantes

- **Python 3.13**: Si tienes problemas con Python 3.13, considera usar Python 3.11 o 3.12
- **Puerto 5000**: Si el puerto está ocupado, cambia el puerto en la línea 1316 de `infotaxi_api.py`
- **Base de Datos**: Asegúrate de que las credenciales en `DB_CONFIG` (línea 103-109) sean correctas

## 🔍 Verificar Instalación

Para verificar que todo está instalado correctamente:

```powershell
python -c "from flask import Flask; from flask_cors import CORS; from flasgger import Swagger; import mysql.connector; print('✅ Todas las dependencias están instaladas')"
```

Si no hay errores, todo está listo para usar.

