# --- Core Imports ---
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
import pytest

# --- Add project root to Python path ---
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# --- Custom Imports ---
from app.services.renderer import DocumentRenderer
from app.services.docx_converter import DocxConverter


class TestDocxConverter:
    """Test suite for DocxConverter service."""

    def test_docx_converter_initialization(self):
        """Tests that DocxConverter initializes correctly."""
        converter = DocxConverter()
        assert converter.FONT_NAME == "Calibri"
        assert converter.PAGE_WIDTH_INCH == 8.27
        assert converter.PAGE_HEIGHT_INCH == 11.69
        assert converter.EMU_PER_INCH == 914400
        assert converter.ROT_UNITS_PER_DEGREE == 60000

    def test_extract_coords_dict_format(self):
        """Tests coordinate extraction from dictionary format polygon."""
        converter = DocxConverter()
        poly = [{"x": 10, "y": 20}, {"x": 30, "y": 40}]
        xs, ys = converter._extract_coords(poly)
        assert xs == [10.0, 30.0]
        assert ys == [20.0, 40.0]

    def test_extract_coords_flat_list_format(self):
        """Tests coordinate extraction from flat list format [x,y,x,y,...]."""
        converter = DocxConverter()
        poly = [10, 20, 30, 40]
        xs, ys = converter._extract_coords(poly)
        assert xs == [10.0, 30.0]
        assert ys == [20.0, 40.0]

    def test_extract_coords_empty_polygon(self):
        """Tests that empty polygon returns empty lists."""
        converter = DocxConverter()
        xs, ys = converter._extract_coords([])
        assert xs == []
        assert ys == []

    def test_convert_to_docx_bytes_simple(self):
        """Tests that convert_to_docx_bytes returns valid DOCX bytes."""
        converter = DocxConverter()
        
        # Minimal Azure JSON structure
        azure_json = {
            "pages": [{
                "pageNumber": 1,
                "width": 2480,
                "height": 3508,
                "unit": "pixel",
                "lines": [{
                    "content": "Test Line",
                    "polygon": [{"x": 100, "y": 100}, {"x": 200, "y": 100}, 
                               {"x": 200, "y": 120}, {"x": 100, "y": 120}]
                }]
            }]
        }
        
        docx_bytes = converter.convert_to_docx_bytes(azure_json)
        
        # Verify it's bytes and has DOCX magic number
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 0
        # DOCX files are ZIP archives, check ZIP signature
        assert docx_bytes[:4] == b'PK\x03\x04'

    def test_convert_to_docx_bytes_with_rotation(self):
        """Tests DOCX conversion with rotated text."""
        converter = DocxConverter()
        
        # Azure JSON with rotated text (polygon defines rotation)
        azure_json = {
            "pages": [{
                "pageNumber": 1,
                "width": 2480,
                "height": 3508,
                "unit": "pixel",
                "lines": [{
                    "content": "Rotated Text",
                    "polygon": [
                        {"x": 100, "y": 100},  # p1
                        {"x": 150, "y": 120},  # p2 (defines rotation angle)
                        {"x": 130, "y": 140},  # p3
                        {"x": 80, "y": 120}    # p4
                    ]
                }]
            }]
        }
        
        docx_bytes = converter.convert_to_docx_bytes(azure_json)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 0

    def test_convert_to_docx_bytes_with_tables(self):
        """Tests DOCX conversion with table structures."""
        converter = DocxConverter()
        
        azure_json = {
            "pages": [{
                "pageNumber": 1,
                "width": 2480,
                "height": 3508,
                "unit": "pixel",
                "lines": []
            }],
            "tables": [{
                "cells": [{
                    "content": "Cell 1",
                    "boundingRegions": [{
                        "pageNumber": 1,
                        "polygon": [{"x": 100, "y": 100}, {"x": 200, "y": 100},
                                   {"x": 200, "y": 120}, {"x": 100, "y": 120}]
                    }]
                }]
            }]
        }
        
        docx_bytes = converter.convert_to_docx_bytes(azure_json)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 0

    def test_convert_to_docx_bytes_empty_pages(self):
        """Tests handling of Azure JSON with no pages."""
        converter = DocxConverter()
        azure_json = {"pages": []}
        
        docx_bytes = converter.convert_to_docx_bytes(azure_json)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 0
        # Verify it's a valid ZIP (DOCX format)
        assert docx_bytes[:4] == b'PK\x03\x04'

    def test_convert_to_docx_bytes_multi_page(self):
        """Tests DOCX conversion with multiple pages."""
        converter = DocxConverter()
        
        azure_json = {
            "pages": [
                {
                    "pageNumber": 1,
                    "width": 2480,
                    "height": 3508,
                    "unit": "pixel",
                    "lines": [{"content": "Page 1", "polygon": [{"x": 100, "y": 100}, 
                             {"x": 200, "y": 100}, {"x": 200, "y": 120}, {"x": 100, "y": 120}]}]
                },
                {
                    "pageNumber": 2,
                    "width": 2480,
                    "height": 3508,
                    "unit": "pixel",
                    "lines": [{"content": "Page 2", "polygon": [{"x": 100, "y": 100}, 
                             {"x": 200, "y": 100}, {"x": 200, "y": 120}, {"x": 100, "y": 120}]}]
                }
            ]
        }
        
        docx_bytes = converter.convert_to_docx_bytes(azure_json)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 0


class TestDocxWorkflow:
    """Integration tests for the complete DOCX workflow."""

    @pytest.mark.asyncio
    async def test_analyze_and_render_docx_complete_workflow(self):
        """Tests the complete analyze_and_render_docx workflow."""
        renderer = DocumentRenderer()
        
        mock_analysis_result = {
            "pages": [{
                "pageNumber": 1,
                "width": 2480,
                "height": 3508,
                "unit": "pixel",
                "lines": [{
                    "content": "Sample Text",
                    "polygon": [{"x": 100, "y": 100}, {"x": 200, "y": 100},
                               {"x": 200, "y": 120}, {"x": 100, "y": 120}]
                }]
            }]
        }
        
        mock_blob_url = "https://storage.azure.com/container/doc_20251212_abc123.docx?sas_token"
        
        with patch.object(renderer, 'analyze_document', new_callable=AsyncMock) as mock_analyze, \
             patch.object(renderer, 'upload_docx_bytes_to_blob') as mock_upload:
            
            mock_analyze.return_value = mock_analysis_result
            mock_upload.return_value = mock_blob_url
            
            file_content = b"fake PDF content"
            result_url = await renderer.analyze_and_render_docx(file_content)
            
            # Verify analyze_document was called
            mock_analyze.assert_called_once_with(file_content)
            
            # Verify upload was called with correct parameters
            mock_upload.assert_called_once()
            call_args = mock_upload.call_args
            assert call_args[0][0].startswith("doc_")  # blob_name
            assert call_args[0][0].endswith(".docx")
            assert isinstance(call_args[0][1], bytes)  # docx_bytes
            
            # Verify result
            assert result_url == mock_blob_url

    @pytest.mark.asyncio
    async def test_analyze_and_render_docx_analysis_failure(self):
        """Tests error handling when document analysis fails."""
        renderer = DocumentRenderer()
        
        with patch.object(renderer, 'analyze_document', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.side_effect = Exception("Azure API error")
            
            file_content = b"fake PDF content"
            
            with pytest.raises(Exception) as exc_info:
                await renderer.analyze_and_render_docx(file_content)
            
            assert "Azure API error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_analyze_and_render_docx_upload_failure(self):
        """Tests error handling when blob upload fails."""
        renderer = DocumentRenderer()
        
        mock_analysis_result = {
            "pages": [{
                "pageNumber": 1,
                "width": 2480,
                "height": 3508,
                "unit": "pixel",
                "lines": []
            }]
        }
        
        with patch.object(renderer, 'analyze_document', new_callable=AsyncMock) as mock_analyze, \
             patch.object(renderer, 'upload_docx_bytes_to_blob') as mock_upload:
            
            mock_analyze.return_value = mock_analysis_result
            mock_upload.side_effect = Exception("Blob upload failed")
            
            file_content = b"fake PDF content"
            
            with pytest.raises(Exception) as exc_info:
                await renderer.analyze_and_render_docx(file_content)
            
            assert "Blob upload failed" in str(exc_info.value)

    def test_upload_docx_bytes_to_blob_success(self):
        """Tests successful DOCX upload to Azure Blob Storage."""
        renderer = DocumentRenderer()
        
        blob_name = "test_document.docx"
        docx_bytes = b"PK\x03\x04" + b"fake docx content"
        
        with patch('app.services.renderer.BlobClient') as mock_blob_client_class:
            mock_blob_client = MagicMock()
            mock_blob_client_class.from_blob_url.return_value = mock_blob_client
            
            # Mock the settings to have a proper blob URL
            with patch('app.services.renderer.settings') as mock_settings:
                mock_settings.blob_url = "https://storage.azure.com/container?sas_token"
                
                result_url = renderer.upload_docx_bytes_to_blob(blob_name, docx_bytes)
                
                # Verify BlobClient was created with correct URL
                assert result_url.startswith("https://storage.azure.com/container/")
                assert blob_name in result_url
                
                # Verify upload_blob was called
                mock_blob_client.upload_blob.assert_called_once_with(docx_bytes, overwrite=True)

    def test_upload_docx_bytes_to_blob_failure(self):
        """Tests error handling when blob upload fails."""
        renderer = DocumentRenderer()
        
        blob_name = "test_document.docx"
        docx_bytes = b"fake docx content"
        
        with patch('app.services.renderer.BlobClient') as mock_blob_client_class:
            mock_blob_client = MagicMock()
            mock_blob_client.upload_blob.side_effect = Exception("Network error")
            mock_blob_client_class.from_blob_url.return_value = mock_blob_client
            
            with patch('app.services.renderer.settings') as mock_settings:
                mock_settings.blob_url = "https://storage.azure.com/container?sas_token"
                
                from fastapi import HTTPException
                with pytest.raises(HTTPException) as exc_info:
                    renderer.upload_docx_bytes_to_blob(blob_name, docx_bytes)
                
                assert exc_info.value.status_code == 500
                assert "Network error" in exc_info.value.detail


class TestDocxConverterEdgeCases:
    """Tests for edge cases and boundary conditions in DOCX conversion."""

    def test_normalized_coordinates(self):
        """Tests handling of normalized coordinates (0-1 range)."""
        converter = DocxConverter()
        
        # Azure JSON with normalized coordinates
        azure_json = {
            "pages": [{
                "pageNumber": 1,
                "width": 2480,
                "height": 3508,
                "unit": "pixel",
                "lines": [{
                    "content": "Normalized",
                    "polygon": [
                        {"x": 0.1, "y": 0.1},  # Normalized (0-1)
                        {"x": 0.2, "y": 0.1},
                        {"x": 0.2, "y": 0.15},
                        {"x": 0.1, "y": 0.15}
                    ]
                }]
            }]
        }
        
        docx_bytes = converter.convert_to_docx_bytes(azure_json)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 0

    def test_missing_polygon_with_bounding_box(self):
        """Tests handling when polygon is missing but boundingBox is present."""
        converter = DocxConverter()
        
        azure_json = {
            "pages": [{
                "pageNumber": 1,
                "width": 2480,
                "height": 3508,
                "unit": "pixel",
                "lines": [{
                    "content": "BBox Only",
                    "boundingBox": {
                        "left": 100,
                        "top": 100,
                        "width": 100,
                        "height": 20
                    }
                }]
            }]
        }
        
        docx_bytes = converter.convert_to_docx_bytes(azure_json)
        assert isinstance(docx_bytes, bytes)

    def test_empty_content_lines(self):
        """Tests handling of lines with empty content."""
        converter = DocxConverter()
        
        azure_json = {
            "pages": [{
                "pageNumber": 1,
                "width": 2480,
                "height": 3508,
                "unit": "pixel",
                "lines": [
                    {"content": "", "polygon": [{"x": 100, "y": 100}, {"x": 200, "y": 100},
                                                {"x": 200, "y": 120}, {"x": 100, "y": 120}]},
                    {"content": "   ", "polygon": [{"x": 100, "y": 150}, {"x": 200, "y": 150},
                                                   {"x": 200, "y": 170}, {"x": 100, "y": 170}]}
                ]
            }]
        }
        
        # Should not crash, but may skip empty lines
        docx_bytes = converter.convert_to_docx_bytes(azure_json)
        assert isinstance(docx_bytes, bytes)

    def test_very_small_text_boxes(self):
        """Tests handling of very small text boxes."""
        converter = DocxConverter()
        
        azure_json = {
            "pages": [{
                "pageNumber": 1,
                "width": 2480,
                "height": 3508,
                "unit": "pixel",
                "lines": [{
                    "content": "x",
                    "polygon": [
                        {"x": 100, "y": 100},
                        {"x": 101, "y": 100},  # 1 pixel wide
                        {"x": 101, "y": 101},  # 1 pixel tall
                        {"x": 100, "y": 101}
                    ]
                }]
            }]
        }
        
        docx_bytes = converter.convert_to_docx_bytes(azure_json)
        assert isinstance(docx_bytes, bytes)

    def test_page_without_unit(self):
        """Tests handling when page unit is missing (defaults to pixel)."""
        converter = DocxConverter()
        
        azure_json = {
            "pages": [{
                "pageNumber": 1,
                "width": 2480,
                "height": 3508,
                # No 'unit' field
                "lines": [{
                    "content": "Test",
                    "polygon": [{"x": 100, "y": 100}, {"x": 200, "y": 100},
                               {"x": 200, "y": 120}, {"x": 100, "y": 120}]
                }]
            }]
        }
        
        docx_bytes = converter.convert_to_docx_bytes(azure_json)
        assert isinstance(docx_bytes, bytes)
