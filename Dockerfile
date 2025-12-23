FROM python:3.11-slim

# Instalar dependencias del sistema para conversión COMPLETA de archivos
# Soporte para: Documentos, Imágenes, Video, Audio, Archivos
RUN apt-get update && apt-get install -y \
    # Document Conversion
    libreoffice \
    libreoffice-calc \
    libreoffice-impress \
    libreoffice-writer \
    # Image Conversion & Processing
    imagemagick \
    graphicsmagick \
    # Video & Audio Conversion (ffmpeg con codecs completos)
    ffmpeg \
    libavcodec-extra \
    libavformat-extra \
    # Document Processing
    pandoc \
    ghostscript \
    poppler-utils \
    # Archive Support
    zip \
    unzip \
    p7zip-full \
    xz-utils \
    bzip2 \
    gzip \
    # Audio Processing
    sox \
    libsox-fmt-all \
    lame \
    libmp3lame0 \
    vorbis-tools \
    flac \
    opus-tools \
    # Video Processing
    mkvtoolnix \
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
    # Additional utilities
    exiftool \
    mediainfo \
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick policy to allow all image formats
RUN if [ -f /etc/ImageMagick-6/policy.xml ]; then \
    sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/g' /etc/ImageMagick-6/policy.xml && \
    sed -i 's/rights="none" pattern="PS"/rights="read|write" pattern="PS"/g' /etc/ImageMagick-6/policy.xml && \
    sed -i 's/rights="none" pattern="EPS"/rights="read|write" pattern="EPS"/g' /etc/ImageMagick-6/policy.xml; \
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

# Verificar instalación de herramientas
RUN echo "=== Herramientas Instaladas ===" && \
    ffmpeg -version | head -1 && \
    sox --version && \
    pandoc --version | head -1 && \
    lame --version | head -1 && \
    flac --version | head -1 && \
    oggenc --version | head -1 && \
    opusenc --version | head -1 && \
    7z i | head -3 && \
    zip -v | head -1 && \
    echo "=== Instalación Completada ==="

# Exponer puerto
EXPOSE 5000

# Comando de inicio
CMD ["python", "app.py"]
