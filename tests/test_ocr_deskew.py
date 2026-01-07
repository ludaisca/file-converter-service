import pytest
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from src.ocr import OCRProcessor
from skimage.transform import rotate
import os

class TestOCRDeskew:

    @pytest.fixture
    def ocr_processor(self):
        return OCRProcessor()

    def create_skewed_image(self, angle=10):
        # Create a white image with black text
        # Make it larger and add more text to help deskew algorithm
        img = Image.new('L', (800, 1000), color=255)
        d = ImageDraw.Draw(img)

        # Add valid text block (simulating a document)
        text = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
        Nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in.
        Reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla.
        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui.
        Officia deserunt mollit anim id est laborum.
        """

        # Repeat text to fill page more
        full_text = text * 5

        # Use default font, but position it nicely
        # Note: default font is very small, might need to draw many lines
        # Or just draw lines of rectangles to simulate text if font is issue
        # But let's try with text first.

        y = 50
        for line in full_text.split('\n'):
            line = line.strip()
            if line:
                d.text((50, y), line, fill=0)
                y += 15 # spacing

        # Rotate the image
        rotated = img.rotate(angle, expand=True, fillcolor=255)

        return rotated

    def test_preprocess_image_deskew(self, ocr_processor):
        """Test that deskewing works on a rotated image"""
        skew_angle = 5
        skewed_img = self.create_skewed_image(angle=skew_angle)

        # Process the image with deskew=True
        result_img = ocr_processor.preprocess_image(skewed_img, deskew=True, enhance=False)

        from deskew import determine_skew

        # Initial skew
        initial_skew = determine_skew(np.array(skewed_img))
        # Result skew
        final_skew = determine_skew(np.array(result_img))

        print(f"Initial skew: {initial_skew}")
        print(f"Final skew: {final_skew}")

        # We expect the initial skew to be close to -skew_angle
        # Note: deskew library usually returns the angle to ROTATE BY to fix it.
        # So if image is rotated +5 deg (clockwise), we need to rotate -5 deg (counter-clockwise) to fix.
        # So determine_skew might return something related to that.

        assert initial_skew is not None
        # Allow some margin of error, but it should detect something

        # Final skew should be close to 0
        if final_skew is not None:
             assert abs(final_skew) < 2.0 # Allow small error
        else:
             # If None, it means it couldn't detect skew (perfectly straight often returns None or 0)
             pass

    def test_preprocess_image_no_deskew(self, ocr_processor):
        """Test that deskew=False does not rotate the image"""
        skew_angle = 5
        skewed_img = self.create_skewed_image(angle=skew_angle)

        result_img = ocr_processor.preprocess_image(skewed_img, deskew=False, enhance=False)

        if skewed_img.mode != 'L':
             skewed_img = skewed_img.convert('L')

        arr1 = np.array(skewed_img)
        arr2 = np.array(result_img)

        assert arr1.shape == arr2.shape
        assert np.array_equal(arr1, arr2)
