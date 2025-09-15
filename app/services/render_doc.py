"""
Example Usage
-------------

This CLI tool converts an Azure Document Intelligence JSON file into both a
set of HTML files (one per page) and a single, combined PDF document.

# From the project root (recommended way to run it):

# Example 1: Pixel-perfect rendering at default 96 DPI, using Arial
python -m app.services.render_doc --input <path-to-json> --out output_files --mode words --dpi 96 --font "Arial, sans-serif"

# Example 2: Higher resolution rendering
python -m app.services.render_doc --input <path-to-json> --out output_files --mode words --dpi 150 --font "Times New Roman, serif"

Arguments
---------
--input
    Path to the input Azure Document Intelligence JSON file.

--out
    Path to the output directory where the generated HTML and PDF files will be saved.

--mode
    "words" --> Pixel-perfect layout (preserves each word's position, good for visual fidelity).

--dpi
    Dots-per-inch (resolution hint). Common values:
    - 96 (default, typical web display)
    - 150 (higher density)
    - 300 (print quality)

--font
    CSS font stack for rendering text. Example values:
    - "Arial, sans-serif"
    - "Times New Roman, serif"
"""

# --- Core Python Imports ---
import argparse
import json
import os
import sys
from pathlib import Path
import asyncio

# --- Add Project Root to sys.path (only needed if not using -m execution) ---
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# --- Custom Application Imports ---
from app.services.document_converter import DocumentConverter
from app.services.html_to_pdf_converter import HtmlToPdfConverter
from app.models.schemas import RenderOptions
from app.core import constants
from app.core.browser_manager import browser_manager


class RenderDocCLI:
    """CLI wrapper for rendering Azure Document Intelligence JSON into HTML and a PDF."""

    def __init__(self):
        self.args = self._parse_args()
        self.converter = DocumentConverter()

    def _parse_args(self):
        parser = argparse.ArgumentParser(
            description="Render Azure Document Intelligence JSON to HTML pages and a single PDF."
        )
        parser.add_argument(
            "--input",
            type=str,
            required=True,
            help="Path to the input Azure JSON file."
        )
        parser.add_argument(
            "--out",
            type=str,
            required=True,
            help="Path to the output directory to save the generated files."
        )
        parser.add_argument(
            "--mode",
            type=str,
            default=constants.DEFAULT_RENDER_MODE,
            choices=["words", "lines"],
            help="Rendering mode: 'words' for a pixel-perfect visual layout."
        )
        parser.add_argument(
            "--dpi",
            type=int,
            default=constants.DEFAULT_DPI,
            help=f"Dots per inch for rendering (default: {constants.DEFAULT_DPI})."
        )
        parser.add_argument(
            "--font",
            type=str,
            default=constants.DEFAULT_FONT_STACK,
            help=f"CSS font stack to use (default: '{constants.DEFAULT_FONT_STACK}')."
        )
        return parser.parse_args()

    def _load_input_file(self):
        try:
            with open(self.args.input, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(constants.CLI_INPUT_FILE_NOT_FOUND.format(input_path=self.args.input))
            sys.exit(1)
        except json.JSONDecodeError:
            print(constants.CLI_INPUT_FILE_INVALID.format(input_path=self.args.input))
            sys.exit(1)

    def _prepare_output_dir(self):
        try:
            os.makedirs(self.args.out, exist_ok=True)
        except OSError as e:
            print(constants.CLI_OUTPUT_DIR_ERROR.format(out_dir=self.args.out, error=e))
            sys.exit(1)

    async def _run_async(self):
        azure_json_data = self._load_input_file()
        self._prepare_output_dir()
        
        # Get the base name of the input file to use for output files
        input_basename = Path(self.args.input).stem

        print(constants.CLI_INIT_MSG.format(mode=self.args.mode))
        render_options = RenderOptions(
            dpi=self.args.dpi,
            font_stack=self.args.font,
            mode=self.args.mode
        )

        # 1. Convert JSON to a list of HTML pages with their dimensions
        html_pages_data = self.converter.to_html_pages(azure_json_data, render_options)

        if not html_pages_data:
            print(constants.CLI_NO_PAGES_WARNING)
            return

        # 2. Save each page as a separate HTML file
        for i, page_data in enumerate(html_pages_data):
            html_file_path = os.path.join(self.args.out, f"{input_basename}_page_{i + 1}.html")
            try:
                with open(html_file_path, 'w', encoding='utf-8') as f:
                    f.write(page_data['html'])
                print(constants.CLI_SAVE_SUCCESS.format(file_path=html_file_path))
            except IOError as e:
                print(constants.CLI_SAVE_ERROR.format(file_path=html_file_path, error=e))

        # 3. Convert all generated HTML pages into a single PDF
        print("\nGenerating PDF document...")
        pdf_converter = HtmlToPdfConverter(html_pages_data)
        pdf_bytes = await pdf_converter.convert_to_pdf()
        
        pdf_file_path = os.path.join(self.args.out, f"{input_basename}.pdf")
        try:
            with open(pdf_file_path, 'wb') as f:
                f.write(pdf_bytes)
            print(constants.CLI_SAVE_SUCCESS.format(file_path=pdf_file_path))
        except IOError as e:
            print(constants.CLI_SAVE_ERROR.format(file_path=pdf_file_path, error=e))

        # 4. Clean up the browser instance
        await browser_manager.stop()

        print(constants.CLI_RENDER_COMPLETE.format(count=len(html_pages_data), out_dir=self.args.out))

    def run(self):
        asyncio.run(self._run_async())


if __name__ == "__main__":
    cli = RenderDocCLI()
    cli.run()