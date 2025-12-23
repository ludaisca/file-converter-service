import unittest
from unittest.mock import MagicMock, patch
from src.converters.factory import ConverterFactory
from src.converters.libreoffice import LibreOfficeConverter
from src.converters.imagemagick import ImageMagickConverter
from src.converters.ffmpeg import FFmpegConverter
from src.converters.archive import ArchiveConverter

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
        # Archive
        self.assertIsInstance(self.factory.get_converter('.zip', '.tar.gz'), ArchiveConverter)

        # None
        self.assertIsNone(self.factory.get_converter('.xyz', '.abc'))

    @patch('src.converters.libreoffice.LibreOfficeConverter.run_command')
    @patch('os.path.exists')
    @patch('shutil.move')
    def test_libreoffice_convert(self, mock_move, mock_exists, mock_run):
        converter = LibreOfficeConverter()
        mock_run.return_value = {'success': True}

        # Simulate that expected output exists but is different from output_path
        # so shutil.move is called.
        def side_effect(path):
            if path == '/app/converted/input.pdf':
                return True
            if path == 'output.pdf':
                return True # After move
            return False

        mock_exists.side_effect = side_effect

        result = converter.convert('input.docx', 'output.pdf', '.docx', '.pdf')
        self.assertTrue(result['success'])
        mock_run.assert_called_once()
        mock_move.assert_called_once()

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
