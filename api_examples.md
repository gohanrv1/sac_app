# 📚 Guía de Uso - API InfoTaxi

## 🚀 Instalación

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar base de datos
# Editar DB_CONFIG en app.py con tus credenciales

# 3. Iniciar servidor
python app.py
```

El servidor iniciará en: `http://localhost:5000`

---

## 📡 Endpoints Disponibles

### 1. **Verificar si API está funcionando**
```bash
GET /api/health
```

**Respuesta:**
```json
{
  "success": true,
  "message": "API InfoTaxi funcionando correctamente",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

### 2. **Verificar si un usuario existe**
```bash
POST /api/verificar-usuario
Content-Type: application/json

{
  "celular": "3007471199"
}
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "exists": true,
  "usuario": {
    "id": 3,
    "nombre": "Admicars",
    "email": "jandrezapata@hotmail.com",
    "rol": "admin",
    "activo": true
  }
}
```

---

### 3. **Crear nuevo usuario**
```bash
POST /api/usuarios
Content-Type: application/json

{
  "username": "nuevo@ejemplo.com",
  "nombres": "Juan Pérez",
  "celular": "3001234567",
  "password": "mipassword123"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Usuario creado exitosamente",
  "id_user": 34
}
```

---

### 4. **Consultar persona por cédula**
```bash
GET /api/personas/8497643
Headers:
  X-User-Celular: 3007471199
```

**Respuesta:**
```json
{
  "success": true,
  "found": true,
  "total_reportes": 1,
  "reportes": [
    {
      "id": 12,
      "fecha_reporte": "2019-07-29",
      "numero_documento": "8497643",
      "nombres": "ADAIR MANUEL",
      "apellidos": "RUA TORRES",
      "fecha_cierre": "",
      "placa": "SXQ286",
      "valor_reporte": 319000,
      "descripcion": "TARIFA.",
      "vehiculo_afiliado": "ADMICARS",
      "estado": "ACTIVA"
    }
  ]
}
```

---

### 5. **Descargar plantilla Excel**
```bash
GET /api/plantilla-excel
Headers:
  X-User-Celular: 3007471199
```

**Respuesta:** Archivo Excel descargable

---

### 6. **Importar datos masivos desde Excel**
```bash
POST /api/importar-excel
Headers:
  X-User-Celular: 3007471199
Content-Type: multipart/form-data

Form Data:
  file: [archivo.xlsx]
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Importación completada",
  "insertados": 45,
  "errores": 2,
  "detalle_errores": [
    "Fila 10: Número de documento duplicado",
    "Fila 25: Placa inválida"
  ]
}
```

---

### 7. **Crear reporte individual**
```bash
POST /api/personas
Headers:
  X-User-Celular: 3007471199
Content-Type: application/json

{
  "numero_documento": "1234567890",
  "nombres": "JUAN",
  "apellidos": "PEREZ GOMEZ",
  "placa": "ABC123",
  "valor_reporte": 50000,
  "descripcion": "REPORTE NEGATIVO POR TARIFAS",
  "vehiculo_afiliado": "ADMICARS",
  "estado": "ACTIVA"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Reporte creado exitosamente",
  "id": 367
}
```

---

### 8. **Editar reporte**
```bash
PUT /api/personas/367
Headers:
  X-User-Celular: 3007471199
Content-Type: application/json

{
  "valor_reporte": 75000,
  "descripcion": "REPORTE ACTUALIZADO - TARIFAS Y DAÑO EN VH",
  "estado": "ACUERDO DE PAGO"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Reporte actualizado exitosamente"
}
```

---

## 🔒 Seguridad y Permisos

### Autenticación
Todos los endpoints (excepto `/verificar-usuario` y `/usuarios`) requieren el header:
```
X-User-Celular: 3007471199
```

### Permisos de edición
- **Usuario normal:** Solo puede editar reportes que él mismo creó
- **Usuario admin:** Puede editar cualquier reporte

---

## ⚠️ Códigos de Error

| Código | Significado |
|--------|-------------|
| 200 | Éxito |
| 201 | Creado |
| 400 | Solicitud incorrecta |
| 401 | No autorizado (falta header) |
| 403 | Prohibido (usuario no activo o sin permisos) |
| 404 | No encontrado |
| 409 | Conflicto (duplicado) |
| 500 | Error del servidor |

---

## 📊 Formato Excel para Importación

La plantilla debe contener estas columnas:

| Columna | Tipo | Requerido | Ejemplo |
|---------|------|-----------|---------|
| Fecha_Reporte | Fecha | No | 2024-01-15 |
| Numero_Documento | Texto | **Sí** | 1234567890 |
| Nombres | Texto | **Sí** | JUAN |
| Apellidos | Texto | **Sí** | PEREZ GOMEZ |
| Fecha_cierre | Texto | No | 2024-12-31 |
| Placa | Texto | **Sí** | ABC123 |
| Valor_Reporte | Número | No | 50000 |
| Descripcion_Reporte | Texto | No | REPORTE NEGATIVO |
| Vehiculo_afiliado | Texto | No | ADMICARS |
| Estado | Texto | No | ACTIVA |

---

## 🧪 Pruebas con cURL

### Verificar usuario
```bash
curl -X POST http://localhost:5000/api/verificar-usuario \
  -H "Content-Type: application/json" \
  -d '{"celular":"3007471199"}'
```

### Consultar persona
```bash
curl -X GET http://localhost:5000/api/personas/8497643 \
  -H "X-User-Celular: 3007471199"
```

### Crear reporte
```bash
curl -X POST http://localhost:5000/api/personas \
  -H "X-User-Celular: 3007471199" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_documento": "1234567890",
    "nombres": "JUAN",
    "apellidos": "PEREZ",
    "placa": "ABC123",
    "valor_reporte": 50000
  }'
```

---

## 🐛 Solución de Problemas

### Error de conexión a BD
```python
# Verificar credenciales en app.py
DB_CONFIG = {
    'host': 'localhost',
    'database': 'u990140860_infotaxi',
    'user': 'root',
    'password': 'TU_PASSWORD'
}
```

### Puerto 5000 ocupado
```python
# Cambiar puerto en app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

### CORS bloqueado
```python
# Ya está configurado en el código con flask-cors
# Si persiste, verificar que el origen esté permitido
```

---

## 📝 Notas Importantes

1. **Contraseñas:** Actualmente usa SHA1 (compatible con tu BD). Se recomienda migrar a bcrypt.
2. **Usuario que sube:** Se registra automáticamente en `Reportante_Nombres` usando el `id_user`.
3. **Consultas:** Se registran en la tabla `consultas` cada vez que se busca una persona.
4. **Excel:** Los errores en filas individuales no detienen la importación completa.

---

## 🔄 Próximas Mejoras Recomendadas

- [ ] Implementar JWT para autenticación más robusta
- [ ] Migrar contraseñas a bcrypt
- [ ] Agregar paginación a consultas
- [ ] Implementar búsqueda por placa
- [ ] Agregar logs de auditoría
- [ ] Implementar rate limiting
- [ ] Agregar endpoint para estadísticas

---

**Desarrollado para Sistema InfoTaxi** 🚕