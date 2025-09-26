# BoundaryBox

A powerful Python tool for adding customizable borders to PDF pages while preserving content quality. Scale your PDF content to fit within borders with precise control over spacing, quality, and appearance.

## Features

- 📐 **Dual Spacing Control**: Separate control for outer margin (page edge to border) and inner padding (border to content)
- 🎨 **Customizable Borders**: Multiple border styles including rounded corners, solid, dashed, and dotted
- 📊 **Quality Preservation**: Multiple quality modes to maintain document fidelity
- 📈 **Real-time Progress**: Visual progress bar with detailed status
- 🔄 **Aspect Ratio Control**: Preserve or stretch content as needed
- 📏 **Multiple Units**: Support for inches, millimeters, and points
- ✅ **Settings Preview**: Review all settings before processing with visual ASCII preview
- 👁️ **Visual Layout Preview**: See exactly how borders will look before processing
- 📄 **Page Range Selection**: Process specific pages or page ranges
- ⌨️ **Intuitive Confirmation**: Simple Enter/any-key confirmation system
- ⚙️ **Configuration File**: YAML-based configuration for default settings

## Installation

### Using pip
```bash
pip install -r requirements.txt
```

### Manual Installation
```bash
pip install pypdf>=3.1.0 reportlab>=4.0.0 pymupdf>=1.23.0 pyyaml>=6.0
```

### Requirements File (requirements.txt)
```
pypdf>=3.1.0
reportlab>=4.0.0
pymupdf>=1.23.0
pyyaml>=6.0
```

## Configuration

BoundaryBox uses a `config.yaml` file for default settings. If not present, built-in defaults are used.

### Default Configuration (config.yaml)
```yaml
# BoundaryBox Configuration

# Border appearance
border:
  style: "rounded"        # Options: solid, rounded, dashed, dotted
  width: 1               # Border line width in points
  color: "0,0,0"        # RGB color (0-255 each)
  corner_radius: 5      # Corner radius in points (for rounded style)

# Spacing
spacing:
  outer_margin: 0.5      # Space from page edge to border
  inner_padding: 0.25    # Space from border to content
  unit: "inch"          # Options: inch, mm, pt

# Quality settings
quality:
  mode: "original"       # Options: original, high, medium, standard
  dpi: 300              # DPI for high/medium quality modes
  preserve_ratio: true   # Preserve aspect ratio

# Processing
processing:
  pages: "all"          # Page range: all, or specific like "1-5,10,15-20"
  confirm: true         # Show confirmation prompt (false to skip)
```

## Quick Start

### Basic Usage
```bash
python boundary-box.py input.pdf output.pdf
```
Uses all settings from config.yaml


## Output Example

```
============================================================
📋 BORDER SETTINGS TO BE APPLIED
============================================================

📁 Files:
  • Input:  input.pdf (47.9MB)
  • Output: output.pdf

📄 Pages:
  • Processing: All pages (1-514)

📐 Spacing:
  • Outer margin:  0.50 inch (36.0 pts)
  • Inner padding: 0.25 inch (18.0 pts)
  • Total spacing: 0.75 inch

🎨 Border Style:
  • Style: Rounded
  • Width: 1 pts
  • Corner radius: 5 pts
  • Color: RGB(0, 0, 0)

⚙️  Quality Settings:
  • Quality mode: ORIGINAL
  • Preserve aspect ratio: Yes

============================================================

📐 PREVIEW OF BORDER LAYOUT:

────────────────────────────────────────────────────────────
│                                                          │
│ ╭████████████████████████████████████████████████████╮  │
│ █                                                    █  │
│ █  ·············································     █  │
│ █  ·                                           ·     █  │
│ █  ·                                           ·     █  │
│ █  ·                                           ·     █  │
│ █  ·              PDF CONTENT                  ·     █  │
│ █  ·             ← preserved →                 ·     █  │
│ █  ·                                           ·     █  │
│ █  ·                                           ·     █  │
│ █  ·············································     █  │
│ █                                                    █  │
│ ╰████████████████████████████████████████████████████╯  │
│                                                          │
────────────────────────────────────────────────────────────

LEGEND:
  ─│ Page edges
  █ Border (Black, rounded corners)
  · Content area boundary
  ← Outer margin: from page edge to border
  → Inner padding: from border to content

============================================================

❓ Do you want to proceed with these settings?
   • Press ENTER to continue
   • Press any other key to cancel

   Waiting for input...
✅ Proceeding with processing...

📄 Reading 'document.pdf'...
Processing 'document.pdf' (514 of 514 pages, 47.9MB)
Quality mode: ORIGINAL
[########################################] 514/514 pages
💾 Saving PDF with quality preservation...
✅ Saved 'output.pdf' (48.2MB)
⏱️  Processing time: 45.23 seconds
```



### Override Config Settings
```bash
python boundary-box.py input.pdf output.pdf --border-style solid --corner-radius 10
```

### Process Specific Pages
```bash
python boundary-box.py input.pdf output.pdf --pages 1-10
```

### Skip Confirmation
```bash
python boundary-box.py input.pdf output.pdf -y
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
| `--outer` | 0.5 (from config) | Outer margin (space from page edge to border) |
| `--inner` | 0.25 (from config) | Inner padding (space from border to content) |
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

## Border Styles

### Rounded (Default)
Creates borders with smooth, rounded corners. Corner radius is configurable.
```bash
python boundary-box.py input.pdf output.pdf --border-style rounded --corner-radius 10
```

### Solid
Traditional rectangular borders with sharp corners.
```bash
python boundary-box.py input.pdf output.pdf --border-style solid
```

### Dashed
Borders with dashed lines (only available in standard/reportlab mode).
```bash
python boundary-box.py input.pdf output.pdf --border-style dashed --quality standard
```

### Dotted
Borders with dotted lines (only available in standard/reportlab mode).
```bash
python boundary-box.py input.pdf output.pdf --border-style dotted --quality standard
```

## Usage Examples

### 1. Basic Border Addition
Use all defaults from config.yaml:
```bash
python boundary-box.py document.pdf output.pdf
```

### 2. Custom Rounded Corners
Adjust corner radius for rounded borders:
```bash
python boundary-box.py document.pdf output.pdf --corner-radius 15
```

### 3. Square Borders
Use solid borders instead of rounded:
```bash
python boundary-box.py document.pdf output.pdf --border-style solid
```

### 4. Process Specific Pages
First 10 pages only:
```bash
python boundary-box.py document.pdf output.pdf --pages 1-10
```

### 5. Custom Spacing
Large outer margin with minimal inner padding:
```bash
python boundary-box.py document.pdf output.pdf --outer 1.5 --inner 0.1
```

### 6. Metric Units
Using millimeters:
```bash
python boundary-box.py document.pdf output.pdf --outer 25 --inner 10 --unit mm
```

### 7. Colored Borders
Red border with custom width:
```bash
python boundary-box.py document.pdf output.pdf --border-color "255,0,0" --border-width 2
```

### 8. High-Quality Processing
For documents with images:
```bash
python boundary-box.py document.pdf output.pdf --quality high --dpi 600
```

### 9. Batch Processing
Skip confirmation for automation:
```bash
python boundary-box.py input.pdf output.pdf -y --pages 1-50
```

### 10. Custom Config File
Use alternative configuration:
```bash
python boundary-box.py input.pdf output.pdf --config custom-config.yaml
```

## About BoundaryBox

BoundaryBox is designed to add professional borders to PDF documents while maintaining the quality of your content. Whether you're preparing documents for printing, adding margins for binding, or creating consistent formatting across multiple PDFs, BoundaryBox provides the control and flexibility you need.

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with description
