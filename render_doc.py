"""
Example Usage
-------------

This CLI tool converts Azure Document Intelligence JSON into HTML.

# Example 1: Pixel-perfect rendering at default 96 DPI, using Arial
python render.py --input sample.json --out output_dir --mode word --dpi 96 --font "Arial, sans-serif"

# Example 2: Semantic rendering (lines-based), higher resolution
python render.py --input sample.json --out output_dir --mode lines --dpi 150 --font "Times New Roman, serif"

Arguments
---------
--mode
    "word"      → Pixel-perfect layout (preserves each word's position, good for visual fidelity).
    "lines"     → Groups words into lines (cleaner, semantic HTML).

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

# --- Add Project Root to sys.path ---
# This allows the script to import modules from the 'app' directory,
# making it a portable part of your project.
sys.path.insert(0, str(Path(__file__).resolve().parent))

# --- Custom Application Imports ---
from app.services.document_converter import DocumentConverter
from app.models.schemas import RenderOptions
from app.core import constants

def main():
    """
    A command-line tool to render Azure Document Intelligence JSON files into
    structured or pixel-perfect HTML pages.
    """
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
    # --- New 'mode' Argument ---
    parser.add_argument(
        "--mode",
        type=str,
        default=constants.DEFAULT_RENDER_MODE,
        choices=["word", "paragraph"],
        help="Rendering mode: 'word' for a pixel-perfect visual layout, "
             "'paragraph' for a clean, semantic HTML document."
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=constants.DEFAULT_DPI,
        help=f"Dots per inch for rendering (default: {constants.DEFAULT_DPI}). "
             "Note: This is for future use."
    )
    parser.add_argument(
        "--font",
        type=str,
        default=constants.DEFAULT_FONT_STACK,
        help=f"CSS font stack to use (default: '{constants.DEFAULT_FONT_STACK}')."
    )

    args = parser.parse_args()

    # --- 1. Read and Validate Input File ---
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            azure_json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at '{args.input}'")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{args.input}'. Please check the file format.")
        sys.exit(1)

    # --- 2. Create Output Directory ---
    try:
        os.makedirs(args.out, exist_ok=True)
    except OSError as e:
        print(f"Error: Could not create output directory at '{args.out}': {e}")
        sys.exit(1)

    # --- 3. Initialize Converter and Render HTML ---
    print(f"Initializing document converter in '{args.mode}' mode...")
    converter = DocumentConverter()
    
    # Bundle CLI arguments into a Pydantic model for clean passing.
    render_options = RenderOptions(
        dpi=args.dpi,
        font_stack=args.font,
        mode=args.mode
    )
    
    html_pages = converter.to_html_pages(azure_json_data, render_options)

    if not html_pages:
        print("Warning: No pages were rendered. The input JSON might be empty or invalid.")
        return

    # --- 4. Save HTML Files ---
    for i, page_html in enumerate(html_pages):
        file_path = os.path.join(args.out, f"page_{i + 1}.html")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(page_html)
            print(f"Successfully saved {file_path}")
        except IOError as e:
            print(f"Error: Could not write to file {file_path}: {e}")

    print(f"\n✅ Rendering complete. {len(html_pages)} pages saved in '{args.out}'.")

if __name__ == "__main__":
    main()
