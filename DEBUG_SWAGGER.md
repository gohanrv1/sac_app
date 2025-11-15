# 🔍 Debugging Swagger UI "Failed to fetch"

## ✅ Cambios Realizados

1. **Endpoint `/apispec.json` mejorado** - Detecta host dinámicamente
2. **CORS mejorado** - Headers `Accept` agregados
3. **Headers en todas las respuestas** - CORS consistente

## 🐛 Diagnóstico del Problema

Si curl funciona pero Swagger UI no, el problema es que Swagger UI está haciendo peticiones desde el navegador que fallan.

### Paso 1: Verificar en el Navegador

1. Abre Swagger UI: `http://electo-infosac.fxtfoe.easypanel.host/apidocs/`
2. Abre la consola del navegador (F12)
3. Ve a la pestaña **Network**
4. Intenta ejecutar un endpoint
5. Busca la petición que falla (estará en rojo)

### Paso 2: Verificar el Host

Abre en el navegador:
```
http://electo-infosac.fxtfoe.easypanel.host/apispec.json
```

Verifica que el campo `host` sea correcto. Debería ser algo como:
- `electo-infosac.fxtfoe.easypanel.host:5000` (si el puerto está expuesto)
- O `electo-infosac.fxtfoe.easypanel.host` (si está detrás de un proxy)

### Paso 3: Verificar Headers CORS

En la pestaña Network del navegador, verifica que las respuestas tengan:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET,PUT,POST,DELETE,OPTIONS`
- `Access-Control-Allow-Headers: Content-Type,Accept,X-User-Celular,Authorization`

## 🔧 Soluciones Posibles

### Solución 1: Verificar el Puerto

Si el servidor está detrás de un proxy (como Easypanel), el puerto puede no estar en el host. Prueba forzar el host sin puerto:

Edita `get_swagger_spec()` en `infotaxi_api.py`:

```python
current_host = request.host
# Si está detrás de un proxy, quitar el puerto
if ':' in current_host and current_host.split(':')[1] == '5000':
    current_host = current_host.split(':')[0]
spec['host'] = current_host
```

### Solución 2: Verificar HTTPS

Si el servidor usa HTTPS pero Swagger detecta HTTP, fuerza HTTPS:

```python
# En get_swagger_spec()
if 'easypanel.host' in current_host:
    current_scheme = 'https'  # Forzar HTTPS si es necesario
```

### Solución 3: Verificar Proxy/Reverse Proxy

Si hay un reverse proxy (nginx, etc.), puede estar bloqueando las peticiones. Verifica la configuración del proxy.

## 📝 Verificación Rápida

```bash
# 1. Verificar que apispec.json funciona
curl http://electo-infosac.fxtfoe.easypanel.host/apispec.json | grep host

# 2. Verificar headers CORS
curl -I -X OPTIONS http://electo-infosac.fxtfoe.easypanel.host/api/health

# 3. Probar endpoint directamente
curl http://electo-infosac.fxtfoe.easypanel.host/api/health
```

## 🎯 Próximos Pasos

1. Reconstruir el contenedor con el código actualizado
2. Verificar en la consola del navegador qué petición está fallando
3. Verificar el host en `/apispec.json`
4. Si el problema persiste, compartir:
   - El host que aparece en `/apispec.json`
   - Los errores de la consola del navegador
   - El scheme (http/https) que está usando

