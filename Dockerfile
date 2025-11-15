# Usar imagen base de Python ligera
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar archivo real de dependencias (corrigiendo nombre)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODOS los archivos del proyecto
COPY . .

# Exponer el puerto donde corre Flask
EXPOSE 5000

# Comando para ejecutar la aplicación en producción
CMD ["python", "infotaxi_api.py"]
