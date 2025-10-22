#!/usr/bin/env python3
"""
BoundaryBox - Add customizable borders to PDF pages with quality preservation
Usage: python boundary-box.py input.pdf output.pdf [options]
"""

import argparse
import sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject, ArrayObject, NameObject, DictionaryObject
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
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
        'page_numbers': {
            'enabled': False,
            'format': 'Page {n} of {total}',
            'position': 'bottom-center',
            'location': 'outside',
            'font_size': 10,
            'font_color': '0,0,0',
            'font_family': 'Helvetica',
            'margin': 20,
            'start_number': 1,
            'skip_first': 0,
            'skip_last': 0
        },
        'title': {
            'enabled': False,
            'text': '',
            'position': 'top-center',
            'location': 'inside',
            'font_size': 12,
            'font_color': '0,0,0',
            'font_family': 'Helvetica-Bold',
            'margin': 25,
            'only_first_page': True
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
    """Parse page range string and return list of page numbers (0-indexed)"""
    if not page_range_str or page_range_str.lower() == 'all':
        return list(range(total_pages))
    
    pages = set()
    parts = page_range_str.split(',')
    
    for part in parts:
        part = part.strip()
        
        if '-' in part:
            try:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                
                for page in range(max(1, start), min(total_pages + 1, end + 1)):
                    pages.add(page - 1)
            except ValueError:
                print(f"⚠️  Invalid page range: {part}")
        else:
            try:
                page_num = int(part)
                if 1 <= page_num <= total_pages:
                    pages.add(page_num - 1)
                else:
                    print(f"⚠️  Page {page_num} out of range (1-{total_pages})")
            except ValueError:
                print(f"⚠️  Invalid page number: {part}")
    
    return sorted(list(pages))

def format_page_number(format_string, current_page, total_pages):
    """Format page number string"""
    if not format_string:
        return ""
    
    # Replace {n} with current page number
    result = format_string.replace("{n}", str(current_page))
    
    # Replace {total} with total pages
    result = result.replace("{total}", str(total_pages))
    
    # If format doesn't contain {n}, don't show anything
    if "{n}" not in format_string and str(current_page) not in result:
        return ""
    
    return result

def calculate_text_position(position, location, page_width, page_height, 
                           outer_margin, text_width, text_height, margin):
    """Calculate x, y coordinates for text placement (PDF coordinates: bottom-left origin)"""
    
    # Determine base position based on location (inside/outside border)
    if location == 'inside':
        # Inside the border
        left_bound = outer_margin + margin
        right_bound = page_width - outer_margin - margin
        top_bound = page_height - outer_margin - margin  
        bottom_bound = outer_margin + margin
    else:
        # Outside the border
        left_bound = margin
        right_bound = page_width - margin
        top_bound = page_height - margin
        bottom_bound = margin
    
    # Calculate x position
    if 'left' in position:
        x = left_bound
    elif 'right' in position:
        x = right_bound - text_width
    else:  # center
        x = (page_width - text_width) / 2
    
    # Calculate y position (PDF coordinates - bottom is 0, top is page_height)
    if 'top' in position:
        y = top_bound - text_height  # Near top of page
    elif 'bottom' in position:
        y = bottom_bound  # Near bottom of page
    else:  # center
        y = (page_height) / 2
    
    return x, y

def add_page_elements_pymupdf(page, page_num, total_pages, config, outer_margin, doc_title=""):
    """Add page numbers and title using PyMuPDF"""
    page_width = page.rect.width
    page_height = page.rect.height
    
    # Add page numbers
    if config['page_numbers']['enabled']:
        skip_first = config['page_numbers'].get('skip_first', 0)
        skip_last = config['page_numbers'].get('skip_last', 0)
        
        if page_num > skip_first and page_num <= (total_pages - skip_last):
            start_number = config['page_numbers'].get('start_number', 1)
            display_page_num = start_number + page_num - 1 - skip_first
            
            text = format_page_number(
                config['page_numbers']['format'],
                display_page_num,
                total_pages - skip_first - skip_last
            )
            
            if text:
                color_parts = config['page_numbers']['font_color'].split(',')
                color = tuple(int(c) / 255.0 for c in color_parts)
                
                font_size = config['page_numbers']['font_size']
                margin = config['page_numbers']['margin']
                
                # Estimate text dimensions
                text_width = len(text) * font_size * 0.5
                text_height = font_size
                
                # Calculate position
                x, y = calculate_text_position(
                    config['page_numbers']['position'],
                    config['page_numbers']['location'],
                    page_width, page_height, outer_margin,
                    text_width, text_height, margin
                )
                
                # PyMuPDF uses top-left origin, so we need to convert Y coordinate
                # PDF y=0 is bottom, PyMuPDF y=0 is top
                pymupdf_y = page_height - y
                
                # Insert text
                page.insert_text(
                    fitz.Point(x, pymupdf_y),
                    text,
                    fontsize=font_size,
                    color=color,
                    fontname='helv'
                )
    
    # Add title
    if config['title']['enabled']:
        if not config['title'].get('only_first_page', True) or page_num == 1:
            title_text = config['title'].get('text', '') or doc_title
            
            if title_text:
                color_parts = config['title']['font_color'].split(',')
                color = tuple(int(c) / 255.0 for c in color_parts)
                
                font_size = config['title']['font_size']
                margin = config['title']['margin']
                
                # Estimate text dimensions
                text_width = len(title_text) * font_size * 0.4
                text_height = font_size
                
                # Calculate position
                x, y = calculate_text_position(
                    config['title']['position'],
                    config['title']['location'],
                    page_width, page_height, outer_margin,
                    text_width, text_height, margin
                )
                
                # PyMuPDF uses top-left origin, convert Y coordinate
                pymupdf_y = page_height - y
                
                # Insert text
                page.insert_text(
                    fitz.Point(x, pymupdf_y),
                    title_text,
                    fontsize=font_size,
                    color=color,
                    fontname='hebo'
                )

def add_page_elements_reportlab(c, page_num, total_pages, config, outer_margin, 
                                page_width, page_height, doc_title=""):
    """Add page numbers and title using ReportLab"""
    
    # Add page numbers
    if config['page_numbers']['enabled']:
        skip_first = config['page_numbers'].get('skip_first', 0)
        skip_last = config['page_numbers'].get('skip_last', 0)
        
        if page_num > skip_first and page_num <= (total_pages - skip_last):
            start_number = config['page_numbers'].get('start_number', 1)
            display_page_num = start_number + page_num - 1 - skip_first
            
            text = format_page_number(
                config['page_numbers']['format'],
                display_page_num,
                total_pages - skip_first - skip_last
            )
            
            if text:
                color_parts = config['page_numbers']['font_color'].split(',')
                c.setFillColorRGB(*(int(c) / 255.0 for c in color_parts))
                
                font_family = config['page_numbers'].get('font_family', 'Helvetica')
                font_size = config['page_numbers']['font_size']
                c.setFont(font_family, font_size)
                
                text_width = c.stringWidth(text, font_family, font_size)
                text_height = font_size
                
                margin = config['page_numbers']['margin']
                x, y = calculate_text_position(
                    config['page_numbers']['position'],
                    config['page_numbers']['location'],
                    page_width, page_height, outer_margin,
                    text_width, text_height, margin
                )
                
                # ReportLab uses bottom-left origin (same as PDF)
                c.drawString(x, y, text)
    
    # Add title
    if config['title']['enabled']:
        if not config['title'].get('only_first_page', True) or page_num == 1:
            title_text = config['title'].get('text', '') or doc_title
            
            if title_text:
                color_parts = config['title']['font_color'].split(',')
                c.setFillColorRGB(*(int(c) / 255.0 for c in color_parts))
                
                font_family = config['title'].get('font_family', 'Helvetica-Bold')
                font_size = config['title']['font_size']
                c.setFont(font_family, font_size)
                
                text_width = c.stringWidth(title_text, font_family, font_size)
                text_height = font_size
                
                margin = config['title']['margin']
                x, y = calculate_text_position(
                    config['title']['position'],
                    config['title']['location'],
                    page_width, page_height, outer_margin,
                    text_width, text_height, margin
                )
                
                # ReportLab uses bottom-left origin
                c.drawString(x, y, title_text)

def get_pdf_title(pdf_path):
    """Extract title from PDF metadata"""
    try:
        reader = PdfReader(pdf_path)
        if reader.metadata and '/Title' in reader.metadata:
            return reader.metadata['/Title']
    except:
        pass
    return ""

def create_visual_preview(outer_margin_ratio, inner_padding_ratio, border_color_rgb, 
                         border_style='solid', corner_radius_ratio=0, preserve_ratio=True):
    """Create an ASCII art preview of how the border will look"""
    
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

def display_settings(args, outer_margin_pts, inner_padding_pts, border_color, 
                    page_indices, total_pages, config):
    """Display the settings that will be applied with visual preview"""
    print("\n" + "="*60)
    print("📋 BOUNDARYBOX - SETTINGS TO BE APPLIED")
    print("="*60)
    
    print(f"\n📁 Files:")
    print(f"  • Input:  {args.input_pdf} ({get_file_size_str(args.input_pdf)})")
    print(f"  • Output: {args.output_pdf}")
    
    # Display page range
    print(f"\n📄 Pages:")
    if len(page_indices) == total_pages:
        print(f"  • Processing: All pages (1-{total_pages})")
    else:
        page_nums = [p + 1 for p in page_indices]
        if len(page_nums) <= 10:
            print(f"  • Processing: {', '.join(map(str, page_nums))} ({len(page_nums)} of {total_pages} pages)")
        else:
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
    
    # Display page numbers settings if enabled
    if config['page_numbers']['enabled']:
        print(f"\n📑 Page Numbers:")
        print(f"  • Format: {config['page_numbers']['format']}")
        print(f"  • Position: {config['page_numbers']['position']} ({config['page_numbers']['location']} border)")
        print(f"  • Font: {config['page_numbers']['font_family']}, {config['page_numbers']['font_size']}pt")
    
    # Display title settings if enabled
    if config['title']['enabled']:
        print(f"\n📝 Title:")
        title_text = config['title'].get('text', '') or "[From PDF metadata]"
        print(f"  • Text: {title_text}")
        print(f"  • Position: {config['title']['position']} ({config['title']['location']} border)")
        print(f"  • Font: {config['title']['font_family']}, {config['title']['font_size']}pt")
        if config['title'].get('only_first_page', True):
            print(f"  • Display: First page only")
    
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
            first_page_idx = page_indices[0] if page_indices else 0
            page = reader.pages[first_page_idx]
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            outer_ratio = outer_margin_pts / min(page_width, page_height)
            inner_ratio = inner_padding_pts / min(page_width, page_height)
            corner_ratio = args.corner_radius / min(page_width, page_height) if args.border_style == 'rounded' else 0
            
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
        print(f"(Preview generation skipped: {str(e)})")
    
    print("\n" + "="*60)

def confirm_proceed():
    """Ask user to confirm before proceeding"""
    print("\n❓ Do you want to proceed with these settings?")
    print("   • Press ENTER to continue")
    print("   • Press any other key to cancel")
    print()
    
    try:
        if sys.platform == 'win32':
            import msvcrt
            print("   Waiting for input...", end='', flush=True)
            key = msvcrt.getch()
            print()
            
            if key in [b'\r', b'\n']:
                print("✅ Proceeding with processing...")
                return True
            else:
                print("❌ Operation cancelled")
                return False
        else:
            import termios, tty
            
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            try:
                tty.setraw(sys.stdin.fileno())
                print("   Waiting for input...", end='', flush=True)
                key = sys.stdin.read(1)
                
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                print()
                
                if key == '\r' or key == '\n':
                    print("✅ Proceeding with processing...")
                    return True
                else:
                    print("❌ Operation cancelled")
                    return False
                    
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled (Ctrl+C)")
        return False
    except Exception as e:
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
                            preserve_ratio=True, quality='original', dpi=300, config=None):
    """Process PDF using PyMuPDF for better quality preservation"""
    
    print(f"\n📄 Reading '{input_path}'...")
    start_time = time.time()
    
    # Get document title
    doc_title = get_pdf_title(input_path) if config else ""
    
    # Open with PyMuPDF for better quality handling
    doc = fitz.open(input_path)
    output_doc = fitz.open()
    
    total_pages = len(doc)
    
    if page_indices is None:
        page_indices = list(range(total_pages))
    
    input_size = get_file_size_str(input_path)
    
    print(f"Processing '{input_path}' ({len(page_indices)} of {total_pages} pages, {input_size})")
    print(f"Quality mode: {quality.upper()}", end="")
    if quality in ['high', 'medium']:
        print(f" | DPI: {dpi}")
    else:
        print()
    
    progress = ProgressBar(len(page_indices), width=40, suffix='pages')
    
    for idx, page_num in enumerate(page_indices):
        progress.update(idx + 1)
        
        page = doc[page_num]
        rect = page.rect
        
        orig_width = rect.width
        orig_height = rect.height
        
        total_margin = outer_margin + inner_padding
        available_width = orig_width - 2 * total_margin
        available_height = orig_height - 2 * total_margin
        
        scale_x = available_width / orig_width
        scale_y = available_height / orig_height
        
        if preserve_ratio:
            scale_factor = min(scale_x, scale_y)
        else:
            scale_factor = scale_x
        
        if quality == 'high':
            mat = fitz.Matrix(scale_factor * (dpi/72), scale_factor * (dpi/72))
        elif quality == 'original':
            mat = fitz.Matrix(scale_factor, scale_factor)
        else:
            mat = fitz.Matrix(scale_factor * 2, scale_factor * 2)
        
        new_page = output_doc.new_page(width=orig_width, height=orig_height)
        
        if preserve_ratio:
            scaled_width = orig_width * scale_factor
            scaled_height = orig_height * scale_factor
            x_offset = total_margin + (available_width - scaled_width) / 2
            y_offset = total_margin + (available_height - scaled_height) / 2
        else:
            x_offset = total_margin
            y_offset = total_margin
        
        if quality == 'original':
            xref = new_page.show_pdf_page(
                fitz.Rect(x_offset, y_offset, 
                         x_offset + orig_width * scale_factor,
                         y_offset + orig_height * scale_factor),
                doc, 
                page_num
            )
        else:
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            new_page.insert_image(
                fitz.Rect(x_offset, y_offset,
                         x_offset + available_width,
                         y_offset + available_height),
                pixmap=pix
            )
        
        # Draw border
        shape = new_page.new_shape()
        
        border_rgb = tuple(int(c * 255) for c in border_color)
        
        x0 = outer_margin
        y0 = outer_margin
        x1 = orig_width - outer_margin
        y1 = orig_height - outer_margin
        
        if border_style == 'rounded' and corner_radius > 0:
            max_radius = min((x1 - x0) / 2, (y1 - y0) / 2, 50)
            actual_radius = min(corner_radius, max_radius)
            
            # Draw rounded rectangle with lines and arcs
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
            
        else:
            border_rect = fitz.Rect(x0, y0, x1, y1)
            shape.draw_rect(border_rect)
        
        shape.finish(width=border_width, color=border_rgb, fill=None)
        shape.commit()
        
        # Add page numbers and title if configured
        if config:
            add_page_elements_pymupdf(new_page, idx + 1, len(page_indices), 
                                     config, outer_margin, doc_title)
    
    print("💾 Saving PDF with quality preservation...")
    
    save_options = {
        'garbage': 4,
        'deflate': True,
        'clean': True,
    }
    
    output_doc.save(output_path, **save_options)
    
    doc.close()
    output_doc.close()
    
    end_time = time.time()
    processing_time = end_time - start_time
    output_size = get_file_size_str(output_path)
    
    print(f"✅ Saved '{output_path}' ({output_size})")
    print(f"⏱️  Processing time: {processing_time:.2f} seconds")

def process_pdf_standard(input_path, output_path, outer_margin, inner_padding, 
                        border_width, border_color, border_style='solid',
                        corner_radius=0, page_indices=None, preserve_ratio=True, config=None):
    """Standard processing using pypdf (fallback method)"""
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    
    print(f"\n📄 Reading '{input_path}'...")
    start_time = time.time()
    
    # Get document title
    doc_title = get_pdf_title(input_path) if config else ""
    
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    writer.compress_identical_objects(remove_use_as=True)
    
    total_pages = len(reader.pages)
    
    if page_indices is None:
        page_indices = list(range(total_pages))
    
    input_size = get_file_size_str(input_path)
    
    print(f"Processing '{input_path}' ({len(page_indices)} of {total_pages} pages, {input_size})")
    print("Quality mode: STANDARD (pypdf)")
    
    progress = ProgressBar(len(page_indices), width=40, suffix='pages')
    
    for idx, page_num in enumerate(page_indices):
        progress.update(idx + 1)
        
        page = reader.pages[page_num]
        
        page_box = page.mediabox
        orig_width = float(page_box.width)
        orig_height = float(page_box.height)
        
        total_margin = outer_margin + inner_padding
        available_width = orig_width - 2 * total_margin
        available_height = orig_height - 2 * total_margin
        
        scale_x = available_width / orig_width
        scale_y = available_height / orig_height
        
        if preserve_ratio:
            scale_factor = min(scale_x, scale_y)
            scaled_width = orig_width * scale_factor
            scaled_height = orig_height * scale_factor
            translate_x = total_margin + (available_width - scaled_width) / 2
            translate_y = total_margin + (available_height - scaled_height) / 2
            
            page.add_transformation([scale_factor, 0, 0, scale_factor, translate_x, translate_y])
        else:
            translate_x = total_margin
            translate_y = total_margin
            page.add_transformation([scale_x, 0, 0, scale_y, translate_x, translate_y])
        
        # Create border with page elements
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(orig_width, orig_height))
        c.setStrokeColorRGB(*border_color)
        c.setLineWidth(border_width)
        
        if border_style == 'rounded' and corner_radius > 0:
            max_radius = min((orig_width - 2 * outer_margin) / 2, 
                           (orig_height - 2 * outer_margin) / 2, 50)
            actual_radius = min(corner_radius, max_radius)
            
            c.roundRect(outer_margin, outer_margin, 
                       orig_width - 2 * outer_margin, 
                       orig_height - 2 * outer_margin,
                       actual_radius, stroke=1, fill=0)
                       
        elif border_style == 'dashed':
            c.setDash([6, 3])
            c.rect(outer_margin, outer_margin, 
                  orig_width - 2 * outer_margin, 
                  orig_height - 2 * outer_margin,
                  stroke=1, fill=0)
                  
        elif border_style == 'dotted':
            c.setDash([2, 2])
            c.rect(outer_margin, outer_margin, 
                  orig_width - 2 * outer_margin, 
                  orig_height - 2 * outer_margin,
                  stroke=1, fill=0)
        else:
            c.rect(outer_margin, outer_margin, 
                  orig_width - 2 * outer_margin, 
                  orig_height - 2 * outer_margin,
                  stroke=1, fill=0)
        
        # Add page numbers and title if configured
        if config:
            add_page_elements_reportlab(c, idx + 1, len(page_indices), config, 
                                       outer_margin, orig_width, orig_height, doc_title)
        
        c.save()
        packet.seek(0)
        
        border_pdf = PdfReader(packet)
        border_page = border_pdf.pages[0]
        
        new_page = writer.add_blank_page(width=orig_width, height=orig_height)
        new_page.merge_page(page)
        new_page.merge_page(border_page)
    
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
    config = load_config()
    
    parser = argparse.ArgumentParser(
        description='BoundaryBox - Add customizable borders to PDF pages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with defaults from config.yaml
  python boundary-box.py input.pdf output.pdf
  
  # Process specific pages only
  python boundary-box.py input.pdf output.pdf --pages 1-5,10,15-20
  
  # Override border style
  python boundary-box.py input.pdf output.pdf --border-style solid
  
  # Custom margins and rounded corners
  python boundary-box.py input.pdf output.pdf --outer 1.0 --inner 0.5 --corner-radius 15
  
  # Skip confirmation prompt
  python boundary-box.py input.pdf output.pdf -y

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
    
    parser.add_argument('--pages', '--page-range', type=str, 
                       default=config['processing']['pages'],
                       help=f'Page range to process (default: {config["processing"]["pages"]})')
    
    parser.add_argument('--outer', '--outer-margin', type=float, 
                       default=config['spacing']['outer_margin'],
                       help=f'Outer margin: space from page edge to border (default: {config["spacing"]["outer_margin"]})')
    parser.add_argument('--inner', '--inner-padding', type=float, 
                       default=config['spacing']['inner_padding'],
                       help=f'Inner padding: space from border to content (default: {config["spacing"]["inner_padding"]})')
    parser.add_argument('--unit', choices=['inch', 'mm', 'pt'], 
                       default=config['spacing']['unit'],
                       help=f'Unit for margins (default: {config["spacing"]["unit"]})')
    
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
    
    parser.add_argument('--quality', choices=['original', 'high', 'medium', 'standard'], 
                       default=config['quality']['mode'],
                       help=f'Quality preservation mode (default: {config["quality"]["mode"]})')
    parser.add_argument('--dpi', type=int, 
                       default=config['quality']['dpi'],
                       help=f'DPI for rendering when using high/medium quality (default: {config["quality"]["dpi"]})')
    
    parser.add_argument('--no-preserve-ratio', action='store_true',
                       default=not config['quality']['preserve_ratio'],
                       help='Stretch content to fit (may distort)')
    
    parser.add_argument('-y', '--yes', action='store_true',
                       help='Skip confirmation prompt')
    
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to configuration file (default: config.yaml)')
    
    args = parser.parse_args()
    
    if args.config != 'config.yaml':
        config = load_config(args.config)
    
    if not os.path.exists(args.input_pdf):
        print(f"❌ Error: Input file '{args.input_pdf}' not found")
        sys.exit(1)
    
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
    
    unit_multipliers = {
        'inch': 72,
        'mm': 72 / 25.4,
        'pt': 1
    }
    
    multiplier = unit_multipliers[args.unit]
    outer_margin_pts = args.outer * multiplier
    inner_padding_pts = args.inner * multiplier
    
    border_color = parse_color(args.border_color)
    
    display_settings(args, outer_margin_pts, inner_padding_pts, border_color, 
                    page_indices, total_pages, config)
    
    if not args.yes and config['processing']['confirm']:
        if not confirm_proceed():
            sys.exit(0)
    
    try:
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
                dpi=args.dpi,
                config=config
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
                preserve_ratio=not args.no_preserve_ratio,
                config=config
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