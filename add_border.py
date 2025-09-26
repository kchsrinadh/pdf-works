#!/usr/bin/env python3
"""
PDF Border Scaler - Add customizable borders to PDF pages
Usage: python border_scale.py input.pdf output.pdf [options]
"""

import argparse
import sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject, ArrayObject
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
import io
import os
import time

class ProgressBar:
    """Simple progress bar for console output"""
    
    def __init__(self, total, width=40, prefix='', suffix=''):
        self.total = total
        self.width = width
        self.prefix = prefix
        self.suffix = suffix
        self.current = 0
        
    def update(self, current):
        self.current = current
        self.display()
    
    def display(self):
        percent = self.current / self.total
        filled = int(self.width * percent)
        bar = '#' * filled + '-' * (self.width - filled)
        
        # Clear the line and write progress
        sys.stdout.write('\r')
        sys.stdout.write(f'{self.prefix}[{bar}] {self.current}/{self.total} {self.suffix}')
        sys.stdout.flush()
        
        if self.current == self.total:
            sys.stdout.write('\n')

def get_file_size_str(file_path):
    """Get human-readable file size"""
    size = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}TB"

def create_border_page(width, height, outer_margin, inner_padding, border_width=1, border_color=(0, 0, 0)):
    """
    Create a PDF page with just a border
    
    Args:
        width, height: Page dimensions in points
        outer_margin: Space from page edge to border (points)
        inner_padding: Space from border to content (points)
        border_width: Border line width in points
        border_color: RGB tuple (0-1 range)
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))
    
    # Set border color and width
    c.setStrokeColorRGB(*border_color)
    c.setLineWidth(border_width)
    
    # Draw rectangle border
    # The border is positioned at outer_margin from the edges
    c.rect(
        outer_margin,
        outer_margin,
        width - 2 * outer_margin,
        height - 2 * outer_margin,
        stroke=1,
        fill=0
    )
    
    c.save()
    packet.seek(0)
    return packet

def scale_and_center_content(page, scale_factor, translate_x, translate_y):
    """
    Scale and translate page content
    """
    # Create transformation matrix for scaling and translation
    # Matrix format: [scale_x, 0, 0, scale_y, translate_x, translate_y]
    page.add_transformation([scale_factor, 0, 0, scale_factor, translate_x, translate_y])
    return page

def process_pdf(input_path, output_path, outer_margin, inner_padding, border_width, border_color, preserve_ratio=True):
    """
    Process PDF to add borders with specified margins and padding
    
    Args:
        input_path: Input PDF file path
        output_path: Output PDF file path
        outer_margin: Space from page edge to border (points)
        inner_padding: Space from border to content (points)
        border_width: Border line width
        border_color: Border color as RGB tuple
        preserve_ratio: Whether to preserve aspect ratio when scaling
    """
    
    # Read input file and get info
    print(f"📄 Reading '{input_path}'...")
    start_time = time.time()
    
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    total_pages = len(reader.pages)
    input_size = get_file_size_str(input_path)
    
    print(f"Processing '{input_path}' ({total_pages} pages, {input_size})")
    
    # Create progress bar
    progress = ProgressBar(total_pages, width=40, suffix='pages')
    
    for page_num, page in enumerate(reader.pages):
        # Update progress
        progress.update(page_num + 1)
        
        # Get original page dimensions
        page_box = page.mediabox
        orig_width = float(page_box.width)
        orig_height = float(page_box.height)
        
        # Calculate the available space for content inside the border
        # Total margin on each side = outer_margin + inner_padding
        total_margin = outer_margin + inner_padding
        available_width = orig_width - 2 * total_margin
        available_height = orig_height - 2 * total_margin
        
        # Calculate scale factor
        scale_x = available_width / orig_width
        scale_y = available_height / orig_height
        
        if preserve_ratio:
            # Use the smaller scale factor to maintain aspect ratio
            scale_factor = min(scale_x, scale_y)
            
            # Calculate the scaled dimensions
            scaled_width = orig_width * scale_factor
            scaled_height = orig_height * scale_factor
            
            # Center the content within the available space
            translate_x = total_margin + (available_width - scaled_width) / 2
            translate_y = total_margin + (available_height - scaled_height) / 2
        else:
            # Stretch to fit (may distort content)
            scale_factor = 1  # We'll use different x and y scales
            translate_x = total_margin
            translate_y = total_margin
            
            # Apply different scaling for x and y
            page.add_transformation([scale_x, 0, 0, scale_y, translate_x, translate_y])
        
        if preserve_ratio:
            # Apply uniform scaling
            scaled_page = scale_and_center_content(page, scale_factor, translate_x, translate_y)
        else:
            scaled_page = page
        
        # Create border overlay
        border_stream = create_border_page(
            orig_width, 
            orig_height, 
            outer_margin, 
            inner_padding, 
            border_width,
            border_color
        )
        
        # Create a new page with the border
        border_pdf = PdfReader(border_stream)
        border_page = border_pdf.pages[0]
        
        # Merge the scaled content with the border
        # First add the scaled content, then overlay the border
        new_page = writer.add_blank_page(width=orig_width, height=orig_height)
        new_page.merge_page(scaled_page)
        new_page.merge_page(border_page)
    
    # Save the output
    print("💾 Saving PDF...")
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    
    # Calculate processing time
    end_time = time.time()
    processing_time = end_time - start_time
    output_size = get_file_size_str(output_path)
    
    # Print success message
    print(f"✅ Saved '{output_path}' ({output_size})")
    print(f"⏱️  Processing time: {processing_time:.2f} seconds")
    print(f"\n📊 Border settings applied:")
    print(f"  • Outer margin: {outer_margin:.1f} pts ({outer_margin/72:.2f}″)")
    print(f"  • Inner padding: {inner_padding:.1f} pts ({inner_padding/72:.2f}″)")
    print(f"  • Border width: {border_width} pts")

def parse_color(color_string):
    """Parse color string in format 'R,G,B' where values are 0-255"""
    try:
        parts = color_string.split(',')
        if len(parts) != 3:
            raise ValueError
        r, g, b = [int(x) / 255.0 for x in parts]
        return (r, g, b)
    except:
        print(f"⚠️  Invalid color format: {color_string}. Using black.")
        return (0, 0, 0)

def main():
    parser = argparse.ArgumentParser(
        description='Add customizable borders to PDF pages with margin and padding control',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default settings (0.5 inch outer, 0.25 inch inner)
  python border_scale.py input.pdf output.pdf
  
  # Custom margins in inches
  python border_scale.py input.pdf output.pdf --outer 1.0 --inner 0.5
  
  # Custom margins in millimeters
  python border_scale.py input.pdf output.pdf --outer 25 --inner 10 --unit mm
  
  # Custom border appearance
  python border_scale.py input.pdf output.pdf --border-width 2 --border-color "255,0,0"
  
  # Stretch content (may distort)
  python border_scale.py input.pdf output.pdf --no-preserve-ratio

Units:
  - inch: inches (default)
  - mm: millimeters
  - pt: points (1/72 inch)
        """
    )
    
    parser.add_argument('input_pdf', help='Input PDF file path')
    parser.add_argument('output_pdf', help='Output PDF file path')
    
    # Spacing options
    parser.add_argument('--outer', '--outer-margin', type=float, default=0.5,
                       help='Outer margin: space from page edge to border (default: 0.5)')
    parser.add_argument('--inner', '--inner-padding', type=float, default=0.25,
                       help='Inner padding: space from border to content (default: 0.25)')
    parser.add_argument('--unit', choices=['inch', 'mm', 'pt'], default='inch',
                       help='Unit for margins (default: inch)')
    
    # Border appearance
    parser.add_argument('--border-width', type=float, default=1,
                       help='Border line width in points (default: 1)')
    parser.add_argument('--border-color', type=str, default='0,0,0',
                       help='Border color as R,G,B (0-255 each, default: "0,0,0" for black)')
    
    # Scaling options
    parser.add_argument('--no-preserve-ratio', action='store_true',
                       help='Stretch content to fit (may distort)')
    
    # Display options
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Minimal output')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_pdf):
        print(f"❌ Error: Input file '{args.input_pdf}' not found")
        sys.exit(1)
    
    # Convert units to points (PDF's native unit)
    unit_multipliers = {
        'inch': 72,
        'mm': 72 / 25.4,
        'pt': 1
    }
    
    multiplier = unit_multipliers[args.unit]
    outer_margin_pts = args.outer * multiplier
    inner_padding_pts = args.inner * multiplier
    
    # Parse border color
    border_color = parse_color(args.border_color)
    
    try:
        process_pdf(
            args.input_pdf,
            args.output_pdf,
            outer_margin_pts,
            inner_padding_pts,
            args.border_width,
            border_color,
            preserve_ratio=not args.no_preserve_ratio
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error processing PDF: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()