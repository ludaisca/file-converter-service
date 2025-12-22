FROM python:3.11-slim

# Instalar dependencias del sistema para conversión de archivos
RUN apt-get update && apt-get install -y \
    libreoffice \
    imagemagick \
    ffmpeg \
    pandoc \
    ghostscript \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios para archivos
RUN mkdir -p /app/uploads /app/converted

# Exponer puerto
EXPOSE 5000

# Comando de inicio
CMD ["python", "app.py"]
