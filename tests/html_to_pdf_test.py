import unittest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from io import StringIO
import pypdf
import asyncio

from app.services.html_to_pdf_converter import HtmlToPdfConverter


class TestHtmlToPdfConverter(unittest.TestCase):
    """
    Test suite for the HtmlToPdfConverter class.
    """

    def setUp(self):
        """
        Set up a temporary HTML file and an output PDF path for testing.
        """
        test_dir = Path(__file__).parent
        self.output_pdf_path = test_dir / "test_pdf_output" / "test_output.pdf"
        self.expected_pdf_path = test_dir / "expected_pdf_output" / "table_html.pdf"
        # The converter expects a list of dicts with html, width, and height.
        self.html_pages = [
            {
                "html": """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page 1</title>
    <style> body {
        font-family: Arial, sans-serif;
        background: #f0f0f0;
    }

    .page {
        margin: 20px auto;
        border: 1px solid #ccc;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
        background: white;
    }

    .table-container table {
        border-collapse: collapse;
        width: 100%;
    }

    .table-container th, .table-container td {
        border: 1px solid black;
        padding: 4px;
        text-align: center;
        font-size: 10px;
        position: relative;
        overflow: hidden;
    } </style>
</head>
<body>
<div class="page" style="width:1100.00px; height:1486.25px; transform:rotate(-0.7060999870300293deg);">
    <div class="table-container" style="position: absolute; left: 118.29px; top: 239.34px; width: 849.45px;">
        <table border="1">
            <tr>
                <td rowspan="1" colspan="2"
                    style="position: relative; min-width: 437.20px; min-height: 26.22px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Nome da Aluna: Maria
                        Eduarda Fonseca Canuto
                    </div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 229.09px; min-height: 22.72px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">R.G: 52.697.474-6
                    </div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 185.37px; min-height: 22.73px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">RA: 01316-1</div>
                </td>
            </tr>
            <tr>
                <td rowspan="2" colspan="1"
                    style="position: relative; min-width: 131.16px; min-height: 40.21px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Nascimento</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 306.04px; min-height: 25.35px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Município: Ribeirão
                        Preto
                    </div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 229.97px; min-height: 21.85px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Estado: SP</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 186.24px; min-height: 20.98px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">País: Brasil</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 306.04px; min-height: 24.47px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Data: 08/04/1998
                    </div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 229.97px; min-height: 23.60px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 186.24px; min-height: 21.85px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
        </table>
    </div>
    <div class="table-container" style="position: absolute; left: 166.80px; top: 299.32px; width: 820.47px;">
        <table border="1">
            <tr>
                <th rowspan="3" colspan="3"
                    style="position: relative; min-width: 558.02px; min-height: 80.48px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">COMPONENTES
                        CURRICULARES
                    </div>
                </th>
                <th rowspan="1" colspan="3"
                    style="position: relative; min-width: 237.94px; min-height: 19.48px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Período Letivo</div>
                </th>
            </tr>
            <tr>
                <th rowspan="1" colspan="1"
                    style="position: relative; min-width: 78.75px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">2013</div>
                </th>
                <th rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 19.48px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">2014</div>
                </th>
                <th rowspan="1" colspan="1"
                    style="position: relative; min-width: 79.60px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">2015</div>
                </th>
            </tr>
            <tr>
                <th rowspan="1" colspan="1"
                    style="position: relative; min-width: 79.59px; min-height: 36.43px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">1º</div>
                </th>
                <th rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 36.43px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">2º</div>
                </th>
                <th rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 36.43px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">3º</div>
                </th>
            </tr>
            <tr>
                <td rowspan="26" colspan="1"
                    style="position: relative; width: 47.42px; height: 452.39px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <span style="position: absolute; left: 18.48px; top: 385.65px; transform-origin: top left; transform: rotate(-90.28deg); font-size: 13.99px; line-height: 15.54px; white-space: nowrap;">BASE</span><span
                        style="position: absolute; left: 18.22px; top: 345.72px; transform-origin: top left; transform: rotate(-90.51deg); font-size: 14.16px; line-height: 15.73px; white-space: nowrap;">NACIONAL</span><span
                        style="position: absolute; left: 17.58px; top: 276.70px; transform-origin: top left; transform: rotate(-90.61deg); font-size: 14.24px; line-height: 15.83px; white-space: nowrap;">COMUM</span><span
                        style="position: absolute; left: 17.03px; top: 223.32px; transform-origin: top left; transform: rotate(-90.46deg); font-size: 14.15px; line-height: 15.72px; white-space: nowrap;">E</span><span
                        style="position: absolute; left: 16.93px; top: 211.48px; transform-origin: top left; transform: rotate(-90.60deg); font-size: 14.16px; line-height: 15.73px; white-space: nowrap;">PARTE</span><span
                        style="position: absolute; left: 16.42px; top: 165.46px; transform-origin: top left; transform: rotate(-90.68deg); font-size: 14.18px; line-height: 15.75px; white-space: nowrap;">DIVERSIFICADA</span>
                </td>
                <td rowspan="6" colspan="1"
                    style="position: relative; width: 94.84px; height: 105.05px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <span style="position: absolute; left: 51.55px; top: 69.65px; transform-origin: top left; transform: rotate(-90.91deg); font-size: 10.68px; line-height: 11.86px; white-space: nowrap;">suas</span><span
                        style="position: absolute; left: 32.48px; top: 86.85px; transform-origin: top left; transform: rotate(-90.27deg); font-size: 13.40px; line-height: 14.89px; white-space: nowrap;">Códigos</span><span
                        style="position: absolute; left: 32.38px; top: 29.12px; transform-origin: top left; transform: rotate(-91.15deg); font-size: 13.06px; line-height: 14.51px; white-space: nowrap;">e</span><span
                        style="position: absolute; left: 15.49px; top: 91.74px; transform-origin: top left; transform: rotate(-90.36deg); font-size: 13.63px; line-height: 15.15px; white-space: nowrap;">Linguagens</span><span
                        style="position: absolute; left: 66.79px; top: 92.18px; transform-origin: top left; transform: rotate(-90.22deg); font-size: 13.34px; line-height: 14.82px; white-space: nowrap;">Tecnologias</span>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 422.54px; min-height: 24.57px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Língua Portuguesa e
                        Literatura
                    </div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 79.59px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">7,5</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,00</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 79.59px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,5</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 421.69px; min-height: 25.41px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Arte</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 79.59px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">9,5</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 19.49px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">7,00</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 79.59px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 421.69px; min-height: 25.41px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Educação Física</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 79.59px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">9,5</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,25</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">10,0</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 422.53px; min-height: 24.57px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Inglês</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">8,0</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">7,50</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">8,5</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 422.53px; min-height: 25.42px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 79.60px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 79.59px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 421.69px; min-height: 25.41px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 79.59px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 79.59px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
        </table>
    </div>
</div>
</body>
</html>""",
                "width": 1100.0,
                "height": 1486.25
            }
        ]

    def get_pdf_text(self, pdf_path: str) -> str:
        """Helper to extract text from a PDF file."""
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    def tearDown(self):
        """Clean up generated files after each test."""
        if os.path.exists(self.output_pdf_path):
            os.remove(self.output_pdf_path)

    def test_convert_html_to_pdf(self):
        """
        Tests the end-to-end conversion from HTML content to a PDF file.
        It generates a PDF and then compares its text content to a
        known-good PDF provided by the user.

        NOTE: Before running this test, you must place your pre-generated PDF
        file in the same directory as this test file, and name it 'expected_pdf_output.pdf'.
        """

        async def run_test():
            # Generate the actual PDF file
            converter = HtmlToPdfConverter(self.html_pages)
            await converter.convert_to_pdf()

            # Check if the output file was created
            self.assertTrue(os.path.exists(self.output_pdf_path))
            self.assertTrue(os.path.exists(self.expected_pdf_path))

            # Extract and compare the text content of the two PDFs
            expected_text = self.get_pdf_text(self.expected_pdf_path)
            actual_text = self.get_pdf_text(self.output_pdf_path)

            # Clean up any whitespace differences
            self.assertEqual(expected_text.strip(), actual_text.strip())

        asyncio.run(run_test())

    @patch('app.services.html_to_pdf_converter.get_browser', side_effect=Exception("Test Error"))
    def test_convert_exception_handling(self, mock_get_browser):
        async def run_test():
            with self.assertRaises(RuntimeError) as context:
                await HtmlToPdfConverter(self.html_pages).convert_to_pdf()
            self.assertIn("Error during conversion:", str(context.exception))

        asyncio.run(run_test())