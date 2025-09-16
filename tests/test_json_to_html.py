import unittest
from unittest.mock import patch
import os
import sys
import json

# Add the application source directories to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'services')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'core')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

# Mock necessary modules and constants before importing the converter
class MockConstants:
    DEFAULT_FONT_STACK = "Arial, sans-serif"
    HTML_VISUALIZATION_CSS = "<style>body {{ font-family: {font_style}; background: #f0f0f0; }} .page {{ margin: 20px auto; border: 1px solid #ccc; box-shadow: 0 0 10px rgba(0,0,0,0.1); position: relative; overflow: hidden; background: white; }} .table-container table {{ border-collapse: collapse; width: 100%; }} .table-container th, .table-container td {{ border: 1px solid black; padding: 4px; text-align: center; font-size: 10px; position: relative; overflow: hidden; }}</style>"
    CONTAINER_STYLE = '<div class="page" style="width:{page_width_scaled:.2f}px; height:{page_height_scaled:.2f}px; transform:rotate({page_angle}deg);">{content}</div>'
    RENDER_WORD_STYLE = "position: absolute; left: {left:.2f}px; top: {top:.2f}px; transform-origin: top left; transform: rotate({angle_deg:.2f}deg); font-size: {font_size:.2f}px; line-height: {word_height:.2f}px; white-space: nowrap; color: rgba(0,0,0,{confidence});"
    RENDER_TABLE_STYLE = '<div class="table-container" style="position: absolute; left: {left:.2f}px; top: {top:.2f}px; width: {width:.2f}px;"><table border="1">'
    CELL_STYLE = 'position: relative; width: {cell_width_px:.2f}px; height: {cell_height_px:.2f}px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;'
    EMPTY_CELL_STYLE = 'position: relative; min-width: {cell_width_px:.2f}px; min-height: {cell_height_px:.2f}px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;'
    CELL_HTML = '<div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">{in_flow_text}</div>'
    RENDER_TABLE_WORD_STYLE = "position: absolute; left: {w_left_position_in_pixels:.2f}px; top: {w_top_position_in_pixels:.2f}px; transform: rotate({angle:.2f}deg); font-size: {font_size_in_pixels:.2f}px; height: {word_height_in_pixels:.2f}px;"

class MockRenderOptions:
    def __init__(self, font_stack=None):
        self.font_stack = font_stack

# Apply patches to mock dependencies
with patch('app.services.document_converter.constants', new=MockConstants), \
     patch('app.services.html_rendering_helpers.constants', new=MockConstants), \
     patch('app.services.document_converter.template') as mock_template:
    
    # Configure the mock template's render method
    def render_mock_template(page_number, html_css, page_container):
        return f'<!DOCTYPE html> <html> <head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>Page {page_number}</title> <style> {html_css} </style> </head> <body> {page_container} </body> </html>'
    mock_template.render.side_effect = render_mock_template

    from app.services.document_converter import DocumentConverter
    from app.services.html_rendering_helpers import render_word, render_table_with_words


class TestDocumentConverter(unittest.TestCase):
    """
    Test suite for the DocumentConverter class and its helper functions.
    """
    def setUp(self):
        """Set up common objects for tests."""
        self.converter = DocumentConverter()
        self.options = MockRenderOptions(font_stack="Arial, sans-serif;")

    def test_to_html_pages_simple_document(self):
        """Tests conversion of a simple document with a single page and words."""
        mock_data = {
            "pages": [{
                "pageNumber": 1, "width": 8.5, "height": 11.0, "unit": "inch",
                "words": [
                    {"content": "Hello", "polygon": [1, 1, 2, 1, 2, 2, 1, 2], "span": {"offset": 0, "length": 5}, "confidence": 0.9},
                    {"content": "World", "polygon": [3, 3, 4, 3, 4, 4, 3, 4], "span": {"offset": 6, "length": 5}, "confidence": 0.9}
                ]
            }],
            "tables": []
        }
        html_pages = self.converter.to_html_pages(mock_data, self.options)
        self.assertEqual(len(html_pages), 1)
        html_content = html_pages[0]['html']
        self.assertIn("Hello", html_content)
        self.assertIn("World", html_content)
        self.assertIn("left: 129.41px; top: 129.41px;", html_content)
        self.assertIn("left: 388.24px; top: 388.24px;", html_content)

    def test_to_html_pages_with_table(self):
        """Tests that tables and their words are rendered correctly and not duplicated."""
        mock_data = {
            "pages": [{
                "pageNumber": 1, "width": 8.5, "height": 11.0, "unit": "inch",
                "words": [
                    {"content": "Header", "polygon": [1, 1, 2, 1, 2, 2, 1, 2], "span": {"offset": 0, "length": 6}, "confidence": 0.9},
                    {"content": "Cell1", "polygon": [3, 3, 4, 3, 4, 4, 3, 4], "span": {"offset": 7, "length": 5}, "confidence": 0.9},
                    {"content": "Standalone", "polygon": [5, 5, 6, 5, 6, 6, 5, 6], "span": {"offset": 13, "length": 10}, "confidence": 0.9}
                ],
            }],
            "tables": [{
                "boundingRegions": [{"pageNumber": 1, "polygon": [0.5, 0.5, 4.5, 0.5, 4.5, 4.5, 0.5, 4.5]}],
                "cells": [
                    {"rowIndex": 0, "columnIndex": 0, "content": "Header", "spans": [{"offset": 0, "length": 6}], "kind": "columnHeader"},
                    {"rowIndex": 1, "columnIndex": 0, "content": "Cell1", "spans": [{"offset": 7, "length": 5}]}
                ],
                "rowCount": 2, "columnCount": 1
            }]
        }
        html_pages = self.converter.to_html_pages(mock_data, self.options)
        self.assertEqual(len(html_pages), 1)
        html_content = html_pages[0]['html']
        self.assertIn("table-container", html_content)
        self.assertIn("Header", html_content)
        self.assertIn("Cell1", html_content)
        self.assertIn("Standalone", html_content)
        self.assertEqual(html_content.count('Header'), 1)
        self.assertEqual(html_content.count('Cell1'), 1)
        self.assertEqual(html_content.count('Standalone'), 1)

    def test_to_html_pages_multiple_pages(self):
        """Tests that the method correctly processes a multi-page document."""
        mock_data = {
            "pages": [
                {"pageNumber": 1, "width": 8.5, "height": 11.0, "unit": "inch", "words": [
                    {"content": "Page One", "span": {"offset": 0, "length": 8}, "polygon": [1,1,2,1,2,2,1,2], "confidence": 0.9}
                ]},
                {"pageNumber": 2, "width": 8.5, "height": 11.0, "unit": "inch", "words": [
                    {"content": "Page Two", "span": {"offset": 9, "length": 8}, "polygon": [1,1,2,1,2,2,1,2], "confidence": 0.9}
                ]}
            ],
            "tables": []
        }
        html_pages = self.converter.to_html_pages(mock_data, self.options)
        self.assertEqual(len(html_pages), 2)
        self.assertIn("Page One", html_pages[0]['html'])
        self.assertIn("Page Two", html_pages[1]['html'])

    def test_to_html_pages_pixel_unit(self):
        """Tests handling of 'pixel' units where no scaling should occur."""
        mock_data = {
            "pages": [{
                "pageNumber": 1, "width": 1000, "height": 1500, "unit": "pixel",
                "words": [{"content": "Pixel World", "polygon": [100, 200, 200, 200, 200, 250, 100, 250], "span": {"offset": 0, "length": 11}, "confidence": 0.9}]
            }],
            "tables": []
        }
        html_pages = self.converter.to_html_pages(mock_data, self.options)
        self.assertEqual(len(html_pages), 1)
        html_content = html_pages[0]['html']
        self.assertIn("width:1000.00px", html_content)
        self.assertIn("height:1500.00px", html_content)
        self.assertIn("left: 100.00px; top: 200.00px;", html_content)

    def test_to_html_pages_empty_document(self):
        """Tests that an empty document returns an empty list."""
        mock_data = {"pages": [], "tables": []}
        html_pages = self.converter.to_html_pages(mock_data, self.options)
        self.assertEqual(html_pages, [])

    def test_to_html_pages_missing_pages_key(self):
        """Tests that a document with a missing 'pages' key returns an empty list."""
        mock_data = {}
        html_pages = self.converter.to_html_pages(mock_data, self.options)
        self.assertEqual(html_pages, [])

    def test_render_word_low_confidence(self):
        """Tests that words with confidence below the threshold are not rendered."""
        word_data = {"content": "Test", "polygon": [1, 1, 2, 1, 2, 2, 1, 2], "confidence": 0.3}
        result = render_word(word_data, 1.0, "inch")
        self.assertEqual(result, "")

    def test_render_word_high_font_size_watermark(self):
        """Tests that words with an extremely large font size (potential watermark) are filtered."""
        word_data = {"content": "Watermark", "polygon": [1, 1, 400, 1, 200, 200, 1, 400], "confidence": 0.9}
        result = render_word(word_data, 1.0, "inch")
        self.assertEqual(result, "")

    def test_render_table_with_words_rotated_words(self):
        """Tests rendering a table with vertically oriented words."""
        mock_table_data = {
            "boundingRegions": [{"pageNumber": 1, "polygon": [1, 1, 2, 1, 2, 10, 1, 10]}],
            "cells": [{"rowIndex": 0, "columnIndex": 0, "spans": [{"offset": 0, "length": 4}], "kind": "columnHeader"}],
            "rowCount": 1, "columnCount": 1
        }
        mock_word_map = {
            0: {"content": "Test", "polygon": [1,1, 1,10, 2,10, 2,1], "span": {"offset": 0, "length": 4}, "confidence": 0.9}
        }
        html = render_table_with_words(mock_table_data, 1, 100, mock_word_map, set(), "inch")
        self.assertIn("position: relative;", html)
        self.assertIn("position: absolute;", html)
        self.assertIn("transform: rotate(90.00deg);", html)

    def test_with_user_provided_document(self):
        """Tests with a user-provided JSON document from a file."""
        file_path = os.path.join(os.path.dirname(__file__), 'test_json', 'user_document.json')
        if not os.path.exists(file_path):
            self.skipTest(f"Skipping test because '{file_path}' was not found.")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        
        html_pages = self.converter.to_html_pages(user_data, self.options)
        self.assertGreater(len(html_pages), 0, "No HTML pages were generated from the user's document.")

if __name__ == '__main__':
    unittest.main()
