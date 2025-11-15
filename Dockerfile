# Imagen ligera y estable
FROM python:3.11-slim

# Establecer directorio
WORKDIR /app

# Instalar dependencias del sistema necesarias para MySQL/MariaDB
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

############################################
# INTELIGENCIA PARA MANEJAR REQUIREMENTS
############################################

# Copia archivos si existen
COPY requirements.txt* /tmp/ 2>/dev/null || true
COPY requirements_txt.txt* /tmp/ 2>/dev/null || true

# Detectar cuál requirements existe y usarlo
RUN if [ -f /tmp/requirements.txt ]; then \
        cp /tmp/requirements.txt /app/requirements.txt; \
    elif [ -f /tmp/requirements_txt.txt ]; then \
        cp /tmp/requirements_txt.txt /app/requirements.txt; \
    else \
        echo "ERROR: No requirements file found!" && exit 1; \
    fi

# Instalar dependencias Python
RUN pip install --no-cache-dir -r /app/requirements.txt

############################################
# COPIAR APLICACIÓN
############################################
COPY . .

# Exponer puerto
EXPOSE 5000

# Comando de ejecución
CMD ["python", "infotaxi_api.py"]
