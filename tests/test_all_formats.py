import unittest
from unittest.mock import MagicMock, patch
from src.converters.factory import ConverterFactory
from src.converters.libreoffice import LibreOfficeConverter
from src.converters.imagemagick import ImageMagickConverter
from src.converters.ffmpeg import FFmpegConverter
from src.converters.archive import ArchiveConverter

class TestAllFormats(unittest.TestCase):
    def setUp(self):
        self.factory = ConverterFactory()

    def test_factory_routing_documents(self):
        # LibreOffice should handle spreadsheets and presentations now
        self.assertIsInstance(self.factory.get_converter('.xlsx', '.pdf'), LibreOfficeConverter)
        self.assertIsInstance(self.factory.get_converter('.pptx', '.pdf'), LibreOfficeConverter)
        self.assertIsInstance(self.factory.get_converter('.html', '.pdf'), LibreOfficeConverter)
        self.assertIsInstance(self.factory.get_converter('.csv', '.xlsx'), LibreOfficeConverter)

    def test_factory_routing_archives(self):
        # ArchiveConverter routing
        self.assertIsInstance(self.factory.get_converter('.zip', '.tar.gz'), ArchiveConverter)
        self.assertIsInstance(self.factory.get_converter('.rar', '.zip'), ArchiveConverter)
        self.assertIsInstance(self.factory.get_converter('.7z', '.tar'), ArchiveConverter)

    def test_factory_routing_multimedia_extended(self):
        # FFmpeg extended
        self.assertIsInstance(self.factory.get_converter('.webm', '.mp4'), FFmpegConverter)
        self.assertIsInstance(self.factory.get_converter('.3gp', '.mp4'), FFmpegConverter)
        self.assertIsInstance(self.factory.get_converter('.mp4', '.mp3'), FFmpegConverter)

        # ImageMagick extended
        self.assertIsInstance(self.factory.get_converter('.heic', '.jpg'), ImageMagickConverter)
        self.assertIsInstance(self.factory.get_converter('.tiff', '.pdf'), ImageMagickConverter)

    @patch('src.converters.archive.ArchiveConverter.run_command')
    @patch('tempfile.TemporaryDirectory')
    def test_archive_conversion_flow(self, mock_temp_dir, mock_run):
        # Mock temp dir context manager
        mock_temp_dir.return_value.__enter__.return_value = '/tmp/test_dir'
        mock_run.return_value = {'success': True}

        converter = ArchiveConverter()
        result = converter.convert('input.zip', 'output.tar.gz', '.zip', '.tar.gz')

        self.assertTrue(result['success'])
        # Verify 7z extraction called
        self.assertTrue(any('7z' in str(call) and 'x' in str(call) for call in mock_run.call_args_list))
        # Verify tar compression called
        self.assertTrue(any('tar' in str(call) and '-czf' in str(call) for call in mock_run.call_args_list))

    @patch('src.converters.libreoffice.LibreOfficeConverter.run_command')
    @patch('os.path.exists')
    @patch('shutil.move')
    def test_libreoffice_spreadsheet(self, mock_move, mock_exists, mock_run):
        converter = LibreOfficeConverter()
        mock_run.return_value = {'success': True}
        # Simulate output file existing
        mock_exists.return_value = True

        result = converter.convert('input.xlsx', 'output.pdf', '.xlsx', '.pdf')

        self.assertTrue(result['success'])
        # Verify correct args passed to libreoffice
        args = mock_run.call_args[0][0]
        self.assertIn('--convert-to', args)
        self.assertIn('pdf', args)

if __name__ == '__main__':
    unittest.main()
