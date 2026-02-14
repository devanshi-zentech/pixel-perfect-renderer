from io import BytesIO
from typing import Dict, Any, List, Tuple
from docx import Document
from docx.shared import Pt
import statistics
import traceback


def _bbox_vertices(word: Dict[str, Any]) -> List[Tuple[float, float]]:
    """Return list of (x,y) vertices for a word's bbox or polygon in normalized form."""
    bbox = word.get("boundingBox") or word.get("polygon") or []
    verts: List[Tuple[float, float]] = []
    for v in bbox:
        if isinstance(v, dict):
            x = float(v.get("x", 0))
            y = float(v.get("y", 0))
            verts.append((x, y))
        elif isinstance(v, (list, tuple)) and len(v) >= 2:
            try:
                x = float(v[0])
                y = float(v[1])
            except Exception:
                x, y = 0.0, 0.0
            verts.append((x, y))
    return verts


def _bbox_metrics(word: Dict[str, Any]) -> Tuple[float, float, float, float]:
    """Return (center_x, center_y, width, height) computed from bbox vertices."""
    verts = _bbox_vertices(word)
    if not verts:
        return 0.0, 0.0, 0.0, 0.0
    xs = [p[0] for p in verts]
    ys = [p[1] for p in verts]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    width = maxx - minx
    height = maxy - miny
    return cx, cy, width, height


def _get_word_center_y(word: Dict[str, Any]) -> float:
    _, cy, _, _ = _bbox_metrics(word)
    return cy


def _get_word_text(word: Dict[str, Any]) -> str:
    """Return the best-guess textual content for a word token from various
    Azure/other schemas (tries `content`, `text`, `word`, and falls back to "")."""
    return (word.get("content") or word.get("text") or word.get("word") or "").strip()


def _group_words_into_lines(words: List[Dict[str, Any]], y_tolerance: float = 5.0) -> List[Dict[str, Any]]:
    """
    Group word-level tokens into lines by Y coordinate clustering and
    compute per-line metrics (avg y, avg x, avg height, avg width, words).
    Returns list of dicts: {"y":..., "x":..., "height":..., "width":..., "words":[...]}.
    """
    if not words:
        return []

    enriched = []
    for w in words:
        cx, cy, width, height = _bbox_metrics(w)
        # fallback x ordering
        x = cx
        enriched.append((cy, x, width, height, w))

    enriched.sort(key=lambda t: (t[0], t[1]))

    # If y_tolerance was not provided explicitly (or is very large), derive a
    # reasonable tolerance from the median word height so lines are grouped
    # based on measured text height rather than an absolute constant.
    if y_tolerance is None or y_tolerance > 1.0:
        heights = [e[3] for e in enriched if e[3] > 0]
        if heights:
            med_h = statistics.median(heights)
            # tolerance should be a fraction of typical height
            y_tolerance = max(med_h * 0.8, 0.01)
        else:
            y_tolerance = 0.02

    lines: List[Dict[str, Any]] = []
    first = enriched[0]
    current_words = [first[4]]
    current_y = first[0]
    heights = [first[3]]
    widths = [first[2]]
    xs = [first[1]]

    for cy, x, width, height, w in enriched[1:]:
        if abs(cy - current_y) <= y_tolerance:
            current_words.append(w)
            heights.append(height)
            widths.append(width)
            xs.append(x)
            # update current_y as running average
            current_y = sum([current_y, cy]) / 2
        else:
            lines.append({
                "y": current_y,
                "x": statistics.median(xs),
                "height": statistics.median(heights) if heights else 0,
                "width": statistics.median(widths) if widths else 0,
                "words": current_words,
            })
            current_words = [w]
            current_y = cy
            heights = [height]
            widths = [width]
            xs = [x]

    if current_words:
        lines.append({
            "y": current_y,
            "x": statistics.median(xs),
            "height": statistics.median(heights) if heights else 0,
            "width": statistics.median(widths) if widths else 0,
            "words": current_words,
        })

    return lines


def azure_json_to_docx(azure_json: Dict[str, Any], debug: bool = False):
    """
    Convert Azure Document Intelligence JSON into a simple, editable DOCX.

    This function focuses on producing semantic Word documents:
    - Tables are reconstructed from `tables` in the payload when present.
    - Otherwise words are grouped into lines and paragraphs.

    Note: This will not reproduce pixel-perfect absolute layout. For visual
    fidelity, consider embedding rendered PDF pages as images into a DOCX.
    """
    doc = Document()

    pages = azure_json.get("pages", [])
    tables = azure_json.get("tables", [])

    # Index tables by page number
    tables_by_page = {}
    for t in tables:
        page_num = t.get("pageNumber", 1)
        tables_by_page.setdefault(page_num, []).append(t)

    # Ensure document has at least one paragraph to avoid some edge-cases downstream
    if not doc.paragraphs and not doc.tables:
        doc.add_paragraph("")

    # diagnostics if requested
    diagnostics = {
        "pages": len(pages),
        "total_words": 0,
        "lines": 0,
        "paragraphs": 0,
    }

    for page in pages:
        page_num = page.get("pageNumber", 1)

        # Insert a page break for subsequent pages
        if page_num > 1:
            doc.add_page_break()

        # If page has tables, render them first (left as-is for now)
        page_tables = tables_by_page.get(page_num, [])
        for t in page_tables:
            # TODO: render table cells into a docx table; kept simple for now
            # We'll still fall back to emitting words as paragraphs below.
            pass

        # Always process words on the page (previous bug: words were only
        # processed inside the table loop, causing pages without tables to be skipped)
        words = page.get("words") or []
        diagnostics["total_words"] += len(words)
        if words:
            lines = _group_words_into_lines(words)
            diagnostics["lines"] += len(lines)

            # Heuristics: determine median line height to detect headings
            line_heights = [l["height"] for l in lines if l.get("height")]
            median_line_height = statistics.median(line_heights) if line_heights else 0

            # Merge lines into paragraphs based on vertical gap
            paragraphs: List[List[Dict[str, Any]]] = []
            current_para: List[Dict[str, Any]] = []
            prev_y = None
            for ln in lines:
                y = ln["y"]
                if prev_y is None:
                    current_para.append(ln)
                else:
                    gap = abs(y - prev_y)
                    # if gap is small relative to median_line_height, continue paragraph
                    if median_line_height and gap <= (median_line_height * 1.2):
                        current_para.append(ln)
                    else:
                        paragraphs.append(current_para)
                        current_para = [ln]
                prev_y = y
            if current_para:
                paragraphs.append(current_para)

            diagnostics["paragraphs"] += len(paragraphs)

            # Emit paragraphs, detecting headings and handling vertical text
            emitted_para_count = 0
            for para in paragraphs:
                # Determine if paragraph is a heading: any line significantly taller than median
                is_heading = any((ln.get("height", 0) > (median_line_height * 1.6)) for ln in para if median_line_height)

                # Compose paragraph text
                para_texts: List[str] = []
                for ln in para:
                    # detect vertical text heuristically
                    if ln.get("width") and ln.get("height") and ln["height"] > (ln["width"] * 1.5):
                        # vertical: join characters/words with newlines to approximate vertical layout
                        words_text = "\n".join(["".join(list(_get_word_text(w))) for w in ln["words"]])
                        para_texts.append(words_text)
                    else:
                        text = " ".join([_get_word_text(w) for w in ln["words"]]).strip()
                        para_texts.append(text)

                final_text = "\n".join([t for t in para_texts if t])
                if not final_text:
                    continue

                if is_heading:
                    # choose heading level based on how big the tallest line is
                    tallest = max((ln.get("height", 0) for ln in para), default=0)
                    level = 1 if median_line_height and tallest > (median_line_height * 2.2) else 2
                    doc.add_paragraph(final_text, style=f'Heading {level}')
                    emitted_para_count += 1
                else:
                    p = doc.add_paragraph()
                    run = p.add_run(final_text)
                    run.font.size = Pt(11)
                    emitted_para_count += 1

            # Fallback: if nothing was emitted for this page (grouping failed),
            # try to use the page-level `content` field if present. This prevents
            # producing an otherwise-empty DOCX when token grouping heuristics
            # don't match the input JSON structure.
            if emitted_para_count == 0:
                page_content = page.get("content") or page.get("text")
                if page_content:
                    p = doc.add_paragraph()
                    run = p.add_run(str(page_content))
                    run.font.size = Pt(11)
                    diagnostics["paragraphs"] += 1

    # Export to bytes with error handling to surface issues during save.
    out = BytesIO()
    try:
        doc.save(out)
    except Exception as e:
        tb = traceback.format_exc()
        raise RuntimeError(f"DOCX generation failed: {e}\n{tb}")

    out.seek(0)
    data = out.getvalue()
    if not data:
        raise RuntimeError("DOCX generator returned no data (expected bytes)")

    if debug:
        return data, diagnostics

    return data
