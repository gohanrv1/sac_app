# 🚀 Iniciar y Probar el Servidor Localmente

## Paso 1: Instalar Dependencias (si no están instaladas)

```powershell
pip install -r requirements.txt
```

O instala manualmente:
```powershell
pip install flask flask-cors mysql-connector-python flasgger pandas openpyxl python-dotenv
```

## Paso 2: Iniciar el Servidor

Abre una terminal PowerShell en la carpeta del proyecto y ejecuta:

```powershell
python infotaxi_api.py
```

Deberías ver:
```
============================================================
🚕 API InfoTaxi iniciando...
============================================================
📡 Servidor: http://0.0.0.0:5000
📚 Documentación Swagger: http://0.0.0.0:5000/apidocs/
🔍 Health Check: http://0.0.0.0:5000/api/health
============================================================
 * Running on http://0.0.0.0:5000
```

**⚠️ IMPORTANTE: Deja esta terminal abierta mientras uses el servidor**

## Paso 3: Abrir Swagger UI

1. Abre tu navegador
2. Ve a: `http://localhost:5000/apidocs/`
3. Deberías ver la interfaz de Swagger UI con todos los endpoints

## Paso 4: Probar Endpoints en Swagger UI

### Probar `/api/health`:
1. Busca "GET /api/health" en Swagger UI
2. Haz clic en el endpoint
3. Haz clic en "Try it out"
4. Haz clic en "Execute"
5. Deberías ver la respuesta JSON

### Probar `/api/usuarios` (Crear Usuario):
1. Busca "POST /api/usuarios"
2. Haz clic en "Try it out"
3. Edita el JSON de ejemplo:
   ```json
   {
     "celular": "3006413771",
     "nombres": "Juan Pérez",
     "password": "contraseña123",
     "username": "usuario@ejemplo.com"
   }
   ```
4. Haz clic en "Execute"
5. Deberías ver la respuesta (201 si se crea, 409 si ya existe)

### Probar `/api/verificar-usuario`:
1. Busca "POST /api/verificar-usuario"
2. Haz clic en "Try it out"
3. Edita el JSON:
   ```json
   {
     "celular": "3006413771"
   }
   ```
4. Haz clic en "Execute"

## Paso 5: Probar con Script (Opcional)

En otra terminal, ejecuta:

```powershell
python probar_endpoints.py
```

Este script probará automáticamente varios endpoints.

## 🔍 Verificación Rápida

Si quieres verificar que el servidor está funcionando:

```powershell
# Con PowerShell
Invoke-RestMethod -Uri http://localhost:5000/api/health

# O con curl
curl http://localhost:5000/api/health
```

## ⚠️ Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'flask_cors'"
```powershell
pip install flask-cors
```

### Error: "Address already in use"
El puerto 5000 está ocupado. Cambia el puerto en `infotaxi_api.py` línea 1336:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Cambia a 5001
```

### "Failed to fetch" en Swagger UI
1. Verifica que el servidor esté corriendo
2. Abre la consola del navegador (F12) para ver errores
3. Prueba acceder directamente a: `http://localhost:5000/api/health`

### El servidor no inicia
Revisa la terminal donde ejecutaste `python infotaxi_api.py` para ver los errores.

## ✅ Checklist

- [ ] Dependencias instaladas
- [ ] Servidor corriendo (`python infotaxi_api.py`)
- [ ] Swagger UI accesible en `http://localhost:5000/apidocs/`
- [ ] Endpoint `/api/health` funciona
- [ ] Puedes probar endpoints desde Swagger UI

## 🎉 ¡Listo!

Una vez que el servidor esté corriendo, puedes usar Swagger UI para probar todos los endpoints de forma interactiva.

