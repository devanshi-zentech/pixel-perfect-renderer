import unittest
from pathlib import Path
from unittest.mock import patch
import pypdf
import asyncio
from io import BytesIO
from pypdf import PdfReader
from app.core.browser_manager import browser_manager
from app.services.html_to_pdf_converter import HtmlToPdfConverter

class TestHtmlToPdfConverter(unittest.TestCase):
    """
    Test suite for the HtmlToPdfConverter class.
    """

    @classmethod
    def tearDownClass(cls):
        """
        Closes the browser instance after all tests in this class have run.
        """
        asyncio.run(browser_manager.stop())

    def setUp(self):
        """
        Set up a temporary HTML file and an output PDF path for testing.
        """
        # Stop any existing browser instance to ensure a clean state for each test.
        # This prevents issues with closed event loops from previous test runs.
        asyncio.run(browser_manager.stop())

        test_dir = Path(__file__).parent
        self.output_pdf_path = test_dir / "test_pdf_output" / "test_output.pdf"
        self.expected_pdf_path = test_dir / "expected_pdf_output" / "table_html.pdf"
        self.html_pages = [
            {
                "html": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page 1</title>
    <style> body { font-family: Arial, sans-serif; } </style>
</head>
<body>
    <h1>Test Content</h1>
    <div>Nome da Aluna: Maria Eduarda Fonseca</div>
    <div>8,5</div>
</body>
</html>""",
                "width": 1100.0,
                "height": 1486.25
            }
        ]

    def get_pdf_text(self, pdf_bytes: bytes) -> str:
        """Helper to extract text from PDF bytes."""
        reader = pypdf.PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    def test_convert_html_to_pdf(self):
        """
        Tests the basic conversion from HTML content to a PDF file.
        """
        async def run_test():
            converter = HtmlToPdfConverter(self.html_pages)
            pdf_bytes = await converter.convert_to_pdf()
            actual_text = self.get_pdf_text(pdf_bytes)
            self.assertIn("Nome da Aluna: Maria Eduarda Fonseca", actual_text)
            self.assertIn("8,5", actual_text)

        asyncio.run(run_test())

    def test_skips_blank_pages(self):
        """
        Tests that blank pages are correctly identified and skipped.
        """
        html_with_blank_pages = [
            {"html": "<html><body><h1>Page 1</h1></body></html>", "width": 800, "height": 600},
            {"html": "<html><body></body></html>", "width": 800, "height": 600},  # Blank page
            {"html": "<html><body><h1>Page 3</h1></body></html>", "width": 800, "height": 600},
        ]

        async def run_test():
            converter = HtmlToPdfConverter(html_with_blank_pages)
            pdf_bytes = await converter.convert_to_pdf()
            reader = PdfReader(BytesIO(pdf_bytes))
            self.assertEqual(len(reader.pages), 2)
            page1_text = reader.pages[0].extract_text()
            page2_text = reader.pages[1].extract_text()
            self.assertIn("Page 1", page1_text)
            self.assertIn("Page 3", page2_text)

        asyncio.run(run_test())

    def test_converts_multiple_pages(self):
        """
        Tests that multiple HTML pages are correctly converted and merged into a single PDF.
        """
        multiple_html_pages = [
            {"html": "<html><body><h1>First Page</h1></body></html>", "width": 800, "height": 600},
            {"html": "<html><body><h1>Second Page</h1></body></html>", "width": 800, "height": 600},
        ]

        async def run_test():
            converter = HtmlToPdfConverter(multiple_html_pages)
            pdf_bytes = await converter.convert_to_pdf()
            reader = PdfReader(BytesIO(pdf_bytes))
            self.assertEqual(len(reader.pages), 2)
            full_text = self.get_pdf_text(pdf_bytes)
            self.assertIn("First Page", full_text)
            self.assertIn("Second Page", full_text)

        asyncio.run(run_test())

    @patch('app.core.browser_manager.browser_manager.get_browser', side_effect=Exception("Test Error"))
    def test_convert_exception_handling(self, mock_get_browser):
        """
        Tests that exceptions during PDF conversion are handled correctly.
        """
        async def run_test():
            with self.assertRaises(RuntimeError) as context:
                await HtmlToPdfConverter(self.html_pages).convert_to_pdf()
            self.assertIn("Error during conversion:", str(context.exception))

        asyncio.run(run_test())