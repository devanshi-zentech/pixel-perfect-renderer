"""
Example Usage
-------------

This CLI tool converts Azure Document Intelligence JSON into HTML.

# From the project root (recommended way to run it):

# Example 1: Pixel-perfect rendering at default 96 DPI, using Arial
python -m app.services.render_doc --input <path-to-json> --out output_html_files --mode words --dpi 96 --font "Arial, sans-serif"

# Example 2: Semantic rendering (lines-based), higher resolution
python -m app.services.render_doc --input <path-to-json> --out output_html_files --mode lines --dpi 150 --font "Times New Roman, serif"

Arguments
---------
--mode
    "words"  → Pixel-perfect layout (preserves each word's position, good for visual fidelity).
    "lines"  → Groups words into lines (cleaner, semantic HTML).

--dpi
    Dots-per-inch (resolution hint). Common values:
    - 96 (default, typical web display)
    - 150 (higher density)
    - 300 (print quality)

--font
    CSS font stack for rendering text. Example values:
    - "Arial, sans-serif"
    - "Times New Roman, serif"
    - "Roboto, Helvetica, sans-serif"
"""

# --- Core Python Imports ---
import argparse
import json
import os
import sys
from pathlib import Path

# --- Add Project Root to sys.path (only needed if not using -m execution) ---
sys.path.insert(0, str(Path(__file__).resolve().parent))

# --- Custom Application Imports ---
from app.services.document_converter import DocumentConverter
from app.models.schemas import RenderOptions
from app.core import constants


class RenderDocCLI:
    """CLI wrapper for rendering Azure Document Intelligence JSON into HTML."""

    def __init__(self):
        self.args = self._parse_args()
        self.converter = DocumentConverter()

    def _parse_args(self):
        parser = argparse.ArgumentParser(
            description="Render Azure Document Intelligence JSON to HTML pages."
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
            help="Path to the output directory to save the generated HTML files."
        )
        parser.add_argument(
            "--mode",
            type=str,
            default=constants.DEFAULT_RENDER_MODE,
            choices=["words", "lines"],
            help="Rendering mode: 'words' for a pixel-perfect visual layout, "
                 "'lines' for a clean, semantic HTML document."
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

    def run(self):
        azure_json_data = self._load_input_file()
        self._prepare_output_dir()

        print(constants.CLI_INIT_MSG.format(mode=self.args.mode))
        render_options = RenderOptions(
            dpi=self.args.dpi,
            font_stack=self.args.font,
            mode=self.args.mode
        )

        html_pages = self.converter.to_html_pages(azure_json_data, render_options)

        if not html_pages:
            print(constants.CLI_NO_PAGES_WARNING)
            return

        for i, page_html in enumerate(html_pages):
            file_path = os.path.join(self.args.out, f"page_{i + 1}.html")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(page_html)
                print(constants.CLI_SAVE_SUCCESS.format(file_path=file_path))
            except IOError as e:
                print(constants.CLI_SAVE_ERROR.format(file_path=file_path, error=e))

        print(constants.CLI_RENDER_COMPLETE.format(count=len(html_pages), out_dir=self.args.out))


if __name__ == "__main__":
    cli = RenderDocCLI()
    cli.run()