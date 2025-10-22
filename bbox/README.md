# BBox

A powerful Python tool for adding customizable borders, page numbers, and titles to PDF pages while preserving content quality. Scale your PDF content to fit within borders with precise control over spacing, quality, and appearance.

## Features

- 📐 **Dual Spacing Control**: Separate control for outer margin (page edge to border) and inner padding (border to content)
- 🎨 **Customizable Borders**: Multiple border styles including rounded corners, solid, dashed, and dotted
- 📑 **Page Numbering**: Flexible page number formatting and positioning
- 📝 **Document Titles**: Add titles from PDF metadata or custom text
- 📊 **Quality Preservation**: Multiple quality modes to maintain document fidelity
- 📈 **Real-time Progress**: Visual progress bar with detailed status
- 🔄 **Aspect Ratio Control**: Preserve or stretch content as needed
- 📏 **Multiple Units**: Support for inches, millimeters, and points
- ✅ **Settings Preview**: Review all settings before processing with visual ASCII preview
- 👁️ **Visual Layout Preview**: See exactly how borders will look before processing
- 📄 **Page Range Selection**: Process specific pages or page ranges
- ⌨️ **Intuitive Confirmation**: Simple Enter/any-key confirmation system
- ⚙️ **Configuration File**: YAML-based configuration for default settings
- 💾 **Standalone Binary**: Available as executable for deployment without Python

## Installation

### Option 1: Using Python
```bash
pip install -r requirements.txt
```

### Option 2: Using Pre-built Binary
Download the latest release from the releases page:
- Windows: `bbox.exe`
- Linux/Mac: `bbox`

### Option 3: Build Your Own Binary
```bash
pip install pyinstaller
pyinstaller --onefile --icon=bbox.ico --name=bbox bbox.py
```

## Configuration

BBox uses a `config.yaml` file for default settings. If not present, built-in defaults are used.

### Default Configuration (config.yaml)
```yaml
# BBox Configuration

# Border appearance
border:
  style: "rounded"        # Options: solid, rounded, dashed, dotted
  width: 1               # Border line width in points
  color: "0,0,0"        # RGB color (0-255 each)
  corner_radius: 5      # Corner radius in points (for rounded style)

# Spacing
spacing:
  outer_margin: 0.1      # Space from page edge to border
  inner_padding: 0.1    # Space from border to content
  unit: "inch"          # Options: inch, mm, pt

# Quality settings
quality:
  mode: "original"       # Options: original, high, medium, standard
  dpi: 300              # DPI for high/medium quality modes
  preserve_ratio: true   # Preserve aspect ratio

# Page numbers
page_numbers:
  enabled: true          # Enable/disable page numbers
  format: "{n}/{total}"  # Format string: {n} = current page, {total} = total pages
  position: "bottom-right"  # Options: top-left, top-center, top-right, bottom-left, bottom-center, bottom-right
  location: "outside"    # Options: inside (within border), outside (outside border)
  font_size: 10         # Font size in points
  font_color: "0,0,0"   # RGB color (0-255 each)
  font_family: "Helvetica"  # Font family
  margin: 20            # Distance from edge in points
  start_number: 1       # Starting page number
  skip_first: 0         # Number of first pages to skip numbering
  skip_last: 0          # Number of last pages to skip numbering

# Document title
title:
  enabled: false         # Enable/disable title
  text: ""              # Title text (leave empty to extract from PDF metadata)
  position: "top-center" # Options: top-left, top-center, top-right, bottom-left, bottom-center, bottom-right
  location: "inside"    # Options: inside (within border), outside (outside border)
  font_size: 12         # Font size in points
  font_color: "0,0,0"   # RGB color (0-255 each)
  font_family: "Helvetica-Bold"  # Font family
  margin: 25            # Distance from edge in points
  only_first_page: true # Show title only on first page

# Processing
processing:
  pages: "all"          # Page range: all, or specific like "1-5,10,15-20"
  confirm: true         # Show confirmation prompt (false to skip)
```

## Quick Start

### Using Python Script
```bash
python bbox.py input.pdf output.pdf
```

### Using Binary
```bash
# Windows
bbox.exe input.pdf output.pdf

# Linux/Mac
./bbox input.pdf output.pdf
```

### Override Config Settings
```bash
python bbox.py input.pdf output.pdf --border-style solid --corner-radius 10
```

### Process Specific Pages
```bash
python bbox.py input.pdf output.pdf --pages 1-10
```

### Skip Confirmation
```bash
python bbox.py input.pdf output.pdf -y
```

## Command Line Options

### Required Arguments
| Argument | Description |
|----------|-------------|
| `input_pdf` | Path to input PDF file |
| `output_pdf` | Path to output PDF file |

### Page Selection
| Option | Default | Description |
|--------|---------|-------------|
| `--pages` | all | Page range to process (e.g., "1-5", "1,3,5", "1-3,7-10") |

### Spacing Options
| Option | Default | Description |
|--------|---------|-------------|
| `--outer` | 0.1 (from config) | Outer margin (space from page edge to border) |
| `--inner` | 0.1 (from config) | Inner padding (space from border to content) |
| `--unit` | inch (from config) | Unit for measurements: `inch`, `mm`, or `pt` |

### Border Styling
| Option | Default | Description |
|--------|---------|-------------|
| `--border-style` | rounded (from config) | Border style: `rounded`, `solid`, `dashed`, `dotted` |
| `--border-width` | 1 (from config) | Border line width in points |
| `--border-color` | 0,0,0 (from config) | Border color as RGB (0-255 each) |
| `--corner-radius` | 5 (from config) | Corner radius for rounded borders (in points) |

### Quality Settings
| Option | Default | Description |
|--------|---------|-------------|
| `--quality` | original (from config) | Quality mode: `original`, `high`, `medium`, `standard` |
| `--dpi` | 300 (from config) | DPI for rendering (high/medium quality modes) |
| `--no-preserve-ratio` | False | Stretch content to fit (may distort) |

### Other Options
| Option | Description |
|--------|-------------|
| `-y`, `--yes` | Skip confirmation prompt |
| `--config` | Path to custom config file (default: config.yaml) |

## Page Numbering

### Format Strings
- `{n}/{total}` → "1/10", "2/10"
- `Page {n} of {total}` → "Page 1 of 10"
- `{n}` → "1", "2"
- `- {n} -` → "- 1 -"

### Positioning Options
- **Position**: top-left, top-center, top-right, bottom-left, bottom-center, bottom-right
- **Location**: inside or outside the border
- **Skip Options**: Skip first/last pages, custom start number

## Document Titles

Add titles from PDF metadata or custom text:
- Automatic extraction from PDF metadata
- Custom text override
- Position control (same as page numbers)
- First page only or all pages

## Border Styles

### Rounded (Default)
```bash
python bbox.py input.pdf output.pdf --border-style rounded --corner-radius 10
```

### Solid
```bash
python bbox.py input.pdf output.pdf --border-style solid
```

### Dashed (standard mode only)
```bash
python bbox.py input.pdf output.pdf --border-style dashed --quality standard
```

### Dotted (standard mode only)
```bash
python bbox.py input.pdf output.pdf --border-style dotted --quality standard
```

## Usage Examples

### 1. Basic Border with Page Numbers
```bash
python bbox.py document.pdf output.pdf
```

### 2. Custom Page Format in Config
```yaml
page_numbers:
  format: "Page {n} of {total}"
  position: "bottom-center"
```

### 3. Add Title to First Page
```yaml
title:
  enabled: true
  text: "Annual Report 2024"
  position: "top-center"
```

### 4. Process Page Range
```bash
python bbox.py document.pdf output.pdf --pages 1-10,15,20-25
```

### 5. Minimal Margins
```bash
python bbox.py document.pdf output.pdf --outer 0.05 --inner 0.05
```

### 6. Colored Border
```bash
python bbox.py document.pdf output.pdf --border-color "0,0,255" --border-width 2
```

### 7. High Quality for Images
```bash
python bbox.py document.pdf output.pdf --quality high --dpi 600
```

### 8. Skip First 2 Pages for Numbering
```yaml
page_numbers:
  skip_first: 2
  start_number: 1
```

### 9. Batch Processing
```bash
python bbox.py input.pdf output.pdf -y
```

### 10. Custom Config
```bash
python bbox.py input.pdf output.pdf --config production.yaml
```

## Building Standalone Binary

### Install PyInstaller
```bash
pip install pyinstaller
```

### Build Command
```bash
pyinstaller --onefile --icon=bbox.ico --name=bbox bbox.py
```

### Platform-Specific Builds

#### Windows
```bash
pyinstaller --onefile --icon=bbox.ico --name=bbox.exe --add-data="config.yaml;." bbox.py
```

#### Linux/Mac
```bash
pyinstaller --onefile --name=bbox --add-data="config.yaml:." bbox.py
```

The binary will be in `dist/` folder after building.

## Output Example

```
============================================================
📋 BBOX - SETTINGS TO BE APPLIED
============================================================

📁 Files:
  • Input:  document.pdf (47.9MB)
  • Output: output.pdf

📄 Pages:
  • Processing: All pages (1-514)

📐 Spacing:
  • Outer margin:  0.10 inch (7.2 pts)
  • Inner padding: 0.10 inch (7.2 pts)
  • Total spacing: 0.20 inch

🎨 Border Style:
  • Style: Rounded
  • Width: 1 pts
  • Corner radius: 5 pts
  • Color: RGB(0, 0, 0)

📑 Page Numbers:
  • Format: {n}/{total}
  • Position: bottom-right (outside border)
  • Font: Helvetica, 10pt

⚙️  Quality Settings:
  • Quality mode: ORIGINAL
  • Preserve aspect ratio: Yes

============================================================

[ASCII Preview Here]

============================================================

❓ Do you want to proceed with these settings?
   • Press ENTER to continue
   • Press any other key to cancel

✅ Proceeding with processing...

📄 Reading 'document.pdf'...
Processing 'document.pdf' (514 of 514 pages, 47.9MB)
Quality mode: ORIGINAL
[########################################] 514/514 pages
💾 Saving PDF with quality preservation...
✅ Saved 'output.pdf' (48.2MB)
⏱️  Processing time: 45.23 seconds
```

## Quality Modes

- **original**: Preserves vector graphics (best for text)
- **high**: High-quality rasterization (best for mixed content)
- **medium**: Balanced quality and speed
- **standard**: Basic processing (fallback mode)

## Requirements

- Python 3.6+
- pypdf 3.1.0+
- reportlab 4.0.0+
- pymupdf 1.23.0+ (optional, for advanced features)
- pyyaml 6.0+

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request