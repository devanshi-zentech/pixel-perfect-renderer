"""
DocxConverter Service

Enhanced Azure Document Intelligence JSON to DOCX converter with:
- Proper text rotation using DrawingML instead of VML
- Rotated table cell borders
- Clean DOCX output without repair warnings
- Accurate positioning and scaling

Key improvements:
1. Uses DrawingML <w:drawing> with <a:xfrm rot> for reliable rotation
2. Rotation applied to both text content and table borders
3. Proper namespace declarations and document structure
4. Shape rotation around center point, not top-left corner
"""

import os
import math
from typing import Dict, List, Tuple
from io import BytesIO

from docx import Document
from docx.shared import Inches, Pt
from docx.oxml import parse_xml, ns

class DocxConverter:
    """
    Converts Azure Document Intelligence JSON to pixel-perfect DOCX files.
    Uses DrawingML for proper text rotation and positioning.
    """
    
    # ============================================================================
    # CONFIGURATION
    # ============================================================================
    
    FONT_NAME = "Calibri"
    FONT_SIZE_PT = 10
    PAGE_WIDTH_INCH = 8.27   # A4 width
    PAGE_HEIGHT_INCH = 11.69 # A4 height
    PRESERVE_ASPECT = True
    MIN_BOX_IN = 0.02
    
    # DrawingML units: 914400 EMUs (English Metric Units) = 1 inch
    EMU_PER_INCH = 914400
    # Rotation in DrawingML: 60,000 units = 1 degree
    ROT_UNITS_PER_DEGREE = 60000
    
    def __init__(self):
        """Initialize the DOCX converter and register necessary namespaces."""
        # Register all necessary namespaces
        ns.nsmap.update({
            "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
            "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
            "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
            "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
        })
    
    # ============================================================================
    # COORDINATE & GEOMETRY UTILITIES
    # ============================================================================
    
    def _extract_coords(self, poly) -> Tuple[List[float], List[float]]:
        """Extract X and Y coordinates from various polygon formats."""
        if not poly:
            return [], []
        first = poly[0]
        if isinstance(first, dict) and "x" in first and "y" in first:
            xs = [float(p["x"]) for p in poly]
            ys = [float(p["y"]) for p in poly]
        elif isinstance(first, (list, tuple)) and len(first) >= 2:
            if isinstance(first[0], (int, float)):
                xs = [float(v) for v in poly[0::2]]
                ys = [float(v) for v in poly[1::2]]
            else:
                xs = [float(p[0]) for p in poly]
                ys = [float(p[1]) for p in poly]
        elif isinstance(first, (int, float)):
            xs = [float(v) for v in poly[0::2]]
            ys = [float(v) for v in poly[1::2]]
        else:
            xs, ys = [], []
        return xs, ys
    
    def _coords_to_bbox(self, xs: List[float], ys: List[float], bbox: dict, 
                        src_width, src_height):
        """Convert coordinates to bounding box (left, top, width, height)."""
        try:
            if xs and ys:
                max_x, max_y = max(xs), max(ys)
                min_x, min_y = min(xs), min(ys)
                # Handle normalized coordinates (0..1)
                if max_x <= 1.01 and src_width:
                    left = float(min_x) * float(src_width)
                    right = float(max_x) * float(src_width)
                    top = float(min_y) * float(src_height)
                    bottom = float(max_y) * float(src_height)
                else:
                    left, right = float(min_x), float(max_x)
                    top, bottom = float(min_y), float(max_y)
                w = max(1.0, right - left)
                h = max(1.0, bottom - top)
                return left, top, w, h
            
            # Fallback to boundingBox dict
            if isinstance(bbox, dict) and all(k in bbox for k in ("left", "top", "width", "height")):
                return (float(bbox["left"]), float(bbox["top"]), 
                       float(bbox["width"]), float(bbox["height"]))
        except Exception:
            return None
        return None
    
    def _bbox_from_polygon(self, poly, src_width, src_height):
        """
        Compute oriented bounding box from polygon.
        Returns (left, top, width, height, angle_deg) where:
        - left, top: coordinates of first polygon point
        - width: length along top edge (p1 to p2)
        - height: length along left edge (p1 to p4)
        - angle_deg: angle of top edge (CCW from +X axis)
        """
        if not poly:
            return None
        
        pts = []
        try:
            if isinstance(poly[0], dict):
                pts = [(float(p["x"]), float(p["y"])) for p in poly]
            elif isinstance(poly[0], (list, tuple)):
                pts = [(float(p[0]), float(p[1])) for p in poly]
            else:
                vals = [float(v) for v in poly]
                pts = [(vals[i], vals[i+1]) for i in range(0, len(vals), 2)]
        except Exception:
            return None
        
        if len(pts) < 4:
            return None
        
        p1x, p1y = pts[0]
        p2x, p2y = pts[1]
        p4x, p4y = pts[3]
        
        # Scale normalized coordinates
        max_x = max(x for x, _ in pts)
        if max_x <= 1.01 and src_width:
            p1x *= src_width; p2x *= src_width; p4x *= src_width
            p1y *= src_height; p2y *= src_height; p4y *= src_height
        
        w = math.hypot(p2x - p1x, p2y - p1y)
        h = math.hypot(p4x - p1x, p4y - p1y)
        angle = math.degrees(math.atan2(p2y - p1y, p2x - p1x))
        
        # Normalize very small angles to zero
        if abs(angle) < 0.25:
            angle = 0.0
        
        return float(p1x), float(p1y), float(w), float(h), float(angle)
    
    def _calculate_font_size(self, height_inch: float) -> int:
        """
        Calculate font size in points from bounding box height.
        
        Args:
            height_inch: Height of bounding box in inches
            
        Returns:
            Font size in points (clamped between 6 and 72)
        """
        # Convert height to points and apply improved multiplier
        # Updated multiplier (0.90) accounts for better text-to-box ratio matching
        # This produces font sizes closer to the original PDF proportions
        font_size_pt = height_inch * 72 * 0.90
        
        # Clamp to reasonable range
        return max(6, min(72, int(font_size_pt)))
    
    # ============================================================================
    # DRAWINGML SHAPE CREATION
    # ============================================================================
    
    def _create_drawingml_textbox(
        self,
        paragraph,
        x_inch: float,
        y_inch: float,
        width_inch: float,
        height_inch: float,
        text: str,
        angle_deg: float = 0.0,
        shape_id: int = 1,
        is_border_only: bool = False,
        font_size_pt: int = 10
    ):
        """
        Create a DrawingML textbox with proper rotation support.
        
        Args:
            paragraph: docx paragraph to append shape to
            x_inch, y_inch: position in inches (top-left before rotation)
            width_inch, height_inch: size in inches
            text: text content
            angle_deg: rotation angle in degrees (CCW from horizontal)
            shape_id: unique shape identifier
            is_border_only: if True, draw only border without text (for tables)
            font_size_pt: font size in points
        """
        # DrawingML rotation: Azure angle is CCW from +X, Word rotation is also CCW
        # Units: 60,000 per degree
        rot_units = int(angle_deg * self.ROT_UNITS_PER_DEGREE)
        
        # CRITICAL FIX: Calculate geometric center accounting for rotation
        # Azure gives us position (x,y) = p1 corner, width/height along rotated edges, and angle
        
        # For NEARLY HORIZONTAL shapes (angle close to 0°), use simple center calculation
        # to avoid numerical errors. For ALL OTHER angles including vertical, use geometric formula.
        abs_angle = abs(angle_deg)
        is_near_horizontal = abs_angle < 2 or abs(abs_angle - 180) < 2
        
        if is_near_horizontal:
            # Nearly horizontal (±2°): simple calculation avoids numerical errors
            cx_rotated = x_inch + width_inch / 2
            cy_rotated = y_inch + height_inch / 2
        else:
            # For ALL other angles (including vertical ±90°), use geometric calculation
            # This correctly handles the sign differences between +90° and -90° rotations
            angle_rad = math.radians(angle_deg)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            
            # Calculate the geometric center from p1, width (along rotated top edge), height (along rotated left edge)
            # Center = p1 + 0.5*(vector from p1 to p2) + 0.5*(vector from p1 to p4)
            # where p1→p2 has length=width at angle=angle_deg
            #       p1→p4 has length=height at angle=(angle_deg - 90°)
            cx_rotated = x_inch + 0.5 * width_inch * cos_a + 0.5 * height_inch * sin_a
            cy_rotated = y_inch + 0.5 * width_inch * sin_a - 0.5 * height_inch * cos_a
        
        # DrawingML rotates around this center. Position parameter is top-left of UNROTATED box
        # For unrotated box: center = (x_unrot + w/2, y_unrot + h/2)
        # Therefore: x_unrot = center_x - w/2, y_unrot = center_y - h/2
        x_unrotated = cx_rotated - width_inch / 2
        y_unrotated = cy_rotated - height_inch / 2
        
        # Convert to EMUs
        x_emu = int(x_unrotated * self.EMU_PER_INCH)
        y_emu = int(y_unrotated * self.EMU_PER_INCH)
        width_emu = int(width_inch * self.EMU_PER_INCH)
        height_emu = int(height_inch * self.EMU_PER_INCH)
        
        # Escape text for XML
        text_escaped = (text.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;")
                            .replace('"', "&quot;"))
        
        # Build the textbox content if not border-only
        if not is_border_only and text:
            textbox_content = f"""
                        <wps:txbx>
                            <w:txbxContent>
                                <w:p>
                                    <w:pPr>
                                        <w:spacing w:before="0" w:after="0"/>
                                    </w:pPr>
                                    <w:r>
                                        <w:rPr>
                                            <w:rFonts w:ascii="{self.FONT_NAME}" w:hAnsi="{self.FONT_NAME}"/>
                                            <w:sz w:val="{int(font_size_pt * 2)}"/>
                                        </w:rPr>
                                        <w:t xml:space="preserve">{text_escaped}</w:t>
                                    </w:r>
                                </w:p>
                            </w:txbxContent>
                        </wps:txbx>"""
        else:
            textbox_content = ""
        
        # Build fill and stroke properties
        if is_border_only:
            fill_xml = '<a:noFill/>'
            line_xml = f'''
                        <a:ln w="9525">
                            <a:solidFill>
                                <a:srgbClr val="000000"/>
                            </a:solidFill>
                        </a:ln>'''
        else:
            fill_xml = '<a:noFill/>'
            line_xml = '<a:ln><a:noFill/></a:ln>'
        
        # Create optimized DrawingML structure for better Word performance
        # Use simple z-index values and minimal XML
        z_index = shape_id
        
        drawing_xml = f'''
        <w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
             xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">
            <w:drawing>
                <wp:anchor simplePos="0" relativeHeight="{z_index}" behindDoc="0" locked="0" layoutInCell="0" allowOverlap="1">
                    <wp:simplePos x="0" y="0"/>
                    <wp:positionH relativeFrom="page">
                        <wp:posOffset>{x_emu}</wp:posOffset>
                    </wp:positionH>
                    <wp:positionV relativeFrom="page">
                        <wp:posOffset>{y_emu}</wp:posOffset>
                    </wp:positionV>
                    <wp:extent cx="{width_emu}" cy="{height_emu}"/>
                    <wp:wrapNone/>
                    <wp:docPr id="{shape_id}" name="S{shape_id}"/>
                    <a:graphic>
                        <a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">
                            <wps:wsp>
                                <wps:cNvSpPr txBox="1"/>
                                <wps:spPr>
                                    <a:xfrm rot="{rot_units}">
                                        <a:off x="0" y="0"/>
                                        <a:ext cx="{width_emu}" cy="{height_emu}"/>
                                    </a:xfrm>
                                    <a:prstGeom prst="rect"/>
                                    {fill_xml}
                                    {line_xml}
                                </wps:spPr>
                                {textbox_content}
                                <wps:bodyPr lIns="0" tIns="0" rIns="0" bIns="0" anchor="t" wrap="none">
                                    <a:spAutoFit/>
                                </wps:bodyPr>
                            </wps:wsp>
                        </a:graphicData>
                    </a:graphic>
                </wp:anchor>
            </w:drawing>
        </w:r>'''
        
        try:
            elem = parse_xml(drawing_xml)
            paragraph._element.append(elem)
        except Exception as e:
            print(f"Warning: Could not add shape '{text[:30] if text else 'border'}...': {e}")
    
    # ============================================================================
    # METADATA & PACKAGING
    # ============================================================================
    
    def _ensure_docx_metadata(self, doc: Document):
        """
        Ensure DOCX has proper OPC metadata, content types, and relationships
        for recognition by Slack, Microsoft Teams, and other viewers.
        
        Fixes:
        - Core properties (document metadata) - required for file type detection
        - App properties (Word application metadata) - identifies as Word document
        - Content_Types.xml with explicit Override entries
        - Root-level relationships (_rels/.rels) with correct URIs
        - Proper package structure compliance
        """
        from docx.opc.constants import CONTENT_TYPE as CT
        from docx.oxml import parse_xml
        
        # Set core properties (required for proper file recognition)
        core_props = doc.core_properties
        if not core_props.title:
            core_props.title = "Document"
        if not core_props.author:
            core_props.author = "Azure Document Intelligence Converter"
        if not core_props.last_modified_by:
            core_props.last_modified_by = "Azure Document Intelligence Converter"
        
        # Ensure app properties exist (critical for Slack/Teams recognition)
        # App properties identify the file as a Word document
        app_part = None
        try:
            # Try to get existing app part
            app_part = doc.part.package.part_related_by(
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties"
            )
        except KeyError:
            # Create app.xml if missing (required for proper Word recognition)
            app_xml_str = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
    <Application>Microsoft Office Word</Application>
    <DocSecurity>0</DocSecurity>
    <ScaleCrop>false</ScaleCrop>
    <HeadingPairs>
        <vt:vector size="2" baseType="variant">
            <vt:variant>
                <vt:lpstr>Heading</vt:lpstr>
            </vt:variant>
            <vt:variant>
                <vt:i4>0</vt:i4>
            </vt:variant>
        </vt:vector>
    </HeadingPairs>
    <TitlesOfParts>
        <vt:vector size="1" baseType="lpstr">
            <vt:lpstr></vt:lpstr>
        </vt:vector>
    </TitlesOfParts>
    <Company></Company>
    <LinksUpToDate>false</LinksUpToDate>
    <CharactersWithSpaces>0</CharactersWithSpaces>
    <SharedDoc>false</SharedDoc>
    <HyperlinksChanged>false</HyperlinksChanged>
    <AppVersion>16.0000</AppVersion>
</Properties>"""
            
            app_part = doc.part.package.add_part(
                "/docProps/app.xml",
                CT.OFC_EXTENDED_PROPERTIES,
                parse_xml(app_xml_str)
            )
            doc.part.package.relate_to(
                app_part,
                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties"
            )
        
        # Remove non-standard parts that prevent proper recognition
        # Standard Word documents don't include customXml or thumbnails
        package = doc.part.package
        
        # Collect parts to remove (by partname)
        parts_to_remove = []
        
        # Find and mark customXml parts for removal
        # package.parts is a list, not a dict
        for part in list(package.parts):
            partname = part.partname
            if partname.startswith("/customXml/"):
                parts_to_remove.append(partname)
        
        # Find and mark thumbnail for removal
        for part in list(package.parts):
            partname = part.partname
            if "thumbnail" in partname.lower():
                parts_to_remove.append(partname)
        
        # Remove relationships pointing to these parts, then remove parts
        for partname in parts_to_remove:
            # Find relationships pointing to this part
            rels_to_remove = []
            for rel in list(package.rels.values()):
                if rel.target_ref == partname.lstrip("/"):
                    rels_to_remove.append(rel.rId)
            
            # Remove relationships first
            for rId in rels_to_remove:
                try:
                    package.drop_rel(rId)
                except:
                    pass
            
            # Remove the part itself
            try:
                # Find and remove the part from the list
                parts_list = list(package.parts)
                for part in parts_list:
                    if part.partname == partname:
                        package.parts.remove(part)
                        break
            except:
                pass
        
        # Also remove customXml relationships from document.xml.rels if present
        try:
            doc_rels = doc.part.rels
            doc_rels_to_remove = []
            for rel in list(doc_rels.values()):
                if rel.target_ref.startswith("customXml/"):
                    doc_rels_to_remove.append(rel.rId)
            
            for rId in doc_rels_to_remove:
                try:
                    doc_rels.drop_rel(rId)
                except:
                    pass
        except:
            pass
    
    # ============================================================================
    # MAIN CONVERSION METHODS
    # ============================================================================
    
    def convert_to_docx_bytes(self, data: Dict) -> bytes:
        """
        Convert Azure JSON to DOCX bytes using DrawingML for proper rotation.
        Returns the DOCX file as bytes for direct upload/streaming.
        Args:
            data: Azure Document Intelligence JSON response
        
        Returns:
            bytes: Complete DOCX file as bytes
        """
        doc = Document()
        section = doc.sections[0]
        section.page_width = Inches(self.PAGE_WIDTH_INCH)
        section.page_height = Inches(self.PAGE_HEIGHT_INCH)
        section.left_margin = section.right_margin = Inches(0)
        section.top_margin = section.bottom_margin = Inches(0)
        
        pages = data.get("pages", [])
        if not pages:
            print("Warning: No pages found in Azure JSON data.")
        
        shape_id = 1
        for page_idx, page in enumerate(pages):
            # Add page break before each page except the first one
            if page_idx > 0:
                doc.add_page_break()
            
            page_paragraph = doc.add_paragraph()
            page_paragraph.paragraph_format.space_before = Pt(0)
            page_paragraph.paragraph_format.space_after = Pt(0)
            
            # Get page dimensions
            src_width = page.get("width", 0)
            src_height = page.get("height", 0)
            src_unit = str(page.get("unit", "pixel")).lower()
            
            if not src_width or not src_height:
                print(f"Warning: Page {page_idx+1} has invalid dimensions, skipping...")
                continue
            
            # Infer DPI for pixel units
            inferred_dpi = 72.0
            if src_unit in ("pixel", "px", ""):
                if float(src_width) > 1000:
                    inferred_dpi = float(src_width) / 8.5
            
            # Convert to inches
            if src_unit in ("inch", "in"):
                src_width_in = float(src_width)
                src_height_in = float(src_height)
            elif src_unit in ("cm", "centimeter"):
                src_width_in = float(src_width) / 2.54
                src_height_in = float(src_height) / 2.54
            else:
                src_width_in = float(src_width) / float(inferred_dpi)
                src_height_in = float(src_height) / float(inferred_dpi)
            
            # Compute scale factors
            x_scale = self.PAGE_WIDTH_INCH / src_width_in if src_width_in > 0 else 1.0
            y_scale = self.PAGE_HEIGHT_INCH / src_height_in if src_height_in > 0 else 1.0
            if self.PRESERVE_ASPECT:
                scale = min(x_scale, y_scale)
                x_scale = y_scale = scale
            
            print(f"Page {page_idx+1}: {src_width}x{src_height} {src_unit} "
                  f"({src_width_in:.2f}\" x {src_height_in:.2f}\") "
                  f"-> scale={scale:.4f}")
            
            # --- Render table borders ---
            tables_on_page = list(page.get("tables", []))
            for t in data.get("tables", []):
                brs = t.get("boundingRegions") or []
                try:
                    if any((br.get("pageNumber") == page.get("pageNumber")) 
                          for br in brs if isinstance(br, dict)):
                        tables_on_page.append(t)
                except Exception:
                    continue
            
            if tables_on_page:
                print(f"  Rendering {len(tables_on_page)} table(s) with borders...")
            
            for table in tables_on_page:
                for cell in table.get("cells", []):
                    # Extract polygon from multiple possible locations
                    region = (cell.get("boundingRegions") or [{}])[0]
                    poly = region.get("polygon") or cell.get("polygon") or cell.get("boundingPolygon") or []
                    
                    # Ensure we have valid polygon data before processing
                    if not poly:
                        # Try to construct from boundingBox if polygon missing
                        bbox = cell.get("boundingBox") or region.get("boundingBox") or {}
                        if bbox:
                            print(f"  Warning: Table cell missing polygon, using bbox (no rotation)")
                        continue
                    
                    # Compute oriented bbox for rotation (REQUIRED for table borders)
                    oriented = self._bbox_from_polygon(poly, src_width, src_height)
                    
                    if not oriented:
                        print(f"  Warning: Could not compute oriented bbox for table cell, skipping")
                        continue
                    
                    left_src, top_src, w_src, h_src, angle = oriented
                    
                    # Convert to inches
                    if src_unit in ("pixel", "px", ""):
                        left_in = left_src / inferred_dpi * x_scale
                        top_in = top_src / inferred_dpi * y_scale
                        width_in = w_src / inferred_dpi * x_scale
                        height_in = h_src / inferred_dpi * y_scale
                    else:
                        left_in = left_src * x_scale
                        top_in = top_src * y_scale
                        width_in = w_src * x_scale
                        height_in = h_src * y_scale
                    
                    # Ensure minimum size
                    width_in = max(width_in, self.MIN_BOX_IN)
                    height_in = max(height_in, self.MIN_BOX_IN)
                    
                    # Clamp to page bounds
                    left_in = max(0.0, min(left_in, self.PAGE_WIDTH_INCH - self.MIN_BOX_IN))
                    top_in = max(0.0, min(top_in, self.PAGE_HEIGHT_INCH - self.MIN_BOX_IN))
                    width_in = min(width_in, self.PAGE_WIDTH_INCH - left_in)
                    height_in = min(height_in, self.PAGE_HEIGHT_INCH - top_in)
                    
                    # Create border-only shape with rotation (font size not used for borders)
                    self._create_drawingml_textbox(
                        page_paragraph, left_in, top_in, width_in, height_in,
                        "", angle, shape_id, is_border_only=True, font_size_pt=10
                    )
                    shape_id += 1
            
            # --- Render text lines ---
            print(f"  Rendering {len(page.get('lines', []))} line(s)...")
            for line in page.get("lines", []):
                text = line.get("content", "").strip()
                if not text:
                    continue
                
                poly = line.get("polygon") or line.get("boundingPolygon") or []
                
                # Prefer oriented bbox for rotation
                oriented = None
                if poly and len(poly) >= 4:
                    oriented = self._bbox_from_polygon(poly, src_width, src_height)
                
                # Fallback to boundingBox if oriented computation failed
                if not oriented:
                    bbox = line.get("boundingBox")
                    if bbox:
                        xs, ys = self._extract_coords(poly)
                        left_src, top_src, width_src, height_src = self._coords_to_bbox(
                            xs, ys, bbox, src_width, src_height
                        )
                        angle = 0.0
                    else:
                        print(f"  Warning: No valid bounding info for line '{text[:30]}...', skipping")
                        continue
                else:
                    left_src, top_src, width_src, height_src, angle = oriented
                
                # Convert to inches
                if src_unit in ("pixel", "px", ""):
                    left_in = left_src / inferred_dpi * x_scale
                    top_in = top_src / inferred_dpi * y_scale
                    width_in = width_src / inferred_dpi * x_scale
                    original_height_in = height_src / inferred_dpi * y_scale
                    height_in = original_height_in
                else:
                    left_in = left_src * x_scale
                    top_in = top_src * y_scale
                    width_in = width_src * x_scale
                    original_height_in = height_src * y_scale
                    height_in = original_height_in
                
                # Ensure minimum size
                width_in = max(width_in, self.MIN_BOX_IN)
                height_in = max(height_in, self.MIN_BOX_IN)
                
                # Calculate font size from bounding box height
                font_size_pt = self._calculate_font_size(height_in)
                
                # Special handling for vertical text (±90°): larger font multiplier
                is_near_vertical = abs(abs(angle) - 90) < 5
                if is_near_vertical:
                    font_size_pt = original_height_in * 72 * 1.0
                    
                    # Apply rightward and downward offset for better vertical baseline alignment
                    left_in += 0.8 * height_in
                    top_in += 0.15 * width_in
                
                # Clamp to page bounds
                left_in = max(0.0, min(left_in, self.PAGE_WIDTH_INCH - self.MIN_BOX_IN))
                top_in = max(0.0, min(top_in, self.PAGE_HEIGHT_INCH - self.MIN_BOX_IN))
                width_in = min(width_in, self.PAGE_WIDTH_INCH - left_in)
                height_in = min(height_in, self.PAGE_HEIGHT_INCH - top_in)
                
                # Create textbox shape with rotation
                self._create_drawingml_textbox(
                    page_paragraph, left_in, top_in, width_in, height_in,
                    text, angle, shape_id, is_border_only=False, font_size_pt=font_size_pt
                )
                shape_id += 1
        
        # Ensure proper OPC metadata for file recognition
        self._ensure_docx_metadata(doc)
        
        # Save to bytes instead of file
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    
    def convert_to_docx_file(self, data: Dict, out_path: str) -> str:
        """
        Convert Azure JSON to DOCX file using DrawingML for proper rotation.
        Each page becomes a Word page with all text and table borders positioned accurately.        
        Args:
            data: Azure Document Intelligence JSON response
            out_path: Output file path
        
        Returns:
            str: Path to the generated DOCX file
        """
        # Get DOCX bytes
        docx_bytes = self.convert_to_docx_bytes(data)
        
        # Ensure output file has .docx extension
        if not out_path.lower().endswith('.docx'):
            out_path = os.path.splitext(out_path)[0] + '.docx'
        
        # Save to file
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, 'wb') as f:
            f.write(docx_bytes)
        
        return out_path

