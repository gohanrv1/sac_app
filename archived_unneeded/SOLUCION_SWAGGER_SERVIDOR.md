# 🔧 Solución para "Failed to fetch" en Swagger UI del Servidor

## ✅ Cambios Realizados

### 1. Endpoint `/apispec.json` Mejorado
- Detecta automáticamente el host desde la petición
- Actualiza el scheme (http/https) dinámicamente
- Manejo de errores mejorado

### 2. CORS Mejorado
- Headers CORS en todas las rutas necesarias
- Incluye `/flasgger_static/*` para recursos estáticos
- Headers `Accept` agregados

### 3. Headers de Respuesta
- `Access-Control-Max-Age` para cachear preflight
- Headers CORS consistentes en todas las respuestas

## 🚀 Desplegar en el Servidor

### Paso 1: Subir el código actualizado

### Paso 2: Reconstruir el contenedor

```bash
docker-compose down
docker-compose up -d --build
```

O con Docker directamente:

```bash
docker stop infotaxi-api
docker rm infotaxi-api
docker build -t infotaxi-api .
docker run -d --name infotaxi-api -p 5000:5000 infotaxi-api
```

### Paso 3: Verificar

```bash
# Verificar que el host sea correcto
curl http://electo-infosac.fxtfoe.easypanel.host/apispec.json | grep -i host

# Probar un endpoint
curl http://electo-infosac.fxtfoe.easypanel.host/api/health
```

## 🔍 Verificación en Swagger UI

1. Abre: `http://electo-infosac.fxtfoe.easypanel.host/apidocs/`
2. Abre la consola del navegador (F12)
3. Intenta ejecutar un endpoint
4. Revisa si hay errores en la consola

## 🐛 Si Aún No Funciona

### Verificar en la consola del navegador (F12):

1. **Network Tab**: Ver qué petición está fallando
2. **Console Tab**: Ver errores de JavaScript
3. **Verificar el host en apispec.json**:
   - Abre: `http://electo-infosac.fxtfoe.easypanel.host/apispec.json`
   - Verifica que el campo `host` sea: `electo-infosac.fxtfoe.easypanel.host:5000` (o el puerto correcto)

### Posibles Problemas:

1. **Puerto incorrecto**: Si el servidor está detrás de un proxy, el puerto puede ser diferente
2. **HTTPS vs HTTP**: Verifica que el scheme sea correcto
3. **Firewall/Proxy**: Puede estar bloqueando peticiones

### Solución Manual (si es necesario):

Si el host detectado no es correcto, puedes forzarlo editando el endpoint:

```python
# En get_swagger_spec(), después de obtener current_host:
if 'fxtfoe.easypanel.host' in current_host:
    # Ajustar host si es necesario
    spec['host'] = current_host  # o forzar un valor específico
```

## ✅ Checklist

- [ ] Código actualizado subido al servidor
- [ ] Contenedor reconstruido
- [ ] `/apispec.json` devuelve el host correcto
- [ ] Headers CORS presentes en las respuestas
- [ ] Swagger UI carga correctamente
- [ ] Endpoints funcionan desde Swagger UI

