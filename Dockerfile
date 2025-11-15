# Imagen ligera con Python 3.11
FROM python:3.11-slim

# Metadatos
LABEL maintainer="InfoTaxi API"
LABEL description="API REST para Sistema InfoTaxi"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=infotaxi_api.py \
    FLASK_ENV=production

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para MySQL/MariaDB
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt /app/requirements.txt

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copiar el proyecto completo
COPY . .

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer el puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Ejecutar API con Gunicorn (producción) o Python (desarrollo)
# Para producción: usar gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "infotaxi_api:app"]

# Para desarrollo, descomentar la siguiente línea y comentar la anterior:
# CMD ["python", "infotaxi_api.py"]
