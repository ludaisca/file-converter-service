FROM python:3.11-slim

# Instalar dependencias del sistema para conversión de archivos
RUN apt-get update && apt-get install -y \
    # Conversion tools
    libreoffice \
    imagemagick \
    ffmpeg \
    pandoc \
    ghostscript \
    poppler-utils \
    # OCR dependencies
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    # File type detection
    libmagic1 \
    file \
    # Essential tools for health checks and debugging
    curl \
    wget \
    netcat-openbsd \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick policy to allow PDF read/write
RUN if [ -f /etc/ImageMagick-6/policy.xml ]; then \
    sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/g' /etc/ImageMagick-6/policy.xml; \
    fi

# Configurar directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios para archivos
RUN mkdir -p /app/uploads /app/converted /app/logs

# Exponer puerto
EXPOSE 5000

# Comando de inicio
CMD ["python", "app.py"]
