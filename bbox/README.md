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
- 🚀 **Auto Output Naming**: Automatically generates output filename when not specified
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

BBox uses a `config.yaml` file for default settings. If not present, built-in defaults are used. The config file is searched in multiple locations:
- Same directory as the executable (for binary version)
- Current working directory
- Script directory (for Python version)

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
  output_suffix: "_bbox"  # Suffix for auto-generated output filenames
```

## Quick Start

### Basic Usage - Auto Output
```bash
# Automatically creates input_bbox.pdf
python bbox.py input.pdf

# Or with binary
bbox input.pdf
```

### Specify Output File
```bash
python bbox.py input.pdf output.pdf

# Or with binary
bbox input.pdf output.pdf
```

### Override Config Settings
```bash
bbox input.pdf --border-style solid --corner-radius 10
```

### Process Specific Pages
```bash
bbox input.pdf --pages 1-10
```

### Skip Confirmation
```bash
bbox input.pdf -y
```

## Command Line Options

### Required Arguments
| Argument | Description |
|----------|-------------|
| `input_pdf` | Path to input PDF file |
| `output_pdf` | Path to output PDF file (optional, auto-generated with suffix if not provided) |

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

## Output Filename Generation

When no output file is specified, BBox automatically generates one:
- Default pattern: `input_filename` + `_bbox` + `.pdf`
- Example: `document.pdf` → `document_bbox.pdf`
- The suffix can be customized in `config.yaml` under `processing.output_suffix`

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
bbox input.pdf --border-style rounded --corner-radius 10
```

### Solid
```bash
bbox input.pdf --border-style solid
```

### Dashed (standard mode only)
```bash
bbox input.pdf --border-style dashed --quality standard
```

### Dotted (standard mode only)
```bash
bbox input.pdf --border-style dotted --quality standard
```

## Usage Examples

### 1. Quick Border Addition (Auto Output)
```bash
bbox document.pdf
# Creates: document_bbox.pdf
```

### 2. Custom Output Location
```bash
bbox /path/to/input.pdf /different/path/output.pdf
```

### 3. Process Specific Pages with Auto Output
```bash
bbox document.pdf --pages 1-10,15,20-25
# Creates: document_bbox.pdf with only specified pages
```

### 4. Minimal Margins for Maximum Content
```bash
bbox document.pdf --outer 0.05 --inner 0.05
```

### 5. Colored Border with Page Numbers
```bash
bbox document.pdf --border-color "0,0,255" --border-width 2
```

### 6. High Quality for Images
```bash
bbox document.pdf --quality high --dpi 600
```

### 7. Custom Config and Output
```bash
bbox document.pdf output.pdf --config production.yaml
```

### 8. Batch Processing Without Confirmation
```bash
bbox input.pdf -y
```

### 9. Custom Page Number Format
Edit config.yaml:
```yaml
page_numbers:
  format: "Page {n} of {total}"
  position: "bottom-center"
```

### 10. Add Title to First Page
Edit config.yaml:
```yaml
title:
  enabled: true
  text: "Annual Report 2024"
  position: "top-center"
```

## Building Standalone Binary

### Windows Build
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --icon=bbox.ico --name=bbox.exe bbox.py

# Copy files
Copy-Item "dist\bbox.exe" "$env:LOCALAPPDATA\bbox\bbox.exe" -Force
Copy-Item "config.yaml" "$env:LOCALAPPDATA\bbox\config.yaml" -Force
setx BBOX "%LOCALAPPDATA%\bbox\bbox"

```

### Linux/Mac Build
```bash
# Build executable
pyinstaller --onefile --name=bbox bbox.py

# Make executable
chmod +x dist/bbox

# Install system-wide (requires sudo)
sudo cp dist/bbox /usr/local/bin/
sudo cp config.yaml /usr/local/share/bbox/

# Or install for current user
mkdir -p ~/.local/bin
cp dist/bbox ~/.local/bin/
mkdir -p ~/.config/bbox
cp config.yaml ~/.config/bbox/
```

## Output Example

```
============================================================
📋 BBOX - SETTINGS TO BE APPLIED
============================================================

📁 Files:
  • Input:  document.pdf (47.9MB)
  • Output: document_bbox.pdf

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

[ASCII Preview of Border Layout]

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
✅ Saved 'document_bbox.pdf' (48.2MB)
⏱️  Processing time: 45.23 seconds
```

## Quality Modes

- **original**: Preserves vector graphics (best for text)
- **high**: High-quality rasterization (best for mixed content)
- **medium**: Balanced quality and speed
- **standard**: Basic processing (fallback mode)

## Troubleshooting

### Config File Not Found
- For binary: Place `config.yaml` in the same directory as `bbox.exe`
- For Python: Place in current directory or script directory
- Use `--config` to specify a custom location

### Page Numbers Not Showing
- Check that `page_numbers.enabled` is `true` in config
- Verify the format string contains `{n}` placeholder
- Check position isn't placing text outside visible area

### Binary Not Working
- Ensure all dependencies are included in the build
- Check antivirus isn't blocking the executable
- Try running from command line to see error messages

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
3. Submit a pull request with description
