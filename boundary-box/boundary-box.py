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
import re
import yaml
import math

# Platform-specific imports for key handling
if sys.platform == 'win32':
    try:
        import msvcrt
    except ImportError:
        pass
else:
    try:
        import termios
        import tty
    except ImportError:
        pass

try:
    import fitz  # PyMuPDF for better quality handling
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

def load_config(config_path='config.yaml'):
    """Load configuration from YAML file"""
    default_config = {
        'border': {
            'style': 'rounded',
            'width': 1,
            'color': '0,0,0',
            'corner_radius': 10
        },
        'spacing': {
            'outer_margin': 0.5,
            'inner_padding': 0.25,
            'unit': 'inch'
        },
        'quality': {
            'mode': 'original',
            'dpi': 300,
            'preserve_ratio': True
        },
        'processing': {
            'pages': 'all',
            'confirm': True
        }
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                # Simply use the user config if it exists
                if user_config:
                    return user_config
        except Exception as e:
            print(f"⚠️  Error loading config file: {e}")
            print("   Using default configuration")
    
    return default_config

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
        percent = self.current / self.total if self.total > 0 else 1
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

def parse_page_range(page_range_str, total_pages):
    """
    Parse page range string and return list of page numbers (0-indexed)
    
    Examples:
        "1-5" -> [0, 1, 2, 3, 4]
        "1,3,5" -> [0, 2, 4]
        "1-3,7,9-10" -> [0, 1, 2, 6, 8, 9]
        "all" or None -> all pages
    """
    if not page_range_str or page_range_str.lower() == 'all':
        return list(range(total_pages))
    
    pages = set()
    
    # Split by comma
    parts = page_range_str.split(',')
    
    for part in parts:
        part = part.strip()
        
        # Check if it's a range (e.g., "1-5")
        if '-' in part:
            try:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                
                # Convert to 0-indexed and add to set
                for page in range(max(1, start), min(total_pages + 1, end + 1)):
                    pages.add(page - 1)
            except ValueError:
                print(f"⚠️  Invalid page range: {part}")
        else:
            # Single page number
            try:
                page_num = int(part)
                if 1 <= page_num <= total_pages:
                    pages.add(page_num - 1)
                else:
                    print(f"⚠️  Page {page_num} out of range (1-{total_pages})")
            except ValueError:
                print(f"⚠️  Invalid page number: {part}")
    
    return sorted(list(pages))

def create_visual_preview(outer_margin_ratio, inner_padding_ratio, border_color_rgb, 
                         border_style='solid', corner_radius_ratio=0, preserve_ratio=True):
    """
    Create an ASCII art preview of how the border will look
    """
    
    # Terminal dimensions for the preview (characters)
    preview_width = 60
    preview_height = 30
    
    # Calculate positions based on ratios
    outer_start = int(outer_margin_ratio * min(preview_width, preview_height))
    inner_start = outer_start + int(inner_padding_ratio * min(preview_width, preview_height))
    
    # Ensure minimum sizes
    outer_start = max(2, min(outer_start, 8))
    inner_start = outer_start + max(1, min(int(inner_padding_ratio * 20), 4))
    
    # Create the preview
    lines = []
    
    # Color indicator
    r, g, b = [int(c * 255) for c in border_color_rgb]
    if r > 200 and g < 100 and b < 100:
        color_name = "Red"
        border_char = "█"
    elif r < 100 and g > 200 and b < 100:
        color_name = "Green"
        border_char = "█"
    elif r < 100 and g < 100 and b > 200:
        color_name = "Blue"
        border_char = "█"
    elif r > 200 and g > 200 and b > 200:
        color_name = "White"
        border_char = "░"
    elif r < 50 and g < 50 and b < 50:
        color_name = "Black"
        border_char = "█"
    else:
        color_name = f"RGB({r},{g},{b})"
        border_char = "█"
    
    # Different characters for different styles
    if border_style == 'dashed':
        h_border = "─ "
        v_border = "┆"
    elif border_style == 'dotted':
        h_border = "·"
        v_border = "·"
    elif border_style == 'rounded':
        corner_chars = ['╭', '╮', '╰', '╯']
    else:
        h_border = border_char
        v_border = border_char
    
    # Build the preview line by line
    for y in range(preview_height):
        line = []
        for x in range(preview_width):
            # Determine what to display at this position
            if y == 0 or y == preview_height - 1:
                # Top/bottom page edge
                line.append("─")
            elif x == 0 or x == preview_width - 1:
                # Left/right page edge
                line.append("│")
            elif border_style == 'rounded' and (
                (y == outer_start and x == outer_start) or
                (y == outer_start and x == preview_width - outer_start - 1) or
                (y == preview_height - outer_start - 1 and x == outer_start) or
                (y == preview_height - outer_start - 1 and x == preview_width - outer_start - 1)
            ):
                # Rounded corners
                if y == outer_start and x == outer_start:
                    line.append('╭')
                elif y == outer_start and x == preview_width - outer_start - 1:
                    line.append('╮')
                elif y == preview_height - outer_start - 1 and x == outer_start:
                    line.append('╰')
                else:
                    line.append('╯')
            elif (y == outer_start or y == preview_height - outer_start - 1) and \
                 (outer_start < x < preview_width - outer_start - 1):
                # Horizontal border lines
                if border_style in ['dashed', 'dotted']:
                    line.append(h_border if x % 2 == 0 else " ")
                else:
                    line.append(border_char)
            elif (x == outer_start or x == preview_width - outer_start - 1) and \
                 (outer_start < y < preview_height - outer_start - 1):
                # Vertical border lines
                if border_style in ['dashed', 'dotted']:
                    line.append(v_border if y % 2 == 0 else " ")
                else:
                    line.append(border_char)
            elif (y == inner_start or y == preview_height - inner_start - 1) and \
                 (inner_start <= x < preview_width - inner_start):
                # Content area boundary (top/bottom)
                line.append("·")
            elif (x == inner_start or x == preview_width - inner_start - 1) and \
                 (inner_start <= y < preview_height - inner_start):
                # Content area boundary (left/right)
                line.append("·")
            elif inner_start < y < preview_height - inner_start - 1 and \
                 inner_start < x < preview_width - inner_start - 1:
                # Content area
                if y == preview_height // 2:
                    content_text = "PDF CONTENT"
                    text_start = (preview_width - len(content_text)) // 2
                    if text_start <= x < text_start + len(content_text):
                        line.append(content_text[x - text_start])
                    else:
                        line.append(" ")
                elif y == preview_height // 2 + 1:
                    content_text = "← scaled →" if not preserve_ratio else "← preserved →"
                    text_start = (preview_width - len(content_text)) // 2
                    if text_start <= x < text_start + len(content_text):
                        line.append(content_text[x - text_start])
                    else:
                        line.append(" ")
                else:
                    line.append(" ")
            else:
                # Empty space between margins
                line.append(" ")
        
        lines.append("".join(line))
    
    # Join lines with proper newlines
    preview_text = "\n📐 PREVIEW OF BORDER LAYOUT:\n\n"
    preview_text += "\n".join(lines)
    
    # Add legend
    preview_text += "\n\nLEGEND:\n"
    preview_text += f"  ─│ Page edges\n"
    if border_style == 'rounded':
        preview_text += f"  {border_char} Border ({color_name}, rounded corners)\n"
    else:
        preview_text += f"  {border_char} Border ({color_name}, {border_style})\n"
    preview_text += f"  · Content area boundary\n"
    preview_text += f"  ← Outer margin: from page edge to border\n"
    preview_text += f"  → Inner padding: from border to content\n"
    
    return preview_text

def display_settings(args, outer_margin_pts, inner_padding_pts, border_color, page_indices, total_pages):
    """Display the settings that will be applied with visual preview"""
    print("\n" + "="*60)
    print("📋 BORDER SETTINGS TO BE APPLIED")
    print("="*60)
    
    print(f"\n📁 Files:")
    print(f"  • Input:  {args.input_pdf} ({get_file_size_str(args.input_pdf)})")
    print(f"  • Output: {args.output_pdf}")
    
    # Display page range
    print(f"\n📄 Pages:")
    if len(page_indices) == total_pages:
        print(f"  • Processing: All pages (1-{total_pages})")
    else:
        # Format page ranges for display
        page_nums = [p + 1 for p in page_indices]  # Convert to 1-indexed
        if len(page_nums) <= 10:
            print(f"  • Processing: {', '.join(map(str, page_nums))} ({len(page_nums)} of {total_pages} pages)")
        else:
            # Show first and last few pages
            display_pages = page_nums[:3] + ['...'] + page_nums[-3:]
            print(f"  • Processing: {', '.join(map(str, display_pages))} ({len(page_nums)} of {total_pages} pages)")
    
    print(f"\n📐 Spacing:")
    print(f"  • Outer margin:  {args.outer:.2f} {args.unit} ({outer_margin_pts:.1f} pts)")
    print(f"  • Inner padding: {args.inner:.2f} {args.unit} ({inner_padding_pts:.1f} pts)")
    print(f"  • Total spacing: {args.outer + args.inner:.2f} {args.unit}")
    
    print(f"\n🎨 Border Style:")
    print(f"  • Style: {args.border_style.capitalize()}")
    print(f"  • Width: {args.border_width} pts")
    if args.border_style == 'rounded':
        print(f"  • Corner radius: {args.corner_radius} pts")
    color_rgb = tuple(int(c * 255) for c in border_color)
    print(f"  • Color: RGB{color_rgb}")
    
    print(f"\n⚙️  Quality Settings:")
    print(f"  • Quality mode: {args.quality.upper()}")
    if args.quality in ['high', 'medium']:
        print(f"  • DPI: {args.dpi}")
    print(f"  • Preserve aspect ratio: {'Yes' if not args.no_preserve_ratio else 'No'}")
    
    print("\n" + "="*60)
    
    # Get first page dimensions for ratio calculation
    try:
        reader = PdfReader(args.input_pdf)
        if len(reader.pages) > 0:
            # Use the first page from the selected range for preview
            first_page_idx = page_indices[0] if page_indices else 0
            page = reader.pages[first_page_idx]
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # Calculate ratios for preview
            outer_ratio = outer_margin_pts / min(page_width, page_height)
            inner_ratio = inner_padding_pts / min(page_width, page_height)
            corner_ratio = args.corner_radius / min(page_width, page_height) if args.border_style == 'rounded' else 0
            
            # Display visual preview
            preview = create_visual_preview(
                outer_ratio, 
                inner_ratio, 
                border_color,
                border_style=args.border_style,
                corner_radius_ratio=corner_ratio,
                preserve_ratio=not args.no_preserve_ratio
            )
            print(preview)
    except Exception as e:
        # If preview fails, continue without it
        print(f"(Preview generation skipped: {str(e)})")
    
    print("\n" + "="*60)

def confirm_proceed():
    """Ask user to confirm before proceeding"""
    print("\n❓ Do you want to proceed with these settings?")
    print("   • Press ENTER to continue")
    print("   • Press any other key to cancel")
    print()
    
    try:
        # For Windows
        if sys.platform == 'win32':
            import msvcrt
            print("   Waiting for input...", end='', flush=True)
            key = msvcrt.getch()
            print()  # New line after input
            
            # Check if Enter was pressed (carriage return)
            if key in [b'\r', b'\n']:
                print("✅ Proceeding with processing...")
                return True
            else:
                print("❌ Operation cancelled")
                return False
        
        # For Unix/Linux/Mac
        else:
            import termios, tty
            
            # Save terminal settings
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            try:
                # Set terminal to raw mode to read single character
                tty.setraw(sys.stdin.fileno())
                print("   Waiting for input...", end='', flush=True)
                key = sys.stdin.read(1)
                
                # Restore terminal settings before printing
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                print()  # New line after input
                
                # Check if Enter was pressed
                if key == '\r' or key == '\n':
                    print("✅ Proceeding with processing...")
                    return True
                else:
                    print("❌ Operation cancelled")
                    return False
                    
            finally:
                # Make sure terminal settings are restored
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled (Ctrl+C)")
        return False
    except Exception as e:
        # Fallback to simple input() if special key handling fails
        print("\n   (Press Enter to continue, Ctrl+C to cancel)")
        try:
            input()
            print("✅ Proceeding with processing...")
            return True
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled")
            return False

def process_pdf_high_quality(input_path, output_path, outer_margin, inner_padding, 
                            border_width, border_color, border_style='solid',
                            corner_radius=0, page_indices=None,
                            preserve_ratio=True, quality='original', dpi=300):
    """
    Process PDF using PyMuPDF for better quality preservation
    """
    
    print(f"\n📄 Reading '{input_path}'...")
    start_time = time.time()
    
    # Open with PyMuPDF for better quality handling
    doc = fitz.open(input_path)
    output_doc = fitz.open()
    
    total_pages = len(doc)
    
    # Use all pages if none specified
    if page_indices is None:
        page_indices = list(range(total_pages))
    
    input_size = get_file_size_str(input_path)
    
    print(f"Processing '{input_path}' ({len(page_indices)} of {total_pages} pages, {input_size})")
    print(f"Quality mode: {quality.upper()}", end="")
    if quality in ['high', 'medium']:
        print(f" | DPI: {dpi}")
    else:
        print()
    
    # Create progress bar
    progress = ProgressBar(len(page_indices), width=40, suffix='pages')
    
    for idx, page_num in enumerate(page_indices):
        progress.update(idx + 1)
        
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
            scale_factor = scale_x
        
        # Determine rendering quality
        if quality == 'high':
            mat = fitz.Matrix(scale_factor * (dpi/72), scale_factor * (dpi/72))
        elif quality == 'original':
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
        
        # Rectangle dimensions
        x0 = outer_margin
        y0 = outer_margin
        x1 = orig_width - outer_margin
        y1 = orig_height - outer_margin
        
        if border_style == 'rounded' and corner_radius > 0:
            # Limit corner radius to half the smaller dimension
            max_radius = min((x1 - x0) / 2, (y1 - y0) / 2, 50)  # Also limit to 50 points max
            actual_radius = min(corner_radius, max_radius)
            
            # Draw rounded rectangle using lines and arcs
            # We'll approximate rounded corners with multiple small lines
            
            # Top line
            shape.draw_line(fitz.Point(x0 + actual_radius, y0), 
                          fitz.Point(x1 - actual_radius, y0))
            
            # Top-right corner arc
            center = fitz.Point(x1 - actual_radius, y0 + actual_radius)
            for i in range(10):
                angle1 = -90 + i * 9
                angle2 = -90 + (i + 1) * 9
                rad1 = math.radians(angle1)
                rad2 = math.radians(angle2)
                p1 = fitz.Point(center.x + actual_radius * math.cos(rad1),
                              center.y + actual_radius * math.sin(rad1))
                p2 = fitz.Point(center.x + actual_radius * math.cos(rad2),
                              center.y + actual_radius * math.sin(rad2))
                shape.draw_line(p1, p2)
            
            # Right line
            shape.draw_line(fitz.Point(x1, y0 + actual_radius), 
                          fitz.Point(x1, y1 - actual_radius))
            
            # Bottom-right corner arc
            center = fitz.Point(x1 - actual_radius, y1 - actual_radius)
            for i in range(10):
                angle1 = 0 + i * 9
                angle2 = 0 + (i + 1) * 9
                rad1 = math.radians(angle1)
                rad2 = math.radians(angle2)
                p1 = fitz.Point(center.x + actual_radius * math.cos(rad1),
                              center.y + actual_radius * math.sin(rad1))
                p2 = fitz.Point(center.x + actual_radius * math.cos(rad2),
                              center.y + actual_radius * math.sin(rad2))
                shape.draw_line(p1, p2)
            
            # Bottom line
            shape.draw_line(fitz.Point(x1 - actual_radius, y1), 
                          fitz.Point(x0 + actual_radius, y1))
            
            # Bottom-left corner arc
            center = fitz.Point(x0 + actual_radius, y1 - actual_radius)
            for i in range(10):
                angle1 = 90 + i * 9
                angle2 = 90 + (i + 1) * 9
                rad1 = math.radians(angle1)
                rad2 = math.radians(angle2)
                p1 = fitz.Point(center.x + actual_radius * math.cos(rad1),
                              center.y + actual_radius * math.sin(rad1))
                p2 = fitz.Point(center.x + actual_radius * math.cos(rad2),
                              center.y + actual_radius * math.sin(rad2))
                shape.draw_line(p1, p2)
            
            # Left line
            shape.draw_line(fitz.Point(x0, y1 - actual_radius), 
                          fitz.Point(x0, y0 + actual_radius))
            
            # Top-left corner arc
            center = fitz.Point(x0 + actual_radius, y0 + actual_radius)
            for i in range(10):
                angle1 = 180 + i * 9
                angle2 = 180 + (i + 1) * 9
                rad1 = math.radians(angle1)
                rad2 = math.radians(angle2)
                p1 = fitz.Point(center.x + actual_radius * math.cos(rad1),
                              center.y + actual_radius * math.sin(rad1))
                p2 = fitz.Point(center.x + actual_radius * math.cos(rad2),
                              center.y + actual_radius * math.sin(rad2))
                shape.draw_line(p1, p2)
            
        else:  # solid, dashed, or dotted
            # Draw rectangle border
            border_rect = fitz.Rect(x0, y0, x1, y1)
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
                        border_width, border_color, border_style='solid',
                        corner_radius=0, page_indices=None, preserve_ratio=True):
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
    
    # Use all pages if none specified
    if page_indices is None:
        page_indices = list(range(total_pages))
    
    input_size = get_file_size_str(input_path)
    
    print(f"Processing '{input_path}' ({len(page_indices)} of {total_pages} pages, {input_size})")
    print("Quality mode: STANDARD (pypdf)")
    
    progress = ProgressBar(len(page_indices), width=40, suffix='pages')
    
    for idx, page_num in enumerate(page_indices):
        progress.update(idx + 1)
        
        page = reader.pages[page_num]
        
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
        
        if border_style == 'rounded' and corner_radius > 0:
            # Draw rounded rectangle
            max_radius = min((orig_width - 2 * outer_margin) / 2, 
                           (orig_height - 2 * outer_margin) / 2, 50)
            actual_radius = min(corner_radius, max_radius)
            
            c.roundRect(outer_margin, outer_margin, 
                       orig_width - 2 * outer_margin, 
                       orig_height - 2 * outer_margin,
                       actual_radius, stroke=1, fill=0)
                       
        elif border_style == 'dashed':
            c.setDash([6, 3])  # 6 points on, 3 points off
            c.rect(outer_margin, outer_margin, 
                  orig_width - 2 * outer_margin, 
                  orig_height - 2 * outer_margin,
                  stroke=1, fill=0)
                  
        elif border_style == 'dotted':
            c.setDash([2, 2])  # 2 points on, 2 points off
            c.rect(outer_margin, outer_margin, 
                  orig_width - 2 * outer_margin, 
                  orig_height - 2 * outer_margin,
                  stroke=1, fill=0)
        else:  # solid
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
    # Load configuration
    config = load_config()
    
    parser = argparse.ArgumentParser(
        description='Add customizable borders to PDF pages with quality preservation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with defaults from config.yaml
  python border_scale.py input.pdf output.pdf
  
  # Process specific pages only
  python border_scale.py input.pdf output.pdf --pages 1-5,10,15-20
  
  # Override border style
  python border_scale.py input.pdf output.pdf --border-style solid
  
  # Custom margins and rounded corners
  python border_scale.py input.pdf output.pdf --outer 1.0 --inner 0.5 --corner-radius 15
  
  # Skip confirmation prompt
  python border_scale.py input.pdf output.pdf -y

Border Styles:
  - rounded: Rounded corners (default)
  - solid: Square corners
  - dashed: Dashed lines (reportlab only)
  - dotted: Dotted lines (reportlab only)

Page Range Examples:
  --pages 1-5        Process pages 1 through 5
  --pages 1,3,5      Process pages 1, 3, and 5
  --pages 1-3,7-10   Process pages 1-3 and 7-10
  --pages all        Process all pages (default)
        """
    )
    
    parser.add_argument('input_pdf', help='Input PDF file path')
    parser.add_argument('output_pdf', help='Output PDF file path')
    
    # Page range option
    parser.add_argument('--pages', '--page-range', type=str, 
                       default=config['processing']['pages'],
                       help=f'Page range to process (default: {config["processing"]["pages"]})')
    
    # Spacing options
    parser.add_argument('--outer', '--outer-margin', type=float, 
                       default=config['spacing']['outer_margin'],
                       help=f'Outer margin: space from page edge to border (default: {config["spacing"]["outer_margin"]})')
    parser.add_argument('--inner', '--inner-padding', type=float, 
                       default=config['spacing']['inner_padding'],
                       help=f'Inner padding: space from border to content (default: {config["spacing"]["inner_padding"]})')
    parser.add_argument('--unit', choices=['inch', 'mm', 'pt'], 
                       default=config['spacing']['unit'],
                       help=f'Unit for margins (default: {config["spacing"]["unit"]})')
    
    # Border appearance
    parser.add_argument('--border-style', choices=['solid', 'rounded', 'dashed', 'dotted'], 
                       default=config['border']['style'],
                       help=f'Border style (default: {config["border"]["style"]})')
    parser.add_argument('--border-width', type=float, 
                       default=config['border']['width'],
                       help=f'Border line width in points (default: {config["border"]["width"]})')
    parser.add_argument('--border-color', type=str, 
                       default=config['border']['color'],
                       help=f'Border color as R,G,B (0-255 each, default: "{config["border"]["color"]}")')
    parser.add_argument('--corner-radius', type=float, 
                       default=config['border']['corner_radius'],
                       help=f'Corner radius for rounded borders (default: {config["border"]["corner_radius"]})')
    
    # Quality options
    parser.add_argument('--quality', choices=['original', 'high', 'medium', 'standard'], 
                       default=config['quality']['mode'],
                       help=f'Quality preservation mode (default: {config["quality"]["mode"]})')
    parser.add_argument('--dpi', type=int, 
                       default=config['quality']['dpi'],
                       help=f'DPI for rendering when using high/medium quality (default: {config["quality"]["dpi"]})')
    
    # Scaling options
    parser.add_argument('--no-preserve-ratio', action='store_true',
                       default=not config['quality']['preserve_ratio'],
                       help='Stretch content to fit (may distort)')
    
    # Confirmation
    parser.add_argument('-y', '--yes', action='store_true',
                       help='Skip confirmation prompt')
    
    # Config file
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to configuration file (default: config.yaml)')
    
    args = parser.parse_args()
    
    # Reload config if different file specified
    if args.config != 'config.yaml':
        config = load_config(args.config)
    
    # Check if input file exists
    if not os.path.exists(args.input_pdf):
        print(f"❌ Error: Input file '{args.input_pdf}' not found")
        sys.exit(1)
    
    # Get total pages and parse page range
    try:
        reader = PdfReader(args.input_pdf)
        total_pages = len(reader.pages)
        page_indices = parse_page_range(args.pages, total_pages)
        
        if not page_indices:
            print(f"❌ Error: No valid pages specified in range '{args.pages}'")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
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
    
    # Display settings with visual preview
    display_settings(args, outer_margin_pts, inner_padding_pts, border_color, page_indices, total_pages)
    
    # Ask for confirmation unless -y flag is used or config says to skip
    if not args.yes and config['processing']['confirm']:
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
                border_style=args.border_style,
                corner_radius=args.corner_radius,
                page_indices=page_indices,
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
                border_style=args.border_style,
                corner_radius=args.corner_radius,
                page_indices=page_indices,
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