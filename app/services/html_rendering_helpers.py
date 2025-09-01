# --- Core Python Imports ---
import math
from typing import Dict, List, Set, Any, Tuple

# --- Custom Imports ---
# Imports constants for default values.
from app.core import constants

def render_word(word: Dict[str, Any], scale: float) -> str:
    """
    Renders a single word as an absolutely positioned HTML <span> element
    based on its polygon coordinates, scale, and angle. It filters out
    low-confidence words and potential watermarks.
    """
    polygon = word.get("polygon", [])
    if not polygon or len(polygon) < 8 or word.get("confidence", 0) < 0.4:
        return ""

    # Calculate word position from the top-left corner of the polygon.
    left, top = polygon[0] * scale, polygon[1] * scale

    # Calculate angle and height for precise rotation and font sizing.
    p1_x, p1_y = polygon[0], polygon[1]
    p2_x, p2_y = polygon[2], polygon[3]
    p4_x, p4_y = polygon[6], polygon[7]

    angle_deg = math.degrees(math.atan2(p2_y - p1_y, p2_x - p1_x))
    word_height = math.sqrt((p4_x - p1_x) ** 2 + (p4_y - p1_y) ** 2) * scale
    font_size = word_height * 0.8  # Approximate font size from bounding box height.

    # Filter out words that are likely part of a large background watermark.
    if font_size > 40:
        return ""

    # Sanitize content to prevent HTML injection.
    sanitized_content = str(word.get("content", "")).replace("<", "&lt;").replace(">", "&gt;")

    style = (
        f'position: absolute; left: {left:.2f}px; top: {top:.2f}px; '
        f'transform-origin: top left; transform: rotate({angle_deg:.2f}deg); '
        f'font-size: {font_size:.2f}px; line-height: {word_height:.2f}px; '
        f'white-space: nowrap; color: rgba(0,0,0,0.9);'
    )

    return f'<span class="word" style="{style}">{sanitized_content}</span>'

def render_table_with_words(
    table: Dict[str, Any],
    page_number: int,
    scale: float,
    word_map: Dict[int, Dict[str, Any]],
    rendered_spans: Set[int],
) -> str:
    """
    Renders an HTML table with absolutely positioned words inside each cell,
    respecting cell polygons, rotation, and row/column spans.
    """
    # Ensure the table belongs to the current page.
    if not table.get("boundingRegions") or table["boundingRegions"][0].get("pageNumber") != page_number:
        return ""

    polygon = table["boundingRegions"][0].get("polygon", [])
    if not polygon:
        return ""

    # Determine the table's overall position on the page.
    x_coords = polygon[0::2]
    y_coords = polygon[1::2]
    left = min(x_coords) * scale
    top = min(y_coords) * scale
    width = (max(x_coords) - min(x_coords)) * scale

    # Start building the table HTML.
    table_html_parts = [
        f'<div class="table-container" style="position: absolute; left: {left:.2f}px; top: {top:.2f}px; width: {width:.2f}px;"><table border="1">'
    ]

    # Create a grid to correctly handle cells with row/column spans.
    grid = [[None for _ in range(table["columnCount"])] for _ in range(table["rowCount"])]

    for cell in table.get("cells", []):
        row_idx, col_idx = cell.get("rowIndex", 0), cell.get("columnIndex", 0)
        
        # Skip this grid position if it's already occupied by a previous cell's span.
        if grid[row_idx][col_idx] is not None:
            continue
            
        row_span, col_span = cell.get("rowSpan", 1), cell.get("columnSpan", 1)
        
        # Aggregate the content of the cell from individual words.
        cell_content = cell.get("content", "")
        for span in cell.get("spans", []):
            for i in range(span["offset"], span["offset"] + span["length"]):
                rendered_spans.add(i) # Mark words as rendered.
        
        # Determine cell tag (header or data) and calculate its dimensions.
        tag = "th" if cell.get("kind") in ["columnHeader", "rowHeader"] else "td"
        cell_poly = cell.get("boundingRegions", [{}])[0].get("polygon", [])
        cell_style = ""
        if cell_poly:
            cell_x = cell_poly[0::2]
            cell_y = cell_poly[1::2]
            cell_width = (max(cell_x) - min(cell_x)) * scale
            cell_height = (max(cell_y) - min(cell_y)) * scale
            cell_style = f'style="width:{cell_width:.2f}px; height:{cell_height:.2f}px;"'

        # Place the cell in the grid.
        grid[row_idx][col_idx] = f'<{tag} {cell_style} rowspan="{row_span}" colspan="{col_span}">{cell_content}</{tag}>'

        # Mark all grid cells covered by this cell's span as "occupied".
        for r in range(row_span):
            for c in range(col_span):
                if r == 0 and c == 0: continue
                if (row_idx + r < len(grid)) and (col_idx + c < len(grid[0])):
                    grid[row_idx + r][col_idx + c] = "occupied"
    
    # Convert the grid into final HTML table rows.
    for row in grid:
        table_html_parts.append("<tr>")
        for cell_html in row:
            if cell_html != "occupied":
                table_html_parts.append(cell_html or "<td></td>")
        table_html_parts.append("</tr>")

    table_html_parts.append("</table></div>")
    return "".join(table_html_parts)

