import tempfile
import os
import fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics

def _mktemp_pdf():
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    return path

def export_certificates(template_path, csv_path, mappings, canvas_size, output_dir, font_manager):
    import pandas as pd
    df = pd.read_csv(csv_path)
    generated = []

    for idx, row in df.iterrows():
        temp_template = _mktemp_pdf()
        template_doc = fitz.open(template_path)
        template_doc.save(temp_template)
        template_doc.close()

        overlay_path = _mktemp_pdf()

        temp_doc = fitz.open(temp_template)
        page = temp_doc[0]
        page_width = page.rect.width
        page_height = page.rect.height

        x_scale = page_width / canvas_size[0] if canvas_size[0] else 1.0
        y_scale = page_height / canvas_size[1] if canvas_size[1] else 1.0

        c = canvas.Canvas(overlay_path, pagesize=(page_width, page_height))

        for m in mappings:
            coords = m['coords']
            field = m.get('field') or ""
            font = m.get('font', 'Helvetica')
            value = str(row.get(field, "")) if field else ""
            box_w = (coords[2] - coords[0]) * x_scale
            box_h = (coords[3] - coords[1]) * y_scale
            size = m.get('max_font_size', m.get('size', 48))
            try:
                pdfmetrics.stringWidth(value, font, size)
            except Exception:
                font = 'Helvetica'
            c.setFont(font, size)

            # optional color support: if mapping provides hex color, caller can set m['color'] = '#RRGGBB'
            color_hex = m.get('color')
            if color_hex:
                try:
                    from reportlab.lib import colors
                    c.setFillColor(colors.HexColor(color_hex))
                except Exception:
                    pass

            text_w = pdfmetrics.stringWidth(value, font, size)
            tk_y = coords[1]
            pdf_y_top = page_height - (tk_y * y_scale)
            align = m.get('alignment', 'center')
            if align == 'left':
                pdf_x = coords[0] * x_scale
            elif align == 'right':
                pdf_x = coords[2] * x_scale - text_w
            else:
                pdf_x = coords[0] * x_scale + (box_w - text_w) / 2
            valign = m.get('valign', 'middle')
            try:
                ascent = pdfmetrics.getAscent(font) / 1000 * size
                descent = abs(pdfmetrics.getDescent(font) / 1000 * size)
            except Exception:
                ascent = size * 0.8
                descent = size * 0.2
            if valign == 'top':
                pdf_y = pdf_y_top - ascent
            elif valign == 'bottom':
                pdf_y = pdf_y_top - box_h + descent
            else:
                pdf_y = pdf_y_top - (box_h / 2) + ((ascent - descent) / 2)
            c.drawString(pdf_x, pdf_y, value)

        c.save()
        overlay_pdf = fitz.open(overlay_path)
        page.show_pdf_page(page.rect, overlay_pdf, 0)

        parts = []
        for m in mappings:
            f = m.get('field')
            if f:
                parts.append(str(row.get(f, "")).strip().replace(" ", "_"))
        name = "_".join([p for p in parts if p]) or f"certificate_{idx+1}"
        outpath = os.path.join(output_dir, f"{name}.pdf")
        temp_doc.save(outpath)
        temp_doc.close()
        overlay_pdf.close()

        try:
            os.unlink(overlay_path)
        except Exception:
            pass
        try:
            os.unlink(temp_template)
        except Exception:
            pass

        generated.append(outpath)

    return generated