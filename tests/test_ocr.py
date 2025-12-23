"""
Tests para OCR (src/ocr.py).
"""
import pytest
from unittest.mock import MagicMock, patch, mock_open
from src.ocr import OCRProcessor

class TestOCRProcessor:

    def setup_method(self):
        self.processor = OCRProcessor(default_lang='spa')

    @patch('src.ocr.pytesseract.get_languages')
    def test_get_available_languages(self, mock_get_languages):
        """Probar obtención de idiomas disponibles."""
        mock_get_languages.return_value = ['spa', 'eng']
        langs = self.processor.get_available_languages()
        assert 'spa' in langs
        assert 'eng' in langs

    @patch('src.ocr.pytesseract.get_languages')
    def test_is_language_available(self, mock_get_languages):
        """Probar verificación de idioma."""
        mock_get_languages.return_value = ['spa', 'eng']
        assert self.processor.is_language_available('spa') is True
        assert self.processor.is_language_available('deu') is False

    @patch('src.ocr.Image.open')
    @patch('src.ocr.pytesseract.image_to_string')
    @patch('src.ocr.pytesseract.image_to_data')
    def test_extract_text_from_image_success(self, mock_data, mock_string, mock_open_img):
        """Probar extracción exitosa de texto de imagen."""
        mock_string.return_value = "Texto de prueba"
        mock_data.return_value = {'conf': [90, 95, -1]} # -1 suele ser ignorado

        # Crear un mock más completo que se comporte como PIL.Image
        mock_image = MagicMock()
        mock_image.mode = 'RGB'
        # Esto es importante si el código trata de iterar sobre la imagen o algo similar
        mock_open_img.return_value = mock_image

        # Asegurarse de que preprocess_image no falle si se llama
        with patch.object(self.processor, 'preprocess_image', return_value=mock_image):
            result = self.processor.extract_text_from_image('path/to/image.jpg')

            # Si falla, imprimir el error para depurar
            if not result['success']:
                print(f"Error: {result.get('error')}")

            assert result['success'] is True
            assert result['text'] == "Texto de prueba"
            assert result['confidence'] > 0
            assert result['language'] == 'spa'

    @patch('src.ocr.Image.open')
    def test_extract_text_from_image_failure(self, mock_open_img):
        """Probar fallo en extracción de imagen."""
        mock_open_img.side_effect = Exception("File not found")

        result = self.processor.extract_text_from_image('invalid.jpg')

        assert result['success'] is False
        assert "File not found" in result['error']

    @patch('src.ocr.convert_from_path')
    @patch('src.ocr.OCRProcessor.extract_text_from_image')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_extract_text_from_pdf_success(self, mock_unlink, mock_temp, mock_extract_img, mock_convert):
        """Probar extracción exitosa de texto de PDF."""
        # Mock pages
        mock_page = MagicMock()
        mock_convert.return_value = [mock_page, mock_page]

        # Mock temp file
        mock_temp_obj = MagicMock()
        mock_temp_obj.name = '/tmp/temp.png'
        mock_temp.return_value.__enter__.return_value = mock_temp_obj

        # Mock image extraction
        mock_extract_img.return_value = {
            'success': True,
            'text': "Page text",
            'confidence': 90
        }

        result = self.processor.extract_text_from_pdf('doc.pdf')

        assert result['success'] is True
        assert result['total_pages'] == 2
        assert "Page text" in result['full_text']
        assert result['avg_confidence'] == 90

    @patch('src.ocr.convert_from_path')
    def test_extract_text_from_pdf_failure(self, mock_convert):
        """Probar fallo en extracción de PDF."""
        mock_convert.side_effect = Exception("PDF Error")

        result = self.processor.extract_text_from_pdf('doc.pdf')

        assert result['success'] is False
        assert "PDF Error" in result['error']
