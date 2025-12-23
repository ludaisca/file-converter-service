# Guía de Contribución

¡Gracias por tu interés en contribuir al Servicio de Conversión de Archivos! Esta guía te ayudará a empezar.

---

## Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Mejoras](#sugerir-mejoras)
- [Tu Primera Contribución](#tu-primera-contribución)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Guía de Estilo](#guía-de-estilo)
- [Configuración de Desarrollo](#configuración-de-desarrollo)
- [Ejecutar Tests](#ejecutar-tests)

---

## Código de Conducta

Este proyecto se adhiere a un código de conducta. Al participar, se espera que mantengas este código:

- **Sé respetuoso**: Trata a todos con respeto
- **Sé constructivo**: Ofrece críticas constructivas
- **Sé inclusivo**: Da la bienvenida a diferentes perspectivas
- **Sé profesional**: Mantén un ambiente profesional

---

## Cómo Contribuir

Hay muchas formas de contribuir:

- 🐛 **Reportar bugs**
- 💡 **Sugerir nuevas funcionalidades**
- 📝 **Mejorar documentación**
- 💻 **Enviar código**
- 🔍 **Revisar pull requests**
- 🌐 **Traducir documentación**
- ⭐ **Dar estrella al repo**

---

## Reportar Bugs

Antes de reportar un bug:

1. **Busca** en [issues existentes](https://github.com/thecocoblue/file-converter-service/issues)
2. **Verifica** que uses la última versión
3. **Lee** la [guía de troubleshooting](docs/TROUBLESHOOTING.md)

### Cómo Reportar

Crea un [nuevo issue](https://github.com/thecocoblue/file-converter-service/issues/new) con:

**Título**: Descripción breve y clara del problema

**Contenido**:
```markdown
## Descripción
Descripción clara y concisa del bug.

## Pasos para Reproducir
1. Ir a '...'
2. Hacer clic en '...'
3. Ejecutar '...'
4. Ver error

## Comportamiento Esperado
Qué esperabas que sucediera.

## Comportamiento Actual
Qué sucedió en realidad.

## Capturas de Pantalla
Si aplica, agrega capturas de pantalla.

## Entorno
- OS: [ej. Ubuntu 22.04]
- Docker Version: [ej. 24.0.5]
- Versión del Servicio: [ej. 1.0.0]

## Logs
```bash
# Pega los logs relevantes aquí
```

## Información Adicional
Cualquier otro contexto sobre el problema.
```

---

## Sugerir Mejoras

### Ideas de Funcionalidades

Crea un [nuevo issue](https://github.com/thecocoblue/file-converter-service/issues/new) con:

**Título**: `Feature: Descripción breve`

**Contenido**:
```markdown
## Problema a Resolver
¿Qué problema solucionaría esta funcionalidad?

## Solución Propuesta
Descripción de cómo funcionaría.

## Alternativas Consideradas
Otras soluciones que consideraste.

## Beneficios
- Beneficio 1
- Beneficio 2

## Casos de Uso
1. Caso de uso 1
2. Caso de uso 2

## Implementación Sugerida
(Opcional) Cómo podría implementarse.
```

### Prioridades Actuales

Estas funcionalidades son especialmente bienvenidas:

- ✅ Autenticación y autorización
- ✅ Rate limiting integrado
- ✅ Cola de procesamiento
- ✅ Webhooks para notificaciones
- ✅ Más formatos de conversión
- ✅ Parámetros de calidad configurables
- ✅ API para conversiones por lotes
- ✅ Interfaz web simple

---

## Tu Primera Contribución

¿Nuevo en contribuciones de código abierto?

Busca issues etiquetados con:
- `good first issue`: Buenos para principiantes
- `help wanted`: Necesitamos ayuda
- `documentation`: Mejoras de documentación

### Issues para Principiantes

1. **Mejorar documentación**
   - Corregir typos
   - Añadir ejemplos
   - Traducir a otros idiomas

2. **Añadir tests**
   - Tests unitarios
   - Tests de integración

3. **Pequeñas mejoras**
   - Mensajes de error más claros
   - Validaciones adicionales

---

## Proceso de Pull Request

### 1. Fork y Clonar

```bash
# Fork el repositorio en GitHub, luego:
git clone https://github.com/TU-USUARIO/file-converter-service.git
cd file-converter-service
git remote add upstream https://github.com/thecocoblue/file-converter-service.git
```

### 2. Crear una Rama

```bash
# Actualizar main
git checkout main
git pull upstream main

# Crear rama descriptiva
git checkout -b feature/nombre-descriptivo
# o
git checkout -b fix/descripcion-del-fix
```

**Nomenclatura de ramas**:
- `feature/` - Nueva funcionalidad
- `fix/` - Corrección de bug
- `docs/` - Cambios en documentación
- `refactor/` - Refactorización de código
- `test/` - Añadir o mejorar tests

### 3. Hacer Cambios

```bash
# Hacer tus cambios
nano src/routes.py

# Probar localmente
docker-compose up --build
curl http://localhost:5000/health

# Ejecutar tests (cuando existan)
python -m pytest
```

### 4. Commit

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat: agregar soporte para formato EPUB"
```

**Formato de commits**:
```
tipo(scope): descripción corta

[cuerpo opcional con más detalles]

[footer opcional]
```

**Tipos**:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formato, punto y coma faltantes, etc.
- `refactor`: Refactorización de código
- `perf`: Mejoras de rendimiento
- `test`: Añadir tests
- `chore`: Tareas de mantenimiento

**Ejemplos**:
```bash
git commit -m "feat: agregar soporte para conversión de HEIC a JPG"
git commit -m "fix: corregir timeout en descargas grandes"
git commit -m "docs: actualizar ejemplos de API en español"
git commit -m "refactor: simplificar lógica de validación de archivos"
```

### 5. Push y PR

```bash
# Push a tu fork
git push origin feature/nombre-descriptivo
```

Luego en GitHub:
1. Ve a tu fork
2. Click en "Compare & pull request"
3. Llena el template del PR:

```markdown
## Descripción
Descripción clara de los cambios.

## Tipo de Cambio
- [ ] Bug fix (cambio que corrige un issue)
- [ ] Nueva funcionalidad (cambio que agrega funcionalidad)
- [ ] Breaking change (fix o feature que causaría que funcionalidad existente no funcione como se esperaba)
- [ ] Cambio en documentación

## ¿Cómo se ha Probado?
Describe las pruebas que ejecutaste.

- [ ] Test A
- [ ] Test B

## Checklist
- [ ] Mi código sigue la guía de estilo del proyecto
- [ ] He realizado una auto-revisión de mi código
- [ ] He comentado mi código, especialmente en áreas difíciles
- [ ] He actualizado la documentación correspondiente
- [ ] Mis cambios no generan nuevos warnings
- [ ] He agregado tests que prueban que mi fix es efectivo o que mi funcionalidad funciona
- [ ] Tests unitarios nuevos y existentes pasan localmente
- [ ] He actualizado el CHANGELOG.md
```

### 6. Revisión

- Espera feedback del mantenedor
- Realiza cambios solicitados
- Push de nuevos commits a la misma rama

### 7. Merge

Una vez aprobado, el mantenedor hará merge de tu PR.

---

## Guía de Estilo

### Python

Seguimos [PEP 8](https://pep8.org/):

```python
# Bueno
def convert_file(input_path: str, output_path: str, format: str) -> dict:
    """Convert a file to the specified format.
    
    Args:
        input_path: Path to input file
        output_path: Path to output file
        format: Target format
        
    Returns:
        Dictionary with conversion result
    """
    result = perform_conversion(input_path, output_path, format)
    return result

# Malo
def convertFile(inputPath,outputPath,format):
    result=performConversion(inputPath,outputPath,format)
    return result
```

**Reglas**:
- Indentación: 4 espacios
- Líneas: Máximo 100 caracteres
- Nombres: `snake_case` para funciones y variables
- Clases: `PascalCase`
- Constantes: `UPPER_CASE`
- Docstrings: Google style

### Estructura de Archivos

```python
# 1. Imports estándar
import os
import sys
from pathlib import Path

# 2. Imports de terceros
from flask import Flask, request
import requests

# 3. Imports locales
from .config import Config
from .utils import sanitize_filename

# 4. Código
```

### Comentarios

```python
# Bueno: Explica el "por qué"
# Usamos UUID para evitar colisiones cuando múltiples usuarios
# suben archivos con el mismo nombre simultáneamente
file_id = uuid.uuid4().hex

# Malo: Explica el "qué" (obvio por el código)
# Generar un UUID
file_id = uuid.uuid4().hex
```

### Manejo de Errores

```python
# Bueno: Específico y con contexto
try:
    result = converter.convert(input_path, output_path)
except FileNotFoundError:
    logger.error(f"Input file not found: {input_path}")
    return {"error": "Input file not found"}, 404
except PermissionError:
    logger.error(f"Permission denied: {input_path}")
    return {"error": "Permission denied"}, 403

# Malo: Genérico
try:
    result = converter.convert(input_path, output_path)
except Exception as e:
    return {"error": str(e)}, 500
```

---

## Configuración de Desarrollo

### Requisitos

- Python 3.11+
- Docker y Docker Compose
- Git

### Setup Local

```bash
# Clonar
git clone https://github.com/TU-USUARIO/file-converter-service.git
cd file-converter-service

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Copiar .env
cp .env.example .env

# Ejecutar con Docker
docker-compose up --build
```

### Desarrollo sin Docker

```bash
# Instalar dependencias del sistema (Ubuntu/Debian)
sudo apt install libreoffice imagemagick ffmpeg pandoc

# Ejecutar servidor de desarrollo
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

---

## Ejecutar Tests

```bash
# Ejecutar todos los tests
python -m pytest

# Con coverage
python -m pytest --cov=src

# Tests específicos
python -m pytest tests/test_converters.py

# Verbose
python -m pytest -v
```

### Escribir Tests

```python
import pytest
from src.converters.imagemagick import ImageMagickConverter

def test_image_conversion():
    """Test basic image conversion."""
    converter = ImageMagickConverter()
    result = converter.convert(
        "test.jpg",
        "test.png",
        ".jpg",
        ".png"
    )
    assert result["success"] is True
    assert os.path.exists("test.png")
```

---

## Estructura del Proyecto

```
file-converter-service/
├── app.py                  # Punto de entrada
├── src/
│   ├── config.py           # Configuración
│   ├── routes.py           # Endpoints de API
│   ├── utils.py            # Utilidades
│   ├── logging.py          # Configuración de logs
│   └── converters/         # Conversores
│       ├── base.py         # Conversor base
│       ├── factory.py      # Factory pattern
│       ├── libreoffice.py  # Conversor de documentos
│       ├── imagemagick.py  # Conversor de imágenes
│       └── ffmpeg.py       # Conversor de audio/video
├── tests/                  # Tests
├── docs/                   # Documentación
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Recursos

- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de Docker](https://docs.docker.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [PEP 8 Style Guide](https://pep8.org/)

---

## Preguntas

¿Tienes preguntas? 

- Abre un [issue de discusión](https://github.com/thecocoblue/file-converter-service/issues)
- Envía un email a [luis.islas@ludaisca.com](mailto:luis.islas@ludaisca.com)

---

## Reconocimientos

Todos los contribuidores serán agregados al archivo `CONTRIBUTORS.md`.

¡Gracias por contribuir! 🎉
