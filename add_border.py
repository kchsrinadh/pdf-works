#!/usr/bin/env python3
import sys
import argparse
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

# --- helpers ---
NAMED_COLORS = {
    "black": (0, 0, 0),
    "white": (1, 1, 1),
    "red":   (1, 0, 0),
    "green": (0, 1, 0),
    "blue":  (0, 0, 1),
    "gray":  (0.5, 0.5, 0.5),
    "grey":  (0.5, 0.5, 0.5),
    "orange": (1.0, 0.5, 0.0),
    "purple": (0.5, 0.0, 0.5),
    "cyan": (0.0, 1.0, 1.0),
    "magenta": (1.0, 0.0, 1.0),
}

def parse_color(color_str: str):
    cs = color_str.strip().lower()
    if cs in NAMED_COLORS:
        return NAMED_COLORS[cs]
    if cs.startswith("#"):  # hex
        h = cs[1:]
        if len(h) == 3:
            r, g, b = (int(h[i]*2, 16) for i in range(3))
        elif len(h) == 6:
            r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
        else:
            raise ValueError("Hex color must be #RGB or #RRGGBB")
        return (r/255.0, g/255.0, b/255.0)
    raise ValueError(f"Unknown color '{color_str}'")

def create_border(page_width, page_height, margin=20, line_width=2, color=(0,0,0)):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    c.setLineWidth(line_width)
    c.setStrokeColorRGB(*color)
    c.rect(margin, margin, page_width - 2*margin, page_height - 2*margin, stroke=1, fill=0)
    c.save()
    packet.seek(0)
    return PdfReader(packet).pages[0]

def print_progress(current, total, bar_length=40):
    percent = current / total
    filled = int(bar_length * percent)
    bar = "#" * filled + "-" * (bar_length - filled)
    sys.stdout.write(f"\r[{bar}] {current}/{total} pages")
    sys.stdout.flush()

def add_borders(input_pdf, output_pdf, margin=20, color=(0,0,0), line_width=2):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    total = len(reader.pages)

    print(f"Processing '{input_pdf}' with {total} pages...")
    for i, page in enumerate(reader.pages, start=1):
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        overlay = create_border(w, h, margin=margin, line_width=line_width, color=color)
        page.merge_page(overlay)
        writer.add_page(page)
        print_progress(i, total)

    with open(output_pdf, "wb") as f:
        writer.write(f)

    sys.stdout.write("\n✅ Finished! Saved to '%s'\n" % output_pdf)

def main(argv=None):
    p = argparse.ArgumentParser(description="Add a border rectangle to all pages of a PDF.")
    p.add_argument("input", help="Input PDF path")
    p.add_argument("output", help="Output PDF path")
    p.add_argument("--margin", type=float, default=20.0, help="Border inset in points (default: 20pt ≈ 0.28in)")
    p.add_argument("--color", default="black", help="Border color (name or #RRGGBB). Default: black")
    p.add_argument("--width", type=float, default=2.0, help="Border line width in points. Default: 2")
    args = p.parse_args(argv)

    rgb = parse_color(args.color)
    add_borders(args.input, args.output, margin=args.margin, color=rgb, line_width=args.width)

if __name__ == "__main__":
    main()
