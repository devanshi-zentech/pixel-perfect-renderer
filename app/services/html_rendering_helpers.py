import math
from typing import Dict, List, Set, Any

# --- Custom Imports ---
# Imports constants for default values.
from app.core import constants


def render_word(word_data: Dict[str, Any], scaling_factor: float, measurement_unit: str) -> str:
    """
    Renders a single word as an absolutely positioned HTML <span> element
    based on its polygon coordinates, scaling factor, and angle. It filters out
    low-confidence words and potential watermarks.
    """
    polygon = word_data.get("polygon", [])
    if not polygon or len(polygon) < 8 or word_data.get("confidence", 0) < 0.4:
        return ""

    # left/top in **output pixels**
    left = polygon[0] * scaling_factor
    top = polygon[1] * scaling_factor

    # compute rotation and height in source units then scale to pixels
    p1_x, p1_y = polygon[0], polygon[1]
    p2_x, p2_y = polygon[2], polygon[3]
    p4_x, p4_y = polygon[6], polygon[7]

    angle_deg = math.degrees(math.atan2(p2_y - p1_y, p2_x - p1_x))
    word_height_in_pixels = math.sqrt((p4_x - p1_x) ** 2 + (p4_y - p1_y) ** 2) * scaling_factor
    font_size_in_pixels = max(1.0, word_height_in_pixels * 0.8)  # avoid zero font size

    # optional watermark filter
    if font_size_in_pixels > 200:  # high threshold; tune as needed
        return ""

    sanitized_content = str(word_data.get("content", "")).replace("<", "&lt;").replace(">", "&gt;")

    style = constants.RENDER_WORD_STYLE.format(
        left=left, top=top, word_height=word_height_in_pixels, font_size=font_size_in_pixels, angle_deg=angle_deg
    )
    extra_attrs = ""
    if abs(abs(angle_deg) - 90) < 15:
        extra_attrs = ' data-orientation="vertical"'

    return f'<span{extra_attrs} style="{style}">{sanitized_content}</span>'


def render_table_with_words(
        table_data: Dict[str, Any],
        current_page: int,
        scaling_factor: float,
        word_position_map: Dict[int, Dict[str, Any]],
        rendered_word_indices: Set[int],
        measurement_unit: str,
) -> str:
    """
    Renders an HTML table with words positioned inside their cells.

    Key improvements:
    - Compute each cell's bounding box from its polygon and scale to px.
    - Make each <td>/<th> `position: relative` so absolute children are localized.
    - For non-rotated cells, reconstruct in-flow text ordered left-to-right.
    - Mark table spans as rendered to avoid duplication.
    """
    if not table_data.get("boundingRegions") or table_data["boundingRegions"][0].get("pageNumber") != current_page:
        return ""

    # Gather all span indices for this table
    all_spans = [i for cell in table_data.get("cells", []) for span in cell.get("spans", [])
                 for i in range(span.get("offset", 0), span.get("offset", 0) + span.get("length", 0))]
    # if everything already rendered, skip whole table
    if all_spans and all(i in rendered_word_indices for i in all_spans):
        return ""

    polygon = table_data["boundingRegions"][0].get("polygon", [])
    if not polygon:
        return ""

    # table bounding box (in source units), then scale to px
    table_x = polygon[0::2]
    table_y = polygon[1::2]
    table_left_position, table_top_position = min(table_x), min(table_y)
    table_width_in_pixels = (max(table_x) - min(table_x)) * scaling_factor
    table_height_in_pixels = (max(table_y) - min(table_y)) * scaling_factor

    # Start table container (position table at absolute location)
    table_left_position_in_pixels = table_left_position * scaling_factor
    table_top_position_in_pixels = table_top_position * scaling_factor
    table_html_content: List[str] = [
        constants.RENDER_TABLE_STYLE.format(left=table_left_position_in_pixels, top=table_top_position_in_pixels, width=table_width_in_pixels)
    ]

    # safe grid
    rows = max(1, int(table_data.get("rowCount", 0)))
    cols = max(1, int(table_data.get("columnCount", 0)))
    table_grid: List[List[Any]] = [[None for _ in range(cols)] for _ in range(rows)]

    def find_next_free_column(row_index: int, start_column_index: int) -> int:
        column_index = start_column_index
        while column_index < cols and table_grid[row_index][column_index] is not None:
            column_index += 1
        return column_index if column_index < cols else -1

    # Render each cell
    for cell in table_data.get("cells", []):
        row_index = int(cell.get("rowIndex", 0))
        column_index = int(cell.get("columnIndex", 0))
        row_span = int(cell.get("rowSpan", 1))
        col_span = int(cell.get("columnSpan", 1))

        if row_index >= rows:
            continue
        if column_index >= cols:
            # try to find next free column in row r
            next_free_column_index = find_next_free_column(row_index, 0)
            if next_free_column_index == -1:
                continue
            column_index = next_free_column_index
        else:
            next_free_column_index = find_next_free_column(row_index, column_index)
            if next_free_column_index == -1:
                continue
            column_index = next_free_column_index

        # collect words that belong to this cell from spans
        cell_spans = cell.get("spans", [])
        cell_word_indices = [i for span in cell_spans for i in range(span.get("offset", 0), span.get("offset", 0) + span.get("length", 0))]
        words_in_cell = [word_position_map[i] for i in cell_word_indices if i in word_position_map]

        # compute avg rotation (source units)
        avg_angle_deg = 0.0
        if words_in_cell:
            angles = []
            for w in words_in_cell:
                poly = w.get("polygon", [])
                if len(poly) >= 4:
                    p1x, p1y = poly[0], poly[1]
                    p2x, p2y = poly[2], poly[3]
                    angles.append(math.degrees(math.atan2(p2y - p1y, p2x - p1x)))
            if angles:
                avg_angle_deg = sum(angles) / len(angles)

        tag = "th" if cell.get("kind") == "columnHeader" else "td"

        # get cell polygon bbox (source units) -> scale to px
        cell_br = cell.get("boundingRegions", [])
        cell_poly = []
        if cell_br:
            cell_poly = cell_br[0].get("polygon", [])
        # if polygon missing, fallback: divide table bbox evenly (best-effort)
        if not cell_poly:
            # fallback: assume uniform column widths / row heights
            # compute best-effort width/height in px
            cell_width_in_pixels = (table_width_in_pixels / cols) * col_span
            cell_height_in_pixels = (table_height_in_pixels / rows) * row_span
            cell_left_position = table_left_position + (table_width_in_pixels / scaling_factor) * column_index / cols
            cell_top_position = table_top_position + (table_height_in_pixels / scaling_factor) * row_index / rows
        else:
            cx = cell_poly[0::2]
            cy = cell_poly[1::2]
            cell_left_position = min(cx)
            cell_top_position = min(cy)
            cell_width_in_pixels = (max(cx) - min(cx)) * scaling_factor
            cell_height_in_pixels = (max(cy) - min(cy)) * scaling_factor

        # generate inner content
        inner_html_parts: List[str] = []
        if words_in_cell and abs(abs(avg_angle_deg) - 90) < 15:
            # vertically-oriented words -> absolute position inside cell
            # compute cell origin in source units for local coordinates
            for idx, w in enumerate(words_in_cell):
                poly = w.get("polygon", [])
                if len(poly) < 8:
                    continue
                # local offset in source units, then convert to px
                w_left_position_in_pixels = (poly[0] - cell_left_position) * scaling_factor
                w_top_position_in_pixels = (poly[1] - cell_top_position) * scaling_factor

                # compute rotated metrics in source units then scale
                p1x, p1y = poly[0], poly[1]
                p2x, p2y = poly[2], poly[3]
                p4x, p4y = poly[6], poly[7]
                angle = math.degrees(math.atan2(p2y - p1y, p2x - p1x))
                word_height_in_pixels = math.sqrt((p4x - p1x) ** 2 + (p4y - p1y) ** 2) * scaling_factor
                font_size_in_pixels = max(1.0, word_height_in_pixels * 0.9)

                sanitized = str(w.get("content", "")).replace("<", "&lt;").replace(">", "&gt;")
                word_style = constants.RENDER_TABLE_WORD_STYLE.format(
                    w_left_position_in_pixels=w_left_position_in_pixels,
                    w_top_position_in_pixels=w_top_position_in_pixels,
                    angle=angle,
                    font_size_in_pixels=font_size_in_pixels,
                    word_height_in_pixels=word_height_in_pixels,
                )
                extra_attrs = ' data-orientation="vertical"'
                inner_html_parts.append(f'<span{extra_attrs} style="{word_style}">{sanitized}</span>')

            inner_html = "".join(inner_html_parts)
            # ensure the cell has the computed width/height and position:relative
            cell_style = constants.CELL_STYLE.format(cell_width_px=cell_width_in_pixels, cell_height_px=cell_height_in_pixels)
            table_grid[row_index][column_index] = f'<{tag} rowspan="{row_span}" colspan="{col_span}" style="{cell_style}">{inner_html}</{tag}>'
        else:
            # normal / horizontal words -> render in-flow text ordered by x coordinate
            # sort words left->right using first polygon x
            sorted_words = sorted(
                [(w, w.get("polygon", [0])) for w in words_in_cell],
                key=lambda t: t[1][0] if len(t[1]) >= 2 else 0
            )
            # combine sanitized contents separated by space
            in_flow_text = " ".join(str(w.get("content", "")).replace("<", "&lt;").replace(">", "&gt;") for w, _ in sorted_words)
            # fallback to cell["content"] if nothing found
            if not in_flow_text:
                in_flow_text = str(cell.get("content", "")).replace("<", "&lt;").replace(">", "&gt;")
            cell_style = constants.EMPTY_CELL_STYLE.format(cell_width_px=cell_width_in_pixels, cell_height_px=cell_height_in_pixels)

            # put text inside a wrapping div to control overflow and ellipsis
            cell_html = constants.CELL_HTML.format(in_flow_text=in_flow_text)
            table_grid[row_index][column_index] = f'<{tag} rowspan="{row_span}" colspan="{col_span}" style="{cell_style}">{cell_html}</{tag}>'

        # mark occupied cells for the span of rowspan/colspan
        for rr in range(row_index, row_index + row_span):
            for cc in range(column_index, column_index + col_span):
                if rr < rows and cc < cols and not (rr == row_index and cc == column_index):
                    table_grid[rr][cc] = "occupied"

        # mark this table's word spans as rendered (so next tables won't duplicate)
        for span in cell.get("spans", []):
            offset = int(span.get("offset", 0))
            length = int(span.get("length", 0))
            for i in range(offset, offset + length):
                rendered_word_indices.add(i)

    # build final rows
    for row_index in range(rows):
        table_html_content.append("<tr>")
        for column_index in range(cols):
            cell_html = table_grid[row_index][column_index]
            if cell_html == "occupied":
                continue
            table_html_content.append(cell_html or "<td style='border:1px solid black;'></td>")
        table_html_content.append("</tr>")

    table_html_content.append("</table></div>")
    return "".join(table_html_content)
