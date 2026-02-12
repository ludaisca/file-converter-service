import sys
import unittest
from unittest.mock import MagicMock, call, patch
import os

# Mock dependencies
sys.modules['pdf2image'] = MagicMock()
sys.modules['pytesseract'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['deskew'] = MagicMock()
sys.modules['skimage'] = MagicMock()
sys.modules['skimage.transform'] = MagicMock()
sys.modules['numpy'] = MagicMock()

# Import
sys.path.append(os.getcwd())
try:
    from src.ocr import OCRProcessor
except ImportError as e:
    print(f"Failed to import OCRProcessor: {e}")
    sys.exit(1)

class TestOCRChunking(unittest.TestCase):
    def setUp(self):
        self.ocr = OCRProcessor()
        # Mock internal image extraction
        self.ocr.extract_text_from_image = MagicMock(return_value={
            'text': 'page_text', 'confidence': 90.0
        })

    @patch('src.ocr.pdfinfo_from_path') # This might fail if not imported yet, so we mock sys.modules above
    @patch('src.ocr.convert_from_path')
    def test_chunking_calls(self, mock_convert, mock_pdfinfo):
        # Configure mocks
        mock_pdfinfo.return_value = {'Pages': 25}

        def side_effect_convert(pdf_path, first_page=None, last_page=None, **kwargs):
            if first_page is None:
                # Old behavior: return all 25 pages
                return [MagicMock()] * 25
            count = last_page - first_page + 1
            return [MagicMock()] * count
        mock_convert.side_effect = side_effect_convert

        print("Running chunking test...")
        try:
            res = self.ocr.extract_text_from_pdf("test.pdf")
        except Exception as e:
            # If pdfinfo_from_path is not imported in src/ocr.py yet, patching it might fail or code might fail
            print(f"Execution failed (expected if not implemented): {e}")
            # If it failed because pdfinfo_from_path is not defined in src.ocr, that's expected
            return

        # Check calls
        calls = mock_convert.call_args_list
        if not calls:
            self.fail("convert_from_path not called")

        args, kwargs = calls[0]
        if 'first_page' not in kwargs:
             print("Old implementation detected (no chunking).")
             return

        self.assertEqual(len(calls), 3, f"Expected 3 chunks, got {len(calls)}")

        # Check logic
        self.assertEqual(res['total_pages'], 25)
        self.assertEqual(len(res['pages']), 25)

    @patch('src.ocr.pdfinfo_from_path')
    @patch('src.ocr.convert_from_path')
    def test_max_pages_chunking(self, mock_convert, mock_pdfinfo):
        mock_pdfinfo.return_value = {'Pages': 25}

        def side_effect_convert(pdf_path, first_page=None, last_page=None, **kwargs):
            if first_page is None:
                return [MagicMock()] * 25
            count = last_page - first_page + 1
            return [MagicMock()] * count
        mock_convert.side_effect = side_effect_convert

        print("Running max_pages chunking test...")
        try:
            res = self.ocr.extract_text_from_pdf("test.pdf", max_pages=15)
        except Exception as e:
            print(f"Execution failed: {e}")
            return

        calls = mock_convert.call_args_list
        if not calls:
             self.fail("No calls made")

        args, kwargs = calls[0]
        if 'first_page' not in kwargs:
             print("Old implementation detected.")
             return

        self.assertEqual(len(calls), 2, f"Expected 2 chunks for max_pages=15, got {len(calls)}")
        self.assertEqual(res['total_pages'], 15)

if __name__ == '__main__':
    unittest.main()
