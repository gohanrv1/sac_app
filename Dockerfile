# Imagen ligera
FROM python:3.11-slim

# Directorio
WORKDIR /app

# Dependencias del sistema para MySQL/MariaDB
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar requirements REAL
COPY requirements.txt /app/requirements.txt

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto completo
COPY . .

# Exponer el puerto
EXPOSE 5000

# Ejecutar API
CMD ["python", "infotaxi_api.py"]
