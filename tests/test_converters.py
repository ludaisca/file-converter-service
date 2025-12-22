import unittest
from unittest.mock import MagicMock, patch
from src.converters.factory import ConverterFactory
from src.converters.libreoffice import LibreOfficeConverter
from src.converters.imagemagick import ImageMagickConverter
from src.converters.ffmpeg import FFmpegConverter

class TestConverters(unittest.TestCase):
    def setUp(self):
        self.factory = ConverterFactory()

    def test_factory_get_converter(self):
        # LibreOffice
        self.assertIsInstance(self.factory.get_converter('.docx', '.pdf'), LibreOfficeConverter)
        # ImageMagick
        self.assertIsInstance(self.factory.get_converter('.jpg', '.png'), ImageMagickConverter)
        # FFmpeg
        self.assertIsInstance(self.factory.get_converter('.mp4', '.gif'), FFmpegConverter)
        self.assertIsInstance(self.factory.get_converter('.mp3', '.wav'), FFmpegConverter)
        # None
        self.assertIsNone(self.factory.get_converter('.xyz', '.abc'))

    @patch('subprocess.run')
    def test_libreoffice_convert(self, mock_run):
        converter = LibreOfficeConverter()
        mock_run.return_value = MagicMock(returncode=0)

        result = converter.convert('input.docx', 'output.pdf', '.docx', '.pdf')
        self.assertTrue(result['success'])
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_imagemagick_convert(self, mock_run):
        converter = ImageMagickConverter()
        mock_run.return_value = MagicMock(returncode=0)

        result = converter.convert('input.jpg', 'output.png', '.jpg', '.png')
        self.assertTrue(result['success'])
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_ffmpeg_convert(self, mock_run):
        converter = FFmpegConverter()
        mock_run.return_value = MagicMock(returncode=0)

        result = converter.convert('input.mp4', 'output.gif', '.mp4', '.gif')
        self.assertTrue(result['success'])
        mock_run.assert_called_once()

if __name__ == '__main__':
    unittest.main()
