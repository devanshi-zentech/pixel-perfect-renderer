# --- Core Python Imports ---
from typing import Any, Dict, List

# --- Custom Imports ---
# Imports constants and the new, more advanced rendering helper functions.
from app.core import constants
from app.services.html_rendering_helpers import render_word, render_table_with_words
from app.models.schemas import RenderOptions
class DocumentConverter:
    """
    Converts a Document Intelligence JSON response into one or more
    standalone HTML pages that visually represent the original document with
    pixel-perfect positioning of words and tables.
    """

    def to_html_pages(self, data: Dict[str, Any],options: RenderOptions) -> List[str]:
        """
        Generates a list of full, standalone HTML strings, one for each page
        in the document analysis result.
        """
        html_pages = []
        dpi = options.dpi or constants.DEFAULT_DPI
        font_stack = options.font_stack or constants.DEFAULT_FONT_STACK

        for page_idx, page in enumerate(data.get("pages", [])):
            page_number = page.get("pageNumber", page_idx + 1)
            page_angle = page.get("angle", constants.DEFAULT_PAGE_ANGLE)

            # Calculate the scaling factor to fit the document into a standard width.
            page_height_scaled = page.get("height", constants.DEFAULT_PAGE_HEIGHT) * dpi
            page_width_scaled = page.get("width", constants.DEFAULT_PAGE_WIDTH)*dpi

            # Create a fast lookup map for words.
            word_map = {
                word["span"]["offset"]: word
                for word in page.get("words", [])
                if "span" in word and "offset" in word["span"]
            }
            
            rendered_spans = set()
            page_elements_html = []

            # Step 1: Render all tables on the current page.
            for table in data.get("tables", []):
                # --- FIX: Pass 'page_number' as a required argument. ---
                table_html = render_table_with_words(
                    table, page_number, dpi, word_map, rendered_spans
                )
                if table_html:
                    page_elements_html.append(table_html)

            # Step 2: Render all remaining words not part of a table.
            for word in page.get("words", []):
                span_offset = word.get("span", {}).get("offset")
                if span_offset is not None and span_offset in rendered_spans:
                    continue
                
                word_html = render_word(word, dpi)
                if word_html:
                    page_elements_html.append(word_html)

            # Step 3: Assemble the final HTML for the page.
            page_container = (
                f'<div class="page" style="width:{page_width_scaled:.2f}px; '
                f'height:{page_height_scaled:.2f}px; transform:rotate({page_angle}deg);">'
                f'{"".join(page_elements_html)}</div>'
            )

            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page {page_number}</title>
    <style>{constants.HTML_VISUALIZATION_CSS.format(font_style = font_stack)}</style>
</head>
<body>
    {page_container}
</body>
</html>""".strip()
            
            final_html = full_html.replace("\n"," ")
            
            html_pages.append(final_html)

        return html_pages

