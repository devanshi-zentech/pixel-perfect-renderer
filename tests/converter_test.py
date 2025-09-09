

import unittest
from unittest.mock import patch, mock_open
import os
import sys
import json
import re

# Mock the jinja2 template environment and the os.path.dirname function
# This prevents errors from trying to load a template file that doesn't exist
# in the test environment.
from unittest.mock import MagicMock

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'services')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'core')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

# Import the DocumentConverter and helper functions
from app.services.document_converter import DocumentConverter
from app.services.html_rendering_helpers import render_word, render_table_with_words

# Mock the external dependencies
with patch('document_converter.os.path.dirname', MagicMock(return_value='/app/services')):
    with patch('document_converter.FileSystemLoader', MagicMock()):
        with patch('document_converter.Environment', MagicMock()):
            # Mock the template and its render method to return a controlled string
            mock_template = MagicMock()
            mock_template.render.return_value = "<html><head>{{ html_css }}</head><body>{{ page_container }}</body></html>"

# Mock `app.models.schemas` which is not provided, and `app.core.constants`
class MockRenderOptions:
    def __init__(self, font_stack=None):
        self.font_stack = font_stack


class MockConstants:
    DEFAULT_FONT_STACK = "Arial, sans-serif"
    DEFAULT_PAGE_WIDTH = 8.5
    DEFAULT_PAGE_HEIGHT = 11.0
    DEFAULT_PAGE_WIDTH_PIXEL = 1056
    DEFAULT_PAGE_HEIGHT_PIXEL = 816
    DEFAULT_PAGE_ANGLE = 0
    HTML_VISUALIZATION_CSS = "<style>{font_style}</style>"
    CONTAINER_STYLE = "<div class='page-container' style='width: {page_width_scaled}px; height: {page_height_scaled}px; transform: rotate({page_angle}deg);'>{content}</div>"
    RENDER_WORD_STYLE = "left: {left:.2f}px; top: {top:.2f}px; height: {word_height:.2f}px; font-size: {font_size:.2f}px; transform: rotate({angle_deg:.2f}deg);"
    RENDER_TABLE_STYLE = "<div class='table-container' style='position: absolute; left: {left:.2f}px; top: {top:.2f}px; width: {width:.2f}px;'><table>"
    CELL_STYLE = "position: relative; width: {cell_width_px:.2f}px; height: {cell_height_px:.2f}px; padding: 4px; box-sizing: border-box;"
    EMPTY_CELL_STYLE = "position: relative; min-width: {cell_width_px:.2f}px; min-height: {cell_height_px:.2f}px; padding: 4px; box-sizing: border-box;"
    CELL_HTML = "<div>{in_flow_text}</div>"
    RENDER_TABLE_WORD_STYLE = "position: absolute; left: {w_left_position_in_pixels:.2f}px; top: {w_top_position_in_pixels:.2f}px; transform: rotate({angle:.2f}deg); font-size: {font_size_in_pixels:.2f}px; height: {word_height_in_pixels:.2f}px;"


with patch('document_converter.constants', new=MockConstants):
    with patch('html_rendering_helpers.constants', new=MockConstants):
        from app.services.document_converter import DocumentConverter


class TestDocumentConverter(unittest.TestCase):
    """
    Test suite for the DocumentConverter class and its helper functions.
    """

    def setUp(self):
        """
        Set up common objects for tests.
        """
        self.converter = DocumentConverter()
        self.options = MockRenderOptions(font_stack="Arial, sans-serif;")

    def test_to_html_pages_simple_document(self):
        """
        Tests conversion of a simple document with a single page and words.
        """
        mock_data = {
            "pages": [{
                "pageNumber": 1,
                "width": 8.5,
                "height": 11.0,
                "unit": "inch",
                "words": [
                    {"content": "Hello", "polygon": [1, 1, 2, 1, 2, 2, 1, 2], "span": {"offset": 0, "length": 5},
                     "confidence": 0.9},
                    {"content": "World", "polygon": [3, 3, 4, 3, 4, 4, 3, 4], "span": {"offset": 6, "length": 5},
                     "confidence": 0.9}
                ]
            }],
            "tables": []
        }

        html_pages = self.converter.to_html_pages(mock_data, self.options)
        self.assertEqual(len(html_pages), 1)
        html = html_pages[0]

        # Check for word content and basic positioning
        self.assertIn("Hello", html)
        self.assertIn("World", html)
        self.assertIn("left: 129.41px; top: 129.41px;", html)  # 1 * 128.41
        self.assertIn("left: 388.24px; top: 388.24px;", html)  # 3 * 128.41

    def test_to_html_pages_with_table(self):
        """
        Tests that tables and their words are rendered correctly.
        Also verifies that words in a table are not rendered twice.
        """
        mock_data = {
            "pages": [{
                "pageNumber": 1,
                "width": 8.5,
                "height": 11.0,
                "unit": "inch",
                "words": [
                    # Words for the table
                    {"content": "Header", "polygon": [1, 1, 2, 1, 2, 2, 1, 2], "span": {"offset": 0, "length": 6},
                     "confidence": 0.9},
                    {"content": "Cell1", "polygon": [3, 3, 4, 3, 4, 4, 3, 4], "span": {"offset": 7, "length": 5},
                     "confidence": 0.9},
                    # Standalone word
                    {"content": "Standalone", "polygon": [5, 5, 6, 5, 6, 6, 5, 6], "span": {"offset": 13, "length": 10},
                     "confidence": 0.9}
                ],
            }],
            "tables": [{
                "boundingRegions": [{"pageNumber": 1, "polygon": [0.5, 0.5, 4.5, 0.5, 4.5, 4.5, 0.5, 4.5]}],
                "cells": [
                    {"rowIndex": 0, "columnIndex": 0, "content": "Header", "spans": [{"offset": 0, "length": 6}],
                     "kind": "columnHeader"},
                    {"rowIndex": 1, "columnIndex": 0, "content": "Cell1", "spans": [{"offset": 7, "length": 5}]}
                ],
                "rowCount": 2,
                "columnCount": 1
            }]
        }

        html_pages = self.converter.to_html_pages(mock_data, self.options)
        self.assertEqual(len(html_pages), 1)
        html = html_pages[0]

        # Check for table container and cell content
        self.assertIn("table-container", html)
        self.assertIn("Header", html)
        self.assertIn("Cell1", html)

        # Check for standalone word
        self.assertIn("Standalone", html)

        # Ensure no duplicate rendering of table words
        self.assertEqual(len(re.findall(r'Header', html)), 1)
        self.assertEqual(len(re.findall(r'Cell1', html)), 1)
        self.assertEqual(len(re.findall(r'Standalone', html)), 1)

    def test_to_html_pages_multiple_pages(self):
        """
        Tests that the method correctly processes a multi-page document.
        """
        mock_data = {
            "pages": [
                {"pageNumber": 1, "width": 8.5, "height": 11.0, "unit": "inch",
                 "words": [{"content": "Page One", "span": {"offset": 0, "length": 8}}]},
                {"pageNumber": 2, "width": 8.5, "height": 11.0, "unit": "inch",
                 "words": [{"content": "Page Two", "span": {"offset": 9, "length": 8}}]}
            ],
            "tables": []
        }

        html_pages = self.converter.to_html_pages(mock_data, self.options)
        print(html_pages)
        self.assertEqual(len(html_pages), 2)
        self.assertIn("Page 1", html_pages[0])
        self.assertIn("Page 2", html_pages[1])

    def test_to_html_pages_pixel_unit(self):
        """
        Tests handling of 'pixel' units where no scaling should occur.
        """
        mock_data = {
            "pages": [{
                "pageNumber": 1,
                "width": 1000,
                "height": 1500,
                "unit": "pixel",
                "words": [{"content": "Pixel World", "polygon": [100, 200, 200, 200, 200, 250, 100, 250],
                           "span": {"offset": 0, "length": 11}, "confidence": 0.9}]
            }],
            "tables": []
        }

        html_pages = self.converter.to_html_pages(mock_data, self.options)
        self.assertEqual(len(html_pages), 1)
        html = html_pages[0]

        # Check for pixel dimensions without scaling
        self.assertIn("width:1000.00px; height:1500.00px;", html)
        self.assertIn("left: 100.00px; top: 200.00px;", html)

    def test_to_html_pages_empty_document(self):
        """
        Tests that an empty document returns an empty list.
        """
        mock_data = {"pages": [], "tables": []}
        html_pages = self.converter.to_html_pages(mock_data, self.options)
        self.assertEqual(html_pages, [])

    def test_to_html_pages_missing_pages_key(self):
        """
        Tests that a document with a missing 'pages' key returns an empty list.
        """
        mock_data = {}
        html_pages = self.converter.to_html_pages(mock_data, self.options)
        self.assertEqual(html_pages, [])

    def test_render_word_low_confidence(self):
        """
        Tests that words with confidence below the threshold are not rendered.
        """
        word_data = {"content": "Test", "polygon": [1, 1, 2, 1, 2, 2, 1, 2], "confidence": 0.3}
        result = render_word(word_data, 1.0, "inch")
        self.assertEqual(result, "")

    def test_render_word_high_font_size_watermark(self):
        """
        Tests that words with an extremely large font size (potential watermark) are filtered.
        """
        # Create a word with a large height to trigger the watermark filter
        word_data = {"content": "Watermark", "polygon": [1, 1, 400, 1, 200, 200, 1, 400], "confidence": 0.9}
        result = render_word(word_data, 1.0, "inch")
        self.assertEqual(result, "")

    def test_render_table_with_words_rotated_words(self):
        """
        Tests rendering a table with vertically oriented words.
        """
        mock_table_data = {
            "boundingRegions": [{"pageNumber": 1, "polygon": [1, 1, 2, 1, 2, 5, 1, 5]}],
            "cells": [
                {"rowIndex": 0, "columnIndex": 0, "spans": [{"offset": 0, "length": 4}], "kind": "columnHeader"}
            ],
            "rowCount": 1,
            "columnCount": 1
        }
        mock_word_map = {
            0: {"content": "Test", "polygon": [1, 1, 1, 1.1, 1.1, 1.1, 1.1, 1], "span": {"offset": 0, "length": 4},
                "confidence": 0.9}
        }
        rendered_spans = set()
        scaling_factor = 100
        unit = "inch"

        html = render_table_with_words(mock_table_data, 1, scaling_factor, mock_word_map, rendered_spans, unit)
        print("HTML:", html)
        self.assertIn("position: relative;", html)
        self.assertIn("position: absolute;", html)
        self.assertIn("transform: rotate(", html)

    def test_with_user_provided_document(self):
        """
        Tests with a user-provided JSON document from a file.
        NOTE: You must place your JSON file named 'user_document.json' in the same directory as this test file.
        """
        file_path = os.path.join(os.path.dirname(__file__), 'test_json','user_document.json')
        if not os.path.exists(file_path):
            self.skipTest(f"Skipping test_with_user_provided_document because '{file_path}' was not found.")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)

            html_pages = self.converter.to_html_pages(user_data, self.options)

            # --- Add your custom assertions here based on the content of your JSON file. ---
            #
            # Example:
            # self.assertEqual(len(html_pages), 1, "The document should have one page.")
            # self.assertIn("Invoice", html_pages[0], "The word 'Invoice' should be in the output HTML.")
            # self.assertIn("Total Due", html_pages[0], "The phrase 'Total Due' should be in the output HTML.")
            #
            # You can also check for table-specific content, for example:
            # self.assertIn("<div class='table-container'", html_pages[0])
            #
            # If your document has multiple pages, you can check each one:
            # self.assertIn("Page Two Content", html_pages[1])

            # For a basic check, we can just assert that pages were generated.
            self.assertGreater(len(html_pages), 0, "No HTML pages were generated from the user's document.")

        except json.JSONDecodeError as e:
            self.fail(f"Could not parse the JSON file: {e}")
        except Exception as e:
            self.fail(f"An unexpected error occurred: {e}")

    def test_generated_document_matches_expected_output(self):
        """
        Tests that the generated HTML from a JSON document exactly matches a pre-saved HTML file.
        NOTE: You must place your JSON file named 'user_document.json' AND a corresponding 'expected_output.html' in the same directory.
        """
        json_path = os.path.join(os.path.dirname(__file__), 'test_json', 'user_document.json')
        html_path = os.path.join(os.path.dirname(__file__), 'expected_html', 'test.html')
        generated_html_path = os.path.join(os.path.dirname(__file__), 'generated_html', 'generated_test.html')

        # Skip the test if either the JSON or the expected HTML file doesn't exist
        if not os.path.exists(json_path):
            self.skipTest(f"Skipping because '{json_path}' was not found.")
        if not os.path.exists(html_path):
            self.skipTest(f"Skipping because '{html_path}' was not found.")

        try:
            # Load the user's JSON document
            with open(json_path, 'r', encoding='utf-8') as f:
                user_data = json.load(f)

            # Generate the HTML
            generated_html = self.converter.to_html_pages(user_data, self.options)

            # Ensure generated_html is a string (if it's a list, join it)
            if isinstance(generated_html, list):
                generated_html = "".join(generated_html)

            # Pretty-print the generated HTML using BeautifulSoup
            generated_html_pretty = BeautifulSoup(generated_html, 'html.parser').prettify()

            # Save the generated HTML into a file
            os.makedirs(os.path.dirname(generated_html_path), exist_ok=True)  # Create folder if it doesn't exist
            with open(generated_html_path, 'w', encoding='utf-8') as f:
                f.write(generated_html_pretty)

            # Load the expected HTML
            with open(html_path, 'r', encoding='utf-8') as f:
                expected_html = f.read()

            # Pretty-print the expected HTML using BeautifulSoup
            expected_html_pretty = BeautifulSoup(expected_html, 'html.parser').prettify()

            # For a fair comparison, normalize whitespace and line breaks
            generated_html_normalized = generated_html_pretty.strip().replace('\n', '')
            expected_html_normalized = expected_html_pretty.strip().replace('\n', '')

            print("Generated HTML saved to:", generated_html_path)
            print("Generated HTML (Normalized):", generated_html_normalized[:200])  # Print first 200 chars for review

            # Assert that the generated output matches the expected output
            self.assertEqual(generated_html_normalized, expected_html_normalized,
                             f"Generated HTML does not match the content of the expected_output.html file. See generated file at: {generated_html_path}")

        except json.JSONDecodeError as e:
            self.fail(f"Could not parse the JSON file: {e}")
        except Exception as e:
            self.fail(f"An unexpected error occurred: {e}")
if __name__ == '__main__':
    unittest.main()