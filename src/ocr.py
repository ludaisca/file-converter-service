"""
Módulo de OCR (Optical Character Recognition)
Extrae texto de imágenes y PDFs usando Tesseract
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
import logging
from pdf2image import convert_from_path
import tempfile


logger = logging.getLogger(__name__)


class OCRProcessor:
    """
    Procesador de OCR para extracción de texto de imágenes y PDFs
    """
    
    # Idiomas soportados por defecto
    SUPPORTED_LANGUAGES = {
        'spa': 'Español',
        'eng': 'English',
        'fra': 'Français',
        'deu': 'Deutsch',
        'ita': 'Italiano',
        'por': 'Português'
    }
    
    def __init__(self, default_lang='spa'):
        """
        Inicializa el procesador OCR
        
        Args:
            default_lang: Idioma por defecto ('spa', 'eng', etc.)
        """
        self.default_lang = default_lang
        
    def preprocess_image(self, image, deskew=True, enhance=True):
        """
        Preprocesa imagen para mejorar precisión de OCR
        
        Args:
            image: PIL Image object
            deskew: Corregir rotación
            enhance: Mejorar contraste y nitidez
            
        Returns:
            PIL Image: Imagen procesada
        """
        # Convertir a escala de grises
        if image.mode != 'L':
            image = image.convert('L')
        
        if enhance:
            # Mejorar contraste
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Mejorar nitidez
            image = image.filter(ImageFilter.SHARPEN)
        
        # TODO: Implementar deskew si es necesario
        # (requiere biblioteca adicional como deskew o scipy)
        
        return image
    
    def extract_text_from_image(self, image_path, lang=None, preprocess=True):
        """
        Extrae texto de una imagen
        
        Args:
            image_path: Ruta de la imagen
            lang: Código de idioma ('spa', 'eng', etc.). None usa default
            preprocess: Aplicar preprocesamiento
            
        Returns:
            dict: {
                'success': bool,
                'text': str,
                'confidence': float,
                'language': str,
                'error': str (si falla)
            }
        """
        try:
            # Cargar imagen
            image = Image.open(image_path)
            
            # Preprocesar si está habilitado
            if preprocess:
                image = self.preprocess_image(image)
            
            # Idioma a usar
            language = lang or self.default_lang
            
            # Extraer texto
            text = pytesseract.image_to_string(image, lang=language)
            
            # Obtener datos detallados (incluye confianza)
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            # Calcular confianza promedio
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'success': True,
                'text': text.strip(),
                'confidence': round(avg_confidence, 2),
                'language': language
            }
            
        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0,
                'language': lang or self.default_lang
            }
    
    def extract_text_from_pdf(self, pdf_path, lang=None, preprocess=True, max_pages=None):
        """
        Extrae texto de un PDF escaneado
        
        Args:
            pdf_path: Ruta del PDF
            lang: Código de idioma
            preprocess: Aplicar preprocesamiento
            max_pages: Máximo número de páginas a procesar (None = todas)
            
        Returns:
            dict: {
                'success': bool,
                'pages': list of dict (una entrada por página),
                'full_text': str (todo el texto concatenado),
                'total_pages': int,
                'avg_confidence': float
            }
        """
        try:
            # Convertir PDF a imágenes
            images = convert_from_path(pdf_path)
            
            # Limitar páginas si se especifica
            if max_pages:
                images = images[:max_pages]
            
            pages_data = []
            full_text = []
            total_confidence = 0
            
            # Procesar cada página
            for i, image in enumerate(images, 1):
                # Guardar imagen temporalmente
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    tmp_path = tmp.name
                    image.save(tmp_path, 'PNG')
                
                # Extraer texto
                result = self.extract_text_from_image(tmp_path, lang, preprocess)
                
                # Limpiar archivo temporal
                os.unlink(tmp_path)
                
                # Guardar resultado de la página
                page_result = {
                    'page': i,
                    'text': result['text'],
                    'confidence': result['confidence']
                }
                pages_data.append(page_result)
                full_text.append(result['text'])
                total_confidence += result['confidence']
            
            avg_confidence = total_confidence / len(images) if images else 0
            
            return {
                'success': True,
                'pages': pages_data,
                'full_text': '\n\n'.join(full_text),
                'total_pages': len(images),
                'avg_confidence': round(avg_confidence, 2),
                'language': lang or self.default_lang
            }
            
        except Exception as e:
            logger.error(f"PDF OCR failed for {pdf_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'pages': [],
                'full_text': '',
                'total_pages': 0,
                'avg_confidence': 0
            }
    
    def is_language_available(self, lang_code):
        """
        Verifica si un idioma está disponible en Tesseract
        
        Args:
            lang_code: Código del idioma ('spa', 'eng', etc.)
            
        Returns:
            bool: True si está disponible
        """
        try:
            available_langs = pytesseract.get_languages()
            return lang_code in available_langs
        except Exception:
            return False
    
    def get_available_languages(self):
        """
        Obtiene lista de idiomas disponibles en Tesseract
        
        Returns:
            list: Lista de códigos de idioma disponibles
        """
        try:
            return pytesseract.get_languages()
        except Exception as e:
            logger.error(f"Failed to get available languages: {str(e)}")
            return ['eng']  # Fallback a inglés
