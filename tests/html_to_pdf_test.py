import unittest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from io import StringIO
import pypdf

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
        self.html_content = ["""<!DOCTYPE html>
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
                    style="position: relative; min-width: 422.53px; min-height: 25.42px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="6" colspan="1"
                    style="position: relative; width: 93.99px; height: 105.05px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <span style="position: absolute; left: 60.62px; top: 78.10px; transform-origin: top left; transform: rotate(-91.72deg); font-size: 11.11px; line-height: 12.34px; white-space: nowrap;">e</span><span
                        style="position: absolute; left: 60.07px; top: 60.90px; transform-origin: top left; transform: rotate(-90.64deg); font-size: 11.55px; line-height: 12.83px; white-space: nowrap;">suas</span><span
                        style="position: absolute; left: 24.68px; top: 86.54px; transform-origin: top left; transform: rotate(-89.96deg); font-size: 12.31px; line-height: 13.68px; white-space: nowrap;">Natureza,</span><span
                        style="position: absolute; left: 41.83px; top: 91.50px; transform-origin: top left; transform: rotate(-90.66deg); font-size: 13.21px; line-height: 14.68px; white-space: nowrap;">Matemática</span><span
                        style="position: absolute; left: 6.71px; top: 92.39px; transform-origin: top left; transform: rotate(-90.51deg); font-size: 12.42px; line-height: 13.80px; white-space: nowrap;">Ciências</span><span
                        style="position: absolute; left: 6.26px; top: 33.00px; transform-origin: top left; transform: rotate(-90.74deg); font-size: 12.79px; line-height: 14.21px; white-space: nowrap;">da</span><span
                        style="position: absolute; left: 76.05px; top: 92.56px; transform-origin: top left; transform: rotate(-90.56deg); font-size: 13.14px; line-height: 14.61px; white-space: nowrap;">Tecnologias</span>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 422.53px; min-height: 24.57px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Matemática</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 79.60px; min-height: 19.49px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,0</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 19.49px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,00</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">7,0</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 423.38px; min-height: 24.57px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Biologia</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,5</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 19.48px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,00</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,5</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 423.38px; min-height: 25.41px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Física</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,0</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,00</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 19.49px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">7,0</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 423.38px; min-height: 24.57px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Química</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,5</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,00</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,0</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 423.38px; min-height: 24.57px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 19.49px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 424.23px; min-height: 25.41px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 20.33px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="6" colspan="1"
                    style="position: relative; width: 94.84px; height: 105.05px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <span style="position: absolute; left: 52.72px; top: 69.47px; transform-origin: top left; transform: rotate(-90.38deg); font-size: 11.06px; line-height: 12.29px; white-space: nowrap;">suas</span><span
                        style="position: absolute; left: 15.43px; top: 82.35px; transform-origin: top left; transform: rotate(-89.98deg); font-size: 13.25px; line-height: 14.72px; white-space: nowrap;">Ciências</span><span
                        style="position: absolute; left: 68.31px; top: 92.29px; transform-origin: top left; transform: rotate(-90.01deg); font-size: 13.40px; line-height: 14.89px; white-space: nowrap;">Tecnologias</span><span
                        style="position: absolute; left: 33.83px; top: 93.01px; transform-origin: top left; transform: rotate(-89.65deg); font-size: 12.75px; line-height: 14.16px; white-space: nowrap;">Humanas</span><span
                        style="position: absolute; left: 34.36px; top: 23.07px; transform-origin: top left; transform: rotate(-90.84deg); font-size: 12.28px; line-height: 13.64px; white-space: nowrap;">e</span>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 424.23px; min-height: 24.57px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">História</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">7,0</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,50</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">8,5</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 425.07px; min-height: 24.57px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Geografia</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">7,0</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,63</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">7,5</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 424.23px; min-height: 25.41px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 425.07px; min-height: 25.41px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.13px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 425.07px; min-height: 25.41px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 80.44px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 425.92px; min-height: 27.11px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 19.49px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 19.49px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 19.48px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="2"
                    style="position: relative; min-width: 519.06px; min-height: 27.11px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">CARGA HORÁRIA - BASE
                        NACIONAL COMUM
                    </div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">1400</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 19.49px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">1200</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">1320</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="2"
                    style="position: relative; min-width: 519.06px; min-height: 26.26px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Filosofia</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">8,0</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">7,13</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">7,5</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="2"
                    style="position: relative; min-width: 519.06px; min-height: 26.26px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Sociologia</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">7,5</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">7,00</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">8,5</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="2"
                    style="position: relative; min-width: 519.06px; min-height: 27.11px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Espanhol</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 81.29px; min-height: 19.49px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 20.33px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">6,50</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 20.33px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">-</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="2"
                    style="position: relative; min-width: 519.91px; min-height: 27.11px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Redação</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">7,00</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 19.49px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="2"
                    style="position: relative; min-width: 519.91px; min-height: 27.11px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 19.48px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="2"
                    style="position: relative; min-width: 519.91px; min-height: 27.96px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.13px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 20.33px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="2"
                    style="position: relative; min-width: 519.91px; min-height: 28.80px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 19.48px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.13px; min-height: 17.79px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 20.33px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="3"
                    style="position: relative; min-width: 563.94px; min-height: 27.11px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">CARGA HORÁRIA - PARTE
                        DIVERSIFICADA
                    </div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 20.33px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">80</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 18.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">160</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.98px; min-height: 20.33px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">80</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="3"
                    style="position: relative; min-width: 563.94px; min-height: 25.41px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">TOTAL DE CARGA
                        HORÁRIA
                    </div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.14px; min-height: 16.94px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">1480</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.98px; min-height: 16.94px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">1360</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 82.98px; min-height: 16.94px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">1400</div>
                </td>
            </tr>
        </table>
    </div>
    <div class="table-container" style="position: absolute; left: 173.13px; top: 847.53px; width: 813.72px;">
        <table border="1">
            <tr>
                <td rowspan="6" colspan="1"
                    style="position: relative; width: 41.18px; height: 98.55px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <span style="position: absolute; left: 6.90px; top: 78.58px; transform-origin: top left; transform: rotate(-91.19deg); font-size: 10.97px; line-height: 12.18px; white-space: nowrap;">ESTUDOS</span><span
                        style="position: absolute; left: 19.55px; top: 87.06px; transform-origin: top left; transform: rotate(-90.32deg); font-size: 11.95px; line-height: 13.28px; white-space: nowrap;">REALIZADOS</span>
                </td>
                <td rowspan="2" colspan="1"
                    style="position: relative; min-width: 107.57px; min-height: 36.22px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Fundamental Ensino
                    </div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 95.80px; min-height: 17.69px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Série/Termo</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 52.95px; min-height: 17.69px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Ano</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 266.40px; min-height: 20.22px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Estabelecimento de
                        Ensino
                    </div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 168.92px; min-height: 20.22px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Município</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 76.48px; min-height: 18.53px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">UF</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 95.80px; min-height: 19.37px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">8ª</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 52.10px; min-height: 19.37px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">2012</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 265.56px; min-height: 21.90px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Colégio Lacordaire
                        Sant'Anna
                    </div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 168.92px; min-height: 20.22px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Ribeirão Preto</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 76.48px; min-height: 18.53px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">SP</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="2"
                    style="position: relative; min-width: 203.37px; min-height: 13.47px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 52.10px; min-height: 10.95px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 266.40px; min-height: 14.32px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 168.92px; min-height: 12.64px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 76.48px; min-height: 10.95px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;"></div>
                </td>
            </tr>
            <tr>
                <td rowspan="3" colspan="1"
                    style="position: relative; min-width: 107.57px; min-height: 55.59px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Ensino Médio</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 95.80px; min-height: 17.69px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">1º</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 52.10px; min-height: 16.85px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">2013</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 266.40px; min-height: 21.06px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Colégio Lacordaire -
                        Ensino Médio
                    </div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 168.92px; min-height: 19.37px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Ribeirão Preto</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 76.48px; min-height: 17.69px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">SP</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 95.80px; min-height: 19.37px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">2º</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 52.10px; min-height: 17.69px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">2014</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 266.40px; min-height: 21.90px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Colégio Viana</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 168.92px; min-height: 20.22px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Ribeirão Preto</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 76.48px; min-height: 18.53px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">SP</div>
                </td>
            </tr>
            <tr>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 95.80px; min-height: 21.06px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">3º</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 52.10px; min-height: 19.37px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">2015</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 266.40px; min-height: 22.74px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Colégio Lacordaire -
                        Ensino Médio
                    </div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 168.92px; min-height: 21.06px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">Ribeirão Preto</div>
                </td>
                <td rowspan="1" colspan="1"
                    style="position: relative; min-width: 76.48px; min-height: 20.22px; padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; text-align: left; border: 1px solid black;">
                    <div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">SP</div>
                </td>
            </tr>
        </table>
    </div>
    <span class="word"
          style="position: absolute; left: 131.18px; top: 144.70px; transform-origin: top left; transform: rotate(-1.32deg); font-size: 15.28px; line-height: 19.10px; white-space: nowrap; color: rgba(0,0,0,0.9);">OLÉGIO</span><span
        class="word"
        style="position: absolute; left: 206.32px; top: 142.93px; transform-origin: top left; transform: rotate(-1.37deg); font-size: 14.03px; line-height: 17.53px; white-space: nowrap; color: rgba(0,0,0,0.9);">ACORDAIRE</span><span
        class="word"
        style="position: absolute; left: 369.25px; top: 76.71px; transform-origin: top left; transform: rotate(-0.85deg); font-size: 23.94px; line-height: 29.93px; white-space: nowrap; color: rgba(0,0,0,0.9);">COLÉGIO</span><span
        class="word"
        style="position: absolute; left: 498.11px; top: 74.91px; transform-origin: top left; transform: rotate(-0.48deg); font-size: 24.50px; line-height: 30.62px; white-space: nowrap; color: rgba(0,0,0,0.9);">LACORDAIRE</span><span
        class="word"
        style="position: absolute; left: 677.53px; top: 73.49px; transform-origin: top left; transform: rotate(-0.74deg); font-size: 24.02px; line-height: 30.03px; white-space: nowrap; color: rgba(0,0,0,0.9);">ENSINO</span><span
        class="word"
        style="position: absolute; left: 788.55px; top: 72.15px; transform-origin: top left; transform: rotate(-0.34deg); font-size: 24.40px; line-height: 30.50px; white-space: nowrap; color: rgba(0,0,0,0.9);">MÉDIO</span><span
        class="word"
        style="position: absolute; left: 441.74px; top: 111.72px; transform-origin: top left; transform: rotate(-0.41deg); font-size: 11.49px; line-height: 14.36px; white-space: nowrap; color: rgba(0,0,0,0.9);">Rua</span><span
        class="word"
        style="position: absolute; left: 467.60px; top: 111.54px; transform-origin: top left; transform: rotate(-0.69deg); font-size: 11.60px; line-height: 14.49px; white-space: nowrap; color: rgba(0,0,0,0.9);">Antônio</span><span
        class="word"
        style="position: absolute; left: 516.18px; top: 110.95px; transform-origin: top left; transform: rotate(-0.59deg); font-size: 11.79px; line-height: 14.73px; white-space: nowrap; color: rgba(0,0,0,0.9);">Milena</span><span
        class="word"
        style="position: absolute; left: 562.59px; top: 110.48px; transform-origin: top left; transform: rotate(-0.59deg); font-size: 11.88px; line-height: 14.84px; white-space: nowrap; color: rgba(0,0,0,0.9);">1811</span><span
        class="word"
        style="position: absolute; left: 593.52px; top: 110.16px; transform-origin: top left; transform: rotate(-0.49deg); font-size: 11.82px; line-height: 14.77px; white-space: nowrap; color: rgba(0,0,0,0.9);">-</span><span
        class="word"
        style="position: absolute; left: 602.71px; top: 110.08px; transform-origin: top left; transform: rotate(-0.54deg); font-size: 11.81px; line-height: 14.76px; white-space: nowrap; color: rgba(0,0,0,0.9);">Campos</span><span
        class="word"
        style="position: absolute; left: 653.94px; top: 109.58px; transform-origin: top left; transform: rotate(-0.68deg); font-size: 11.91px; line-height: 14.89px; white-space: nowrap; color: rgba(0,0,0,0.9);">Elíseos</span><span
        class="word"
        style="position: absolute; left: 695.03px; top: 109.10px; transform-origin: top left; transform: rotate(-0.55deg); font-size: 12.07px; line-height: 15.09px; white-space: nowrap; color: rgba(0,0,0,0.9);">-</span><span
        class="word"
        style="position: absolute; left: 703.98px; top: 109.01px; transform-origin: top left; transform: rotate(-0.56deg); font-size: 12.03px; line-height: 15.04px; white-space: nowrap; color: rgba(0,0,0,0.9);">CEP:</span><span
        class="word"
        style="position: absolute; left: 734.18px; top: 108.72px; transform-origin: top left; transform: rotate(-0.37deg); font-size: 11.88px; line-height: 14.85px; white-space: nowrap; color: rgba(0,0,0,0.9);">14085-660</span><span
        class="word"
        style="position: absolute; left: 564.71px; top: 128.22px; transform-origin: top left; transform: rotate(-0.71deg); font-size: 10.32px; line-height: 12.90px; white-space: nowrap; color: rgba(0,0,0,0.9);">Ribeirão</span><span
        class="word"
        style="position: absolute; left: 618.17px; top: 127.55px; transform-origin: top left; transform: rotate(-0.26deg); font-size: 10.65px; line-height: 13.31px; white-space: nowrap; color: rgba(0,0,0,0.9);">Preto</span><span
        class="word"
        style="position: absolute; left: 653.10px; top: 127.41px; transform-origin: top left; transform: rotate(-0.56deg); font-size: 10.56px; line-height: 13.20px; white-space: nowrap; color: rgba(0,0,0,0.9);">-</span><span
        class="word"
        style="position: absolute; left: 660.64px; top: 127.34px; transform-origin: top left; transform: rotate(-0.80deg); font-size: 10.53px; line-height: 13.16px; white-space: nowrap; color: rgba(0,0,0,0.9);">SP</span><span
        class="word"
        style="position: absolute; left: 464.12px; top: 145.69px; transform-origin: top left; transform: rotate(-0.52deg); font-size: 11.40px; line-height: 14.26px; white-space: nowrap; color: rgba(0,0,0,0.9);">Fone</span><span
        class="word"
        style="position: absolute; left: 496.67px; top: 145.39px; transform-origin: top left; transform: rotate(-0.65deg); font-size: 11.55px; line-height: 14.44px; white-space: nowrap; color: rgba(0,0,0,0.9);">-</span><span
        class="word"
        style="position: absolute; left: 505.72px; top: 145.30px; transform-origin: top left; transform: rotate(-0.81deg); font-size: 11.56px; line-height: 14.45px; white-space: nowrap; color: rgba(0,0,0,0.9);">Fax</span><span
        class="word"
        style="position: absolute; left: 523.82px; top: 145.04px; transform-origin: top left; transform: rotate(-0.86deg); font-size: 11.65px; line-height: 14.57px; white-space: nowrap; color: rgba(0,0,0,0.9);">::</span><span
        class="word"
        style="position: absolute; left: 540.21px; top: 144.78px; transform-origin: top left; transform: rotate(-1.01deg); font-size: 11.73px; line-height: 14.66px; white-space: nowrap; color: rgba(0,0,0,0.9);">16-</span><span
        class="word"
        style="position: absolute; left: 562.23px; top: 144.39px; transform-origin: top left; transform: rotate(-0.74deg); font-size: 11.86px; line-height: 14.82px; white-space: nowrap; color: rgba(0,0,0,0.9);">3626-0655</span><span
        class="word"
        style="position: absolute; left: 628.52px; top: 143.56px; transform-origin: top left; transform: rotate(-0.48deg); font-size: 12.13px; line-height: 15.16px; white-space: nowrap; color: rgba(0,0,0,0.9);">/</span><span
        class="word"
        style="position: absolute; left: 638.07px; top: 143.48px; transform-origin: top left; transform: rotate(-0.53deg); font-size: 12.13px; line-height: 15.16px; white-space: nowrap; color: rgba(0,0,0,0.9);">3615-8222</span><span
        class="word"
        style="position: absolute; left: 703.39px; top: 142.88px; transform-origin: top left; transform: rotate(-0.48deg); font-size: 12.25px; line-height: 15.31px; white-space: nowrap; color: rgba(0,0,0,0.9);">/</span><span
        class="word"
        style="position: absolute; left: 712.93px; top: 142.80px; transform-origin: top left; transform: rotate(-0.18deg); font-size: 12.22px; line-height: 15.27px; white-space: nowrap; color: rgba(0,0,0,0.9);">3615-8711</span><span
        class="word"
        style="position: absolute; left: 409.68px; top: 169.79px; transform-origin: top left; transform: rotate(-0.64deg); font-size: 11.28px; line-height: 14.10px; white-space: nowrap; color: rgba(0,0,0,0.9);">Autorização</span><span
        class="word"
        style="position: absolute; left: 475.12px; top: 169.06px; transform-origin: top left; transform: rotate(-0.69deg); font-size: 11.56px; line-height: 14.45px; white-space: nowrap; color: rgba(0,0,0,0.9);">de</span><span
        class="word"
        style="position: absolute; left: 492.92px; top: 168.84px; transform-origin: top left; transform: rotate(-0.77deg); font-size: 11.59px; line-height: 14.49px; white-space: nowrap; color: rgba(0,0,0,0.9);">Funcionamento:</span><span
        class="word"
        style="position: absolute; left: 582.17px; top: 167.65px; transform-origin: top left; transform: rotate(-0.77deg); font-size: 11.71px; line-height: 14.63px; white-space: nowrap; color: rgba(0,0,0,0.9);">Deliberação</span><span
        class="word"
        style="position: absolute; left: 646.41px; top: 166.77px; transform-origin: top left; transform: rotate(-0.85deg); font-size: 11.98px; line-height: 14.97px; white-space: nowrap; color: rgba(0,0,0,0.9);">CEE</span><span
        class="word"
        style="position: absolute; left: 668.54px; top: 166.45px; transform-origin: top left; transform: rotate(-0.63deg); font-size: 12.03px; line-height: 15.03px; white-space: nowrap; color: rgba(0,0,0,0.9);">01/99</span><span
        class="word"
        style="position: absolute; left: 702.22px; top: 166.08px; transform-origin: top left; transform: rotate(-0.54deg); font-size: 12.03px; line-height: 15.03px; white-space: nowrap; color: rgba(0,0,0,0.9);">-</span><span
        class="word"
        style="position: absolute; left: 711.84px; top: 165.99px; transform-origin: top left; transform: rotate(-0.61deg); font-size: 12.00px; line-height: 15.00px; white-space: nowrap; color: rgba(0,0,0,0.9);">DOE</span><span
        class="word"
        style="position: absolute; left: 738.79px; top: 165.70px; transform-origin: top left; transform: rotate(-0.34deg); font-size: 11.94px; line-height: 14.93px; white-space: nowrap; color: rgba(0,0,0,0.9);">03/02/2005</span><span
        class="word"
        style="position: absolute; left: 452.09px; top: 195.94px; transform-origin: top left; transform: rotate(-0.73deg); font-size: 16.26px; line-height: 20.32px; white-space: nowrap; color: rgba(0,0,0,0.9);">HISTÓRICO</span><span
        class="word"
        style="position: absolute; left: 562.75px; top: 194.56px; transform-origin: top left; transform: rotate(-0.58deg); font-size: 16.94px; line-height: 21.17px; white-space: nowrap; color: rgba(0,0,0,0.9);">ESCOLAR</span><span
        class="word"
        style="position: absolute; left: 651.98px; top: 193.62px; transform-origin: top left; transform: rotate(-0.69deg); font-size: 17.07px; line-height: 21.34px; white-space: nowrap; color: rgba(0,0,0,0.9);">-</span><span
        class="word"
        style="position: absolute; left: 665.12px; top: 193.49px; transform-origin: top left; transform: rotate(-0.42deg); font-size: 17.04px; line-height: 21.30px; white-space: nowrap; color: rgba(0,0,0,0.9);">ENSINO</span><span
        class="word"
        style="position: absolute; left: 742.94px; top: 192.95px; transform-origin: top left; transform: rotate(-0.35deg); font-size: 17.01px; line-height: 21.27px; white-space: nowrap; color: rgba(0,0,0,0.9);">MÉDIO</span><span
        class="word"
        style="position: absolute; left: 134.21px; top: 900.83px; transform-origin: top left; transform: rotate(-90.33deg); font-size: 12.83px; line-height: 16.03px; white-space: nowrap; color: rgba(0,0,0,0.9);">Fundamento</span><span
        class="word"
        style="position: absolute; left: 133.72px; top: 821.08px; transform-origin: top left; transform: rotate(-90.53deg); font-size: 13.10px; line-height: 16.38px; white-space: nowrap; color: rgba(0,0,0,0.9);">Legal:</span><span
        class="word"
        style="position: absolute; left: 133.39px; top: 784.46px; transform-origin: top left; transform: rotate(-90.35deg); font-size: 13.18px; line-height: 16.47px; white-space: nowrap; color: rgba(0,0,0,0.9);">Lei</span><span
        class="word"
        style="position: absolute; left: 133.25px; top: 761.02px; transform-origin: top left; transform: rotate(-90.32deg); font-size: 13.12px; line-height: 16.40px; white-space: nowrap; color: rgba(0,0,0,0.9);">Federal</span><span
        class="word"
        style="position: absolute; left: 132.98px; top: 713.95px; transform-origin: top left; transform: rotate(-90.29deg); font-size: 13.27px; line-height: 16.59px; white-space: nowrap; color: rgba(0,0,0,0.9);">9394/96,</span><span
        class="word"
        style="position: absolute; left: 132.70px; top: 660.94px; transform-origin: top left; transform: rotate(-90.58deg); font-size: 13.30px; line-height: 16.63px; white-space: nowrap; color: rgba(0,0,0,0.9);">Artigo</span><span
        class="word"
        style="position: absolute; left: 132.32px; top: 623.52px; transform-origin: top left; transform: rotate(-90.61deg); font-size: 13.32px; line-height: 16.65px; white-space: nowrap; color: rgba(0,0,0,0.9);">35</span><span
        class="word"
        style="position: absolute; left: 132.13px; top: 606.00px; transform-origin: top left; transform: rotate(-90.62deg); font-size: 13.31px; line-height: 16.64px; white-space: nowrap; color: rgba(0,0,0,0.9);">e</span><span
        class="word"
        style="position: absolute; left: 132.03px; top: 595.23px; transform-origin: top left; transform: rotate(-90.40deg); font-size: 13.31px; line-height: 16.64px; white-space: nowrap; color: rgba(0,0,0,0.9);">36;</span><span
        class="word"
        style="position: absolute; left: 131.87px; top: 573.71px; transform-origin: top left; transform: rotate(-90.73deg); font-size: 13.30px; line-height: 16.62px; white-space: nowrap; color: rgba(0,0,0,0.9);">Resoluções</span><span
        class="word"
        style="position: absolute; left: 131.01px; top: 503.50px; transform-origin: top left; transform: rotate(-90.72deg); font-size: 13.16px; line-height: 16.45px; white-space: nowrap; color: rgba(0,0,0,0.9);">CNE/</span><span
        class="word"
        style="position: absolute; left: 130.56px; top: 469.32px; transform-origin: top left; transform: rotate(-91.13deg); font-size: 13.07px; line-height: 16.34px; white-space: nowrap; color: rgba(0,0,0,0.9);">CEB</span><span
        class="word"
        style="position: absolute; left: 129.91px; top: 421.04px; transform-origin: top left; transform: rotate(-90.74deg); font-size: 13.13px; line-height: 16.42px; white-space: nowrap; color: rgba(0,0,0,0.9);">03/1998</span><span
        class="word"
        style="position: absolute; left: 127.79px; top: 984.73px; transform-origin: top left; transform: rotate(-1.14deg); font-size: 13.98px; line-height: 17.47px; white-space: nowrap; color: rgba(0,0,0,0.9);">OBSERVAÇÕES:</span><span
        class="word"
        style="position: absolute; left: 154.18px; top: 1078.28px; transform-origin: top left; transform: rotate(-0.97deg); font-size: 11.61px; line-height: 14.51px; white-space: nowrap; color: rgba(0,0,0,0.9);">de</span><span
        class="word"
        style="position: absolute; left: 172.48px; top: 1078.00px; transform-origin: top left; transform: rotate(-1.13deg); font-size: 11.52px; line-height: 14.41px; white-space: nowrap; color: rgba(0,0,0,0.9);">Concluinte</span><span
        class="word"
        style="position: absolute; left: 238.04px; top: 1076.73px; transform-origin: top left; transform: rotate(-0.82deg); font-size: 11.75px; line-height: 14.69px; white-space: nowrap; color: rgba(0,0,0,0.9);">GDAE:</span><span
        class="word"
        style="position: absolute; left: 134.83px; top: 1094.35px; transform-origin: top left; transform: rotate(-1.40deg); font-size: 11.52px; line-height: 14.40px; white-space: nowrap; color: rgba(0,0,0,0.9);">Resolução</span><span
        class="word"
        style="position: absolute; left: 202.27px; top: 1092.70px; transform-origin: top left; transform: rotate(-1.35deg); font-size: 11.69px; line-height: 14.62px; white-space: nowrap; color: rgba(0,0,0,0.9);">SE</span><span
        class="word"
        style="position: absolute; left: 223.65px; top: 1092.25px; transform-origin: top left; transform: rotate(-1.02deg); font-size: 11.66px; line-height: 14.57px; white-space: nowrap; color: rgba(0,0,0,0.9);">108/02</span><span
        class="word"
        style="position: absolute; left: 492.59px; top: 1107.08px; transform-origin: top left; transform: rotate(-0.92deg); font-size: 12.77px; line-height: 15.97px; white-space: nowrap; color: rgba(0,0,0,0.9);">CERTIFICADO</span><span
        class="word"
        style="position: absolute; left: 143.56px; top: 1132.11px; transform-origin: top left; transform: rotate(-1.53deg); font-size: 13.85px; line-height: 17.31px; white-space: nowrap; color: rgba(0,0,0,0.9);">O</span><span
        class="word"
        style="position: absolute; left: 163.53px; top: 1131.57px; transform-origin: top left; transform: rotate(-1.49deg); font-size: 13.94px; line-height: 17.42px; white-space: nowrap; color: rgba(0,0,0,0.9);">Diretor</span><span
        class="word"
        style="position: absolute; left: 219.04px; top: 1130.14px; transform-origin: top left; transform: rotate(-1.34deg); font-size: 14.25px; line-height: 17.82px; white-space: nowrap; color: rgba(0,0,0,0.9);">do</span><span
        class="word"
        style="position: absolute; left: 242.84px; top: 1129.58px; transform-origin: top left; transform: rotate(-1.05deg); font-size: 14.46px; line-height: 18.07px; white-space: nowrap; color: rgba(0,0,0,0.9);">Colégio</span><span
        class="word"
        style="position: absolute; left: 304.52px; top: 1128.47px; transform-origin: top left; transform: rotate(-1.01deg); font-size: 14.54px; line-height: 18.17px; white-space: nowrap; color: rgba(0,0,0,0.9);">Lacordaire</span><span
        class="word"
        style="position: absolute; left: 387.07px; top: 1127.00px; transform-origin: top left; transform: rotate(-1.24deg); font-size: 14.28px; line-height: 17.85px; white-space: nowrap; color: rgba(0,0,0,0.9);">-</span><span
        class="word"
        style="position: absolute; left: 403.52px; top: 1126.64px; transform-origin: top left; transform: rotate(-1.20deg); font-size: 14.30px; line-height: 17.87px; white-space: nowrap; color: rgba(0,0,0,0.9);">Ensino</span><span
        class="word"
        style="position: absolute; left: 459.62px; top: 1125.50px; transform-origin: top left; transform: rotate(-0.95deg); font-size: 14.40px; line-height: 18.00px; white-space: nowrap; color: rgba(0,0,0,0.9);">Médio,</span><span
        class="word"
        style="position: absolute; left: 514.56px; top: 1124.57px; transform-origin: top left; transform: rotate(-0.99deg); font-size: 14.55px; line-height: 18.19px; white-space: nowrap; color: rgba(0,0,0,0.9);">CERTIFICA,</span><span
        class="word"
        style="position: absolute; left: 611.79px; top: 1122.91px; transform-origin: top left; transform: rotate(-1.18deg); font-size: 14.35px; line-height: 17.93px; white-space: nowrap; color: rgba(0,0,0,0.9);">nos</span><span
        class="word"
        style="position: absolute; left: 643.51px; top: 1122.23px; transform-origin: top left; transform: rotate(-1.41deg); font-size: 14.32px; line-height: 17.89px; white-space: nowrap; color: rgba(0,0,0,0.9);">termos</span><span
        class="word"
        style="position: absolute; left: 700.20px; top: 1120.85px; transform-origin: top left; transform: rotate(-1.25deg); font-size: 14.34px; line-height: 17.92px; white-space: nowrap; color: rgba(0,0,0,0.9);">do</span><span
        class="word"
        style="position: absolute; left: 724.28px; top: 1120.33px; transform-origin: top left; transform: rotate(-1.51deg); font-size: 14.30px; line-height: 17.87px; white-space: nowrap; color: rgba(0,0,0,0.9);">Inciso</span><span
        class="word"
        style="position: absolute; left: 771.57px; top: 1119.07px; transform-origin: top left; transform: rotate(-1.70deg); font-size: 14.34px; line-height: 17.92px; white-space: nowrap; color: rgba(0,0,0,0.9);">VII,</span><span
        class="word"
        style="position: absolute; left: 802.70px; top: 1118.15px; transform-origin: top left; transform: rotate(-1.43deg); font-size: 14.42px; line-height: 18.02px; white-space: nowrap; color: rgba(0,0,0,0.9);">Artigo</span><span
        class="word"
        style="position: absolute; left: 849.99px; top: 1116.97px; transform-origin: top left; transform: rotate(-1.36deg); font-size: 14.60px; line-height: 18.24px; white-space: nowrap; color: rgba(0,0,0,0.9);">24</span><span
        class="word"
        style="position: absolute; left: 874.37px; top: 1116.41px; transform-origin: top left; transform: rotate(-1.23deg); font-size: 14.57px; line-height: 18.21px; white-space: nowrap; color: rgba(0,0,0,0.9);">da</span><span
        class="word"
        style="position: absolute; left: 899.04px; top: 1115.88px; transform-origin: top left; transform: rotate(-1.22deg); font-size: 14.44px; line-height: 18.05px; white-space: nowrap; color: rgba(0,0,0,0.9);">Lei</span><span
        class="word"
        style="position: absolute; left: 926.36px; top: 1115.29px; transform-origin: top left; transform: rotate(-1.37deg); font-size: 14.29px; line-height: 17.87px; white-space: nowrap; color: rgba(0,0,0,0.9);">Federal</span><span
        class="word"
        style="position: absolute; left: 130.64px; top: 1151.38px; transform-origin: top left; transform: rotate(-1.40deg); font-size: 14.11px; line-height: 17.64px; white-space: nowrap; color: rgba(0,0,0,0.9);">9394/96,</span><span
        class="word"
        style="position: absolute; left: 200.57px; top: 1149.67px; transform-origin: top left; transform: rotate(-1.40deg); font-size: 14.51px; line-height: 18.14px; white-space: nowrap; color: rgba(0,0,0,0.9);">que</span><span
        class="word"
        style="position: absolute; left: 233.91px; top: 1148.87px; transform-origin: top left; transform: rotate(-1.24deg); font-size: 14.51px; line-height: 18.14px; white-space: nowrap; color: rgba(0,0,0,0.9);">Maria</span><span
        class="word"
        style="position: absolute; left: 279.94px; top: 1147.88px; transform-origin: top left; transform: rotate(-1.23deg); font-size: 14.51px; line-height: 18.14px; white-space: nowrap; color: rgba(0,0,0,0.9);">Eduarda</span><span
        class="word"
        style="position: absolute; left: 347.80px; top: 1146.42px; transform-origin: top left; transform: rotate(-1.17deg); font-size: 14.52px; line-height: 18.15px; white-space: nowrap; color: rgba(0,0,0,0.9);">Fonseca</span><span
        class="word"
        style="position: absolute; left: 415.67px; top: 1145.04px; transform-origin: top left; transform: rotate(-1.06deg); font-size: 14.45px; line-height: 18.06px; white-space: nowrap; color: rgba(0,0,0,0.9);">Canuto,</span><span
        class="word"
        style="position: absolute; left: 478.52px; top: 1143.88px; transform-origin: top left; transform: rotate(-1.04deg); font-size: 14.65px; line-height: 18.32px; white-space: nowrap; color: rgba(0,0,0,0.9);">R.G</span><span
        class="word"
        style="position: absolute; left: 504.78px; top: 1143.40px; transform-origin: top left; transform: rotate(-0.97deg); font-size: 14.72px; line-height: 18.40px; white-space: nowrap; color: rgba(0,0,0,0.9);">.:</span><span
        class="word"
        style="position: absolute; left: 624.00px; top: 1141.23px; transform-origin: top left; transform: rotate(-1.31deg); font-size: 14.37px; line-height: 17.96px; white-space: nowrap; color: rgba(0,0,0,0.9);">concluiu</span><span
        class="word"
        style="position: absolute; left: 689.21px; top: 1139.74px; transform-origin: top left; transform: rotate(-1.30deg); font-size: 14.41px; line-height: 18.02px; white-space: nowrap; color: rgba(0,0,0,0.9);">o</span><span
        class="word"
        style="position: absolute; left: 703.66px; top: 1139.41px; transform-origin: top left; transform: rotate(-1.31deg); font-size: 14.40px; line-height: 18.00px; white-space: nowrap; color: rgba(0,0,0,0.9);">3º</span><span
        class="word"
        style="position: absolute; left: 723.43px; top: 1138.95px; transform-origin: top left; transform: rotate(-1.43deg); font-size: 14.38px; line-height: 17.97px; white-space: nowrap; color: rgba(0,0,0,0.9);">ano</span><span
        class="word"
        style="position: absolute; left: 755.59px; top: 1138.14px; transform-origin: top left; transform: rotate(-1.54deg); font-size: 14.36px; line-height: 17.95px; white-space: nowrap; color: rgba(0,0,0,0.9);">do</span><span
        class="word"
        style="position: absolute; left: 779.49px; top: 1137.50px; transform-origin: top left; transform: rotate(-1.38deg); font-size: 14.36px; line-height: 17.95px; white-space: nowrap; color: rgba(0,0,0,0.9);">Ensino</span><span
        class="word"
        style="position: absolute; left: 834.37px; top: 1136.19px; transform-origin: top left; transform: rotate(-1.32deg); font-size: 14.40px; line-height: 18.00px; white-space: nowrap; color: rgba(0,0,0,0.9);">Médio,</span><span
        class="word"
        style="position: absolute; left: 887.77px; top: 1134.96px; transform-origin: top left; transform: rotate(-1.37deg); font-size: 14.33px; line-height: 17.91px; white-space: nowrap; color: rgba(0,0,0,0.9);">no</span><span
        class="word"
        style="position: absolute; left: 910.79px; top: 1134.41px; transform-origin: top left; transform: rotate(-1.40deg); font-size: 14.26px; line-height: 17.82px; white-space: nowrap; color: rgba(0,0,0,0.9);">ano</span><span
        class="word"
        style="position: absolute; left: 942.65px; top: 1133.63px; transform-origin: top left; transform: rotate(-1.42deg); font-size: 14.15px; line-height: 17.69px; white-space: nowrap; color: rgba(0,0,0,0.9);">letivo</span><span
        class="word"
        style="position: absolute; left: 131.12px; top: 1170.30px; transform-origin: top left; transform: rotate(-1.47deg); font-size: 13.87px; line-height: 17.34px; white-space: nowrap; color: rgba(0,0,0,0.9);">de</span><span
        class="word"
        style="position: absolute; left: 154.46px; top: 1169.71px; transform-origin: top left; transform: rotate(-1.22deg); font-size: 14.09px; line-height: 17.62px; white-space: nowrap; color: rgba(0,0,0,0.9);">2015,estando</span><span
        class="word"
        style="position: absolute; left: 259.36px; top: 1167.50px; transform-origin: top left; transform: rotate(-1.22deg); font-size: 14.68px; line-height: 18.35px; white-space: nowrap; color: rgba(0,0,0,0.9);">apta</span><span
        class="word"
        style="position: absolute; left: 295.70px; top: 1166.71px; transform-origin: top left; transform: rotate(-1.20deg); font-size: 14.78px; line-height: 18.47px; white-space: nowrap; color: rgba(0,0,0,0.9);">ao</span><span
        class="word"
        style="position: absolute; left: 319.34px; top: 1166.23px; transform-origin: top left; transform: rotate(-0.99deg); font-size: 14.79px; line-height: 18.49px; white-space: nowrap; color: rgba(0,0,0,0.9);">prosseguimento</span><span
        class="word"
        style="position: absolute; left: 440.79px; top: 1164.14px; transform-origin: top left; transform: rotate(-1.19deg); font-size: 14.38px; line-height: 17.97px; white-space: nowrap; color: rgba(0,0,0,0.9);">de</span><span
        class="word"
        style="position: absolute; left: 463.54px; top: 1163.67px; transform-origin: top left; transform: rotate(-0.71deg); font-size: 14.31px; line-height: 17.89px; white-space: nowrap; color: rgba(0,0,0,0.9);">estudos.</span><span
        class="word"
        style="position: absolute; left: 197.79px; top: 1224.57px; transform-origin: top left; transform: rotate(-1.03deg); font-size: 12.53px; line-height: 15.67px; white-space: nowrap; color: rgba(0,0,0,0.9);">13/04/2016</span><span
        class="word"
        style="position: absolute; left: 221.96px; top: 1242.94px; transform-origin: top left; transform: rotate(-0.66deg); font-size: 12.30px; line-height: 15.37px; white-space: nowrap; color: rgba(0,0,0,0.9);">DATA</span><span
        class="word"
        style="position: absolute; left: 478.22px; top: 1211.47px; transform-origin: top left; transform: rotate(-0.61deg); font-size: 17.20px; line-height: 21.51px; white-space: nowrap; color: rgba(0,0,0,0.9);">Ruepz</span><span
        class="word"
        style="position: absolute; left: 464.64px; top: 1238.21px; transform-origin: top left; transform: rotate(-0.84deg); font-size: 12.36px; line-height: 15.45px; white-space: nowrap; color: rgba(0,0,0,0.9);">Renata</span><span
        class="word"
        style="position: absolute; left: 523.20px; top: 1237.35px; transform-origin: top left; transform: rotate(-0.83deg); font-size: 12.42px; line-height: 15.53px; white-space: nowrap; color: rgba(0,0,0,0.9);">Cristina</span><span
        class="word"
        style="position: absolute; left: 583.79px; top: 1236.57px; transform-origin: top left; transform: rotate(-0.87deg); font-size: 12.35px; line-height: 15.44px; white-space: nowrap; color: rgba(0,0,0,0.9);">Cruz</span><span
        class="word"
        style="position: absolute; left: 504.47px; top: 1256.47px; transform-origin: top left; transform: rotate(-0.35deg); font-size: 12.42px; line-height: 15.52px; white-space: nowrap; color: rgba(0,0,0,0.9);">Secretária</span><span
        class="word"
        style="position: absolute; left: 471.18px; top: 1275.46px; transform-origin: top left; transform: rotate(-0.61deg); font-size: 12.73px; line-height: 15.92px; white-space: nowrap; color: rgba(0,0,0,0.9);">R.G</span><span
        class="word"
        style="position: absolute; left: 499.32px; top: 1275.15px; transform-origin: top left; transform: rotate(-0.65deg); font-size: 12.87px; line-height: 16.09px; white-space: nowrap; color: rgba(0,0,0,0.9);">.:</span><span
        class="word"
        style="position: absolute; left: 514.45px; top: 1274.97px; transform-origin: top left; transform: rotate(-1.02deg); font-size: 12.73px; line-height: 15.91px; white-space: nowrap; color: rgba(0,0,0,0.9);">29.859.092-X</span><span
        class="word"
        style="position: absolute; left: 735.56px; top: 1231.93px; transform-origin: top left; transform: rotate(-1.32deg); font-size: 13.53px; line-height: 16.92px; white-space: nowrap; color: rgba(0,0,0,0.9);">Christinhe</span><span
        class="word"
        style="position: absolute; left: 814.48px; top: 1230.17px; transform-origin: top left; transform: rotate(-0.93deg); font-size: 13.92px; line-height: 17.40px; white-space: nowrap; color: rgba(0,0,0,0.9);">Sant'Anna</span><span
        class="word"
        style="position: absolute; left: 894.26px; top: 1228.76px; transform-origin: top left; transform: rotate(-1.13deg); font-size: 13.93px; line-height: 17.41px; white-space: nowrap; color: rgba(0,0,0,0.9);">Magalhães</span><span
        class="word"
        style="position: absolute; left: 826.27px; top: 1249.54px; transform-origin: top left; transform: rotate(-0.44deg); font-size: 12.30px; line-height: 15.37px; white-space: nowrap; color: rgba(0,0,0,0.9);">Diretora</span><span
        class="word"
        style="position: absolute; left: 785.90px; top: 1269.07px; transform-origin: top left; transform: rotate(-0.93deg); font-size: 12.93px; line-height: 16.16px; white-space: nowrap; color: rgba(0,0,0,0.9);">R.G</span><span
        class="word"
        style="position: absolute; left: 813.90px; top: 1268.60px; transform-origin: top left; transform: rotate(-1.31deg); font-size: 13.27px; line-height: 16.58px; white-space: nowrap; color: rgba(0,0,0,0.9);">.:</span><span
        class="word"
        style="position: absolute; left: 829.79px; top: 1268.25px; transform-origin: top left; transform: rotate(-1.41deg); font-size: 13.19px; line-height: 16.49px; white-space: nowrap; color: rgba(0,0,0,0.9);">15.652.291-3</span><span
        class="word"
        style="position: absolute; left: 960.05px; top: 1412.43px; transform-origin: top left; transform: rotate(-0.51deg); font-size: 6.52px; line-height: 8.15px; white-space: nowrap; color: rgba(0,0,0,0.9);">MADE</span><span
        class="word"
        style="position: absolute; left: 986.84px; top: 1412.20px; transform-origin: top left; transform: rotate(0.21deg); font-size: 6.81px; line-height: 8.51px; white-space: nowrap; color: rgba(0,0,0,0.9);">WITH</span><span
        class="word"
        style="position: absolute; left: 961.17px; top: 1423.02px; transform-origin: top left; transform: rotate(0.62deg); font-size: 13.57px; line-height: 16.96px; white-space: nowrap; color: rgba(0,0,0,0.9);">Scanner</span><span
        class="word"
        style="position: absolute; left: 961.38px; top: 1441.51px; transform-origin: top left; transform: rotate(1.56deg); font-size: 14.26px; line-height: 17.82px; white-space: nowrap; color: rgba(0,0,0,0.9);">App</span>
</div>
</body>
</html>"""]
        self.output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # def tearDown(self):
    #     """
    #     Clean up the test files after each test.
    #     """
    #     if os.path.exists(self.output_pdf_path):
    #         os.remove(self.output_pdf_path)

    def get_pdf_text(self, pdf_path):
        """
        Helper function to extract text from a PDF.
        """
        try:
            with open(pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except FileNotFoundError:
            self.fail(f"PDF file not found at {pdf_path}. Please place your expected PDF here.")
        except Exception as e:
            self.fail(f"An error occurred while reading the PDF: {e}")
        return ""

    @patch('app.services.html_to_pdf_converter.async_playwright')
    def test_convert_success_mocked(self, mock_async_playwright):
        async def run_test():
            # Mock async context manager for async_playwright()
            mock_playwright_cm = AsyncMock()
            mock_async_playwright.return_value = mock_playwright_cm

            # The playwright instance yielded by __aenter__
            mock_playwright = MagicMock()
            mock_playwright_cm.__aenter__.return_value = mock_playwright

            # Mock browser and page with async methods
            mock_browser = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_browser.new_page = AsyncMock(return_value=mock_page)

            # Mock async methods on page
            mock_page.set_content = AsyncMock()
            mock_page.emulate_media = AsyncMock()
            mock_page.pdf = AsyncMock(return_value=b'%PDF-1.4 fake pdf content')
            mock_page.close = AsyncMock()

            # Mock async browser.close()
            mock_browser.close = AsyncMock()

            # Use a list of HTML pages as input
            html_pages = ['<html>Page 1</html>', '<html>Page 2</html>']
            converter = HtmlToPdfConverter(html_pages)

            # Await the async convert_to_pdf method
            output_path = await converter.convert_to_pdf(base_name="test.pdf")

            # Assertions that async methods were awaited properly
            mock_playwright.chromium.launch.assert_awaited_once()
            mock_browser.new_page.assert_awaited()
            # We expect set_content and pdf to be called once per page
            self.assertEqual(mock_page.set_content.await_count, len(html_pages))
            self.assertEqual(mock_page.pdf.await_count, len(html_pages))
            self.assertEqual(mock_page.emulate_media.await_count, len(html_pages))
            self.assertEqual(mock_page.close.await_count, len(html_pages))
            mock_browser.close.assert_awaited_once()

            # Check the output path ends with .pdf
            self.assertTrue(output_path.endswith('.pdf'))

    def test_generated_pdf_content(self):
        """
        Tests that the content of the generated PDF matches the expected content.

        This test is an integration test and requires Playwright to be installed.
        It generates a PDF and then compares its text content to a
        known-good PDF provided by the user.

        NOTE: Before running this test, you must place your pre-generated PDF
        file in the same directory as this test file, and name it 'expected_pdf_output.pdf'.
        """
        # Generate the actual PDF file
        converter = HtmlToPdfConverter(self.html_content)
        converter.convert_to_pdf()

        # Check if the output file was created
        self.assertTrue(os.path.exists(self.output_pdf_path))
        self.assertTrue(os.path.exists(self.expected_pdf_path))

        # Extract and compare the text content of the two PDFs
        expected_text = self.get_pdf_text(self.expected_pdf_path)
        actual_text = self.get_pdf_text(self.output_pdf_path)

        # Clean up any whitespace differences
        self.assertEqual(expected_text.strip(), actual_text.strip())

    @patch('app.services.html_to_pdf_converter.async_playwright', side_effect=Exception("Test Error"))
    def test_convert_exception_handling(self, mock_async_playwright):
        async def run_test():
            with self.assertRaises(RuntimeError) as context:
                await HtmlToPdfConverter(self.html_pages).convert_to_pdf()

            self.assertIn("Error during conversion:", str(context.exception))
            self.assertIn("Test Error", str(context.exception))



if __name__ == '__main__':
    unittest.main()
