# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema mínimas necesarias para el runtime y las herramientas de conversión
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Document Conversion
    libreoffice \
    libreoffice-calc \
    libreoffice-impress \
    libreoffice-writer \
    # Image Conversion & Processing
    imagemagick \
    graphicsmagick \
    # Video & Audio Conversion
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
    # Utilities
    curl \
    wget \
    procps \
    exiftool \
    mediainfo \
    # Antivirus
    clamav-daemon \
    clamav \
    # Redis tools (optional, useful for debugging)
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Configurar ImageMagick Policy
RUN if [ -f /etc/ImageMagick-6/policy.xml ]; then \
    sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/g' /etc/ImageMagick-6/policy.xml && \
    sed -i 's/rights="none" pattern="PS"/rights="read|write" pattern="PS"/g' /etc/ImageMagick-6/policy.xml && \
    sed -i 's/rights="none" pattern="EPS"/rights="read|write" pattern="EPS"/g' /etc/ImageMagick-6/policy.xml; \
    fi

# Create entrypoint script for ClamAV
RUN echo '#!/bin/sh\n\
mkdir -p /var/run/clamav\n\
chown clamav:clamav /var/run/clamav\n\
# Configure clamd to listen on TCP\n\
if ! grep -q "TCPSocket 3310" /etc/clamav/clamd.conf; then\n\
    echo "TCPSocket 3310" >> /etc/clamav/clamd.conf\n\
    echo "TCPAddr 127.0.0.1" >> /etc/clamav/clamd.conf\n\
fi\n\
# Start clamd in background (if enabled via env var, or just start it)\n\
# We use freshclam to update db if we had internet, but in offline env might fail. \n\
# Just starting daemon.\n\
service clamav-daemon start\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

# Crear usuario no privilegiado
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copiar paquetes instalados desde builder
COPY --from=builder /install /usr/local

# Copiar código de la aplicación
COPY . .

# Crear directorios y asignar permisos
# Only give write permissions to data directories
RUN mkdir -p /app/uploads /app/converted /app/logs /app/temp && \
    chown -R appuser:appuser /app/uploads /app/converted /app/logs /app/temp

# Cambiar al usuario no privilegiado
# NOTE: Need to verify if we switch to appuser, can we still access the code?
# Yes, because COPY . . copies as root (default), so appuser can read but not write.
USER appuser

# Exponer puerto
EXPOSE 5000

# Usar el entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
