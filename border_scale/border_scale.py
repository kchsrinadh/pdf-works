#!/usr/bin/env python3
"""
PDF Border Scaler - Add customizable borders to PDF pages with quality preservation
Usage: python border_scale.py input.pdf output.pdf [options]
"""

import argparse
import sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject, ArrayObject, NameObject, DictionaryObject
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
import io
import os
import time

try:
    import fitz  # PyMuPDF for better quality handling
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

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

def display_settings(args, outer_margin_pts, inner_padding_pts, border_color):
    """Display the settings that will be applied"""
    print("\n" + "="*60)
    print("📋 BORDER SETTINGS TO BE APPLIED")
    print("="*60)
    
    print(f"\n📁 Files:")
    print(f"  • Input:  {args.input_pdf} ({get_file_size_str(args.input_pdf)})")
    print(f"  • Output: {args.output_pdf}")
    
    print(f"\n📐 Spacing:")
    print(f"  • Outer margin:  {args.outer:.2f} {args.unit} ({outer_margin_pts:.1f} pts)")
    print(f"  • Inner padding: {args.inner:.2f} {args.unit} ({inner_padding_pts:.1f} pts)")
    print(f"  • Total spacing: {args.outer + args.inner:.2f} {args.unit}")
    
    print(f"\n🎨 Border Style:")
    print(f"  • Width: {args.border_width} pts")
    color_rgb = tuple(int(c * 255) for c in border_color)
    print(f"  • Color: RGB{color_rgb}")
    
    print(f"\n⚙️  Quality Settings:")
    print(f"  • Quality mode: {args.quality.upper()}")
    if args.quality in ['high', 'medium']:
        print(f"  • DPI: {args.dpi}")
    print(f"  • Preserve aspect ratio: {'Yes' if not args.no_preserve_ratio else 'No'}")
    
    print("\n" + "="*60)

def confirm_proceed():
    """Ask user to confirm before proceeding"""
    print("\n❓ Do you want to proceed with these settings?")
    print("   Press Enter to continue, or Ctrl+C to cancel...")
    try:
        input()
        return True
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        return False

def process_pdf_high_quality(input_path, output_path, outer_margin, inner_padding, 
                            border_width, border_color, preserve_ratio=True, 
                            quality='high', dpi=300):
    """
    Process PDF using PyMuPDF for better quality preservation
    """
    
    print(f"\n📄 Reading '{input_path}'...")
    start_time = time.time()
    
    # Open with PyMuPDF for better quality handling
    doc = fitz.open(input_path)
    output_doc = fitz.open()
    
    total_pages = len(doc)
    input_size = get_file_size_str(input_path)
    
    print(f"Processing '{input_path}' ({total_pages} pages, {input_size})")
    print(f"Quality mode: {quality.upper()} | DPI: {dpi}")
    
    # Create progress bar
    progress = ProgressBar(total_pages, width=40, suffix='pages')
    
    for page_num in range(total_pages):
        progress.update(page_num + 1)
        
        # Get the page
        page = doc[page_num]
        rect = page.rect
        
        # Calculate dimensions
        orig_width = rect.width
        orig_height = rect.height
        
        # Total margin calculation
        total_margin = outer_margin + inner_padding
        available_width = orig_width - 2 * total_margin
        available_height = orig_height - 2 * total_margin
        
        # Calculate scale factor
        scale_x = available_width / orig_width
        scale_y = available_height / orig_height
        
        if preserve_ratio:
            scale_factor = min(scale_x, scale_y)
        else:
            scale_factor = scale_x  # Will handle x/y separately
        
        # Determine rendering quality
        if quality == 'high':
            mat = fitz.Matrix(scale_factor * (dpi/72), scale_factor * (dpi/72))
        elif quality == 'original':
            # Keep original without rasterization
            mat = fitz.Matrix(scale_factor, scale_factor)
        else:  # medium
            mat = fitz.Matrix(scale_factor * 2, scale_factor * 2)
        
        # Create new page with same dimensions
        new_page = output_doc.new_page(width=orig_width, height=orig_height)
        
        # Calculate position for centered content
        if preserve_ratio:
            scaled_width = orig_width * scale_factor
            scaled_height = orig_height * scale_factor
            x_offset = total_margin + (available_width - scaled_width) / 2
            y_offset = total_margin + (available_height - scaled_height) / 2
        else:
            x_offset = total_margin
            y_offset = total_margin
        
        # Method 1: Direct vector preservation (best quality for vector content)
        if quality == 'original':
            # This preserves vectors as vectors
            xref = new_page.show_pdf_page(
                fitz.Rect(x_offset, y_offset, 
                         x_offset + orig_width * scale_factor,
                         y_offset + orig_height * scale_factor),
                doc, 
                page_num
            )
        else:
            # Method 2: High-quality rasterization (for mixed content)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Insert the pixmap into the new page
            new_page.insert_image(
                fitz.Rect(x_offset, y_offset,
                         x_offset + available_width,
                         y_offset + available_height),
                pixmap=pix
            )
        
        # Draw border
        shape = new_page.new_shape()
        
        # Convert border color from 0-1 to 0-255
        border_rgb = tuple(int(c * 255) for c in border_color)
        
        # Draw rectangle border
        border_rect = fitz.Rect(
            outer_margin,
            outer_margin,
            orig_width - outer_margin,
            orig_height - outer_margin
        )
        
        shape.draw_rect(border_rect)
        shape.finish(width=border_width, color=border_rgb, fill=None)
        shape.commit()
    
    # Save with optimization
    print("💾 Saving PDF with quality preservation...")
    
    # Save options for quality - using only valid PyMuPDF options
    save_options = {
        'garbage': 4,  # Maximum garbage collection
        'deflate': True,  # Compress streams
        'clean': True,  # Clean up redundant objects
    }
    
    output_doc.save(output_path, **save_options)
    
    # Close documents
    doc.close()
    output_doc.close()
    
    # Calculate processing time
    end_time = time.time()
    processing_time = end_time - start_time
    output_size = get_file_size_str(output_path)
    
    # Print success message
    print(f"✅ Saved '{output_path}' ({output_size})")
    print(f"⏱️  Processing time: {processing_time:.2f} seconds")

def process_pdf_standard(input_path, output_path, outer_margin, inner_padding, 
                        border_width, border_color, preserve_ratio=True):
    """
    Standard processing using pypdf (fallback method)
    """
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    
    print(f"\n📄 Reading '{input_path}'...")
    start_time = time.time()
    
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    # Set compression
    writer.compress_identical_objects(remove_use_as=True)
    
    total_pages = len(reader.pages)
    input_size = get_file_size_str(input_path)
    
    print(f"Processing '{input_path}' ({total_pages} pages, {input_size})")
    print("Using standard quality mode (pypdf)")
    
    progress = ProgressBar(total_pages, width=40, suffix='pages')
    
    for page_num, page in enumerate(reader.pages):
        progress.update(page_num + 1)
        
        # Get original page dimensions
        page_box = page.mediabox
        orig_width = float(page_box.width)
        orig_height = float(page_box.height)
        
        # Calculate available space
        total_margin = outer_margin + inner_padding
        available_width = orig_width - 2 * total_margin
        available_height = orig_height - 2 * total_margin
        
        # Calculate scale factor
        scale_x = available_width / orig_width
        scale_y = available_height / orig_height
        
        if preserve_ratio:
            scale_factor = min(scale_x, scale_y)
            scaled_width = orig_width * scale_factor
            scaled_height = orig_height * scale_factor
            translate_x = total_margin + (available_width - scaled_width) / 2
            translate_y = total_margin + (available_height - scaled_height) / 2
            
            # Apply transformation
            page.add_transformation([scale_factor, 0, 0, scale_factor, translate_x, translate_y])
        else:
            translate_x = total_margin
            translate_y = total_margin
            page.add_transformation([scale_x, 0, 0, scale_y, translate_x, translate_y])
        
        # Create border
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(orig_width, orig_height))
        c.setStrokeColorRGB(*border_color)
        c.setLineWidth(border_width)
        c.rect(outer_margin, outer_margin, 
               orig_width - 2 * outer_margin, 
               orig_height - 2 * outer_margin,
               stroke=1, fill=0)
        c.save()
        packet.seek(0)
        
        border_pdf = PdfReader(packet)
        border_page = border_pdf.pages[0]
        
        # Merge pages
        new_page = writer.add_blank_page(width=orig_width, height=orig_height)
        new_page.merge_page(page)
        new_page.merge_page(border_page)
    
    # Save output
    print("💾 Saving PDF...")
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    
    end_time = time.time()
    processing_time = end_time - start_time
    output_size = get_file_size_str(output_path)
    
    print(f"✅ Saved '{output_path}' ({output_size})")
    print(f"⏱️  Processing time: {processing_time:.2f} seconds")

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
        description='Add customizable borders to PDF pages with quality preservation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with high quality
  python border_scale.py input.pdf output.pdf
  
  # Maximum quality preservation (keeps vectors as vectors)
  python border_scale.py input.pdf output.pdf --quality original
  
  # High quality with custom DPI
  python border_scale.py input.pdf output.pdf --quality high --dpi 600
  
  # Custom margins
  python border_scale.py input.pdf output.pdf --outer 1.0 --inner 0.5
  
  # Skip confirmation prompt
  python border_scale.py input.pdf output.pdf -y

Quality Modes:
  - original: Preserves vector graphics as vectors (best for text/drawings)
  - high: High-quality rendering at specified DPI (default 300)
  - medium: Balanced quality and file size
  - standard: Use pypdf method (fallback)
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
    
    # Quality options
    parser.add_argument('--quality', choices=['original', 'high', 'medium', 'standard'], 
                       default='high',
                       help='Quality preservation mode (default: high)')
    parser.add_argument('--dpi', type=int, default=300,
                       help='DPI for rendering when using high/medium quality (default: 300)')
    
    # Scaling options
    parser.add_argument('--no-preserve-ratio', action='store_true',
                       help='Stretch content to fit (may distort)')
    
    # Confirmation
    parser.add_argument('-y', '--yes', action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_pdf):
        print(f"❌ Error: Input file '{args.input_pdf}' not found")
        sys.exit(1)
    
    # Convert units to points
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
    
    # Display settings
    display_settings(args, outer_margin_pts, inner_padding_pts, border_color)
    
    # Ask for confirmation unless -y flag is used
    if not args.yes:
        if not confirm_proceed():
            sys.exit(0)
    
    try:
        # Check if PyMuPDF is available for high-quality processing
        if args.quality != 'standard' and PYMUPDF_AVAILABLE:
            process_pdf_high_quality(
                args.input_pdf,
                args.output_pdf,
                outer_margin_pts,
                inner_padding_pts,
                args.border_width,
                border_color,
                preserve_ratio=not args.no_preserve_ratio,
                quality=args.quality,
                dpi=args.dpi
            )
        else:
            if args.quality != 'standard' and not PYMUPDF_AVAILABLE:
                print("⚠️  PyMuPDF not installed. Using standard quality.")
                print("   Install with: pip install pymupdf")
            process_pdf_standard(
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
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()