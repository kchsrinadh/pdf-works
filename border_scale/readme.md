# PDF Border Scale

A powerful Python tool for adding customizable borders to PDF pages while preserving content quality. Scale your PDF content to fit within borders with precise control over spacing, quality, and appearance.

## Features

- 📐 **Dual Spacing Control**: Separate control for outer margin (page edge to border) and inner padding (border to content)
- 🎨 **Customizable Borders**: Adjust border width, color, and style
- 📊 **Quality Preservation**: Multiple quality modes to maintain document fidelity
- 📈 **Real-time Progress**: Visual progress bar with detailed status
- 🔄 **Aspect Ratio Control**: Preserve or stretch content as needed
- 📏 **Multiple Units**: Support for inches, millimeters, and points
- ✅ **Settings Preview**: Review all settings before processing

## Installation

### Basic Installation
```bash
pip install pypdf reportlab
```

### Full Installation (with high-quality support)
```bash
pip install pypdf reportlab pymupdf
```

## Quick Start

### Basic Usage
```bash
python border_scale.py input.pdf output.pdf
```

### With Custom Settings
```bash
python border_scale.py input.pdf output.pdf --outer 1.0 --inner 0.5
```

## Command Line Options

### Required Arguments
| Argument | Description |
|----------|-------------|
| `input_pdf` | Path to input PDF file |
| `output_pdf` | Path to output PDF file |

### Spacing Options
| Option | Default | Description |
|--------|---------|-------------|
| `--outer` | 0.5 | Outer margin (space from page edge to border) |
| `--inner` | 0.25 | Inner padding (space from border to content) |
| `--unit` | inch | Unit for measurements: `inch`, `mm`, or `pt` |

### Border Styling
| Option | Default | Description |
|--------|---------|-------------|
| `--border-width` | 1 | Border line width in points |
| `--border-color` | 0,0,0 | Border color as RGB (0-255 each) |

### Quality Settings
| Option | Default | Description |
|--------|---------|-------------|
| `--quality` | high | Quality mode: `original`, `high`, `medium`, `standard` |
| `--dpi` | 300 | DPI for rendering (high/medium quality modes) |
| `--no-preserve-ratio` | False | Stretch content to fit (may distort) |

### Other Options
| Option | Description |
|--------|-------------|
| `-y`, `--yes` | Skip confirmation prompt |

## Usage Examples

### 1. Basic Border Addition
Add default borders (0.5" outer, 0.25" inner):
```bash
python border_scale.py document.pdf output.pdf
```

### 2. Custom Spacing
Large outer margin with minimal inner padding:
```bash
python border_scale.py document.pdf output.pdf --outer 1.5 --inner 0.1
```

### 3. Metric Units
Using millimeters for precise control:
```bash
python border_scale.py document.pdf output.pdf --outer 25 --inner 10 --unit mm
```

### 4. Colored Border
Red border with 3pt width:
```bash
python border_scale.py document.pdf output.pdf --border-width 3 --border-color "255,0,0"
```

### 5. Blue Border with Custom Spacing
```bash
python border_scale.py document.pdf output.pdf --outer 0.75 --inner 0.5 --border-color "0,0,255"
```

### 6. Maximum Quality for Text Documents
Preserves vector graphics as vectors:
```bash
python border_scale.py document.pdf output.pdf --quality original
```

### 7. High-Resolution Processing
For documents with detailed images:
```bash
python border_scale.py document.pdf output.pdf --quality high --dpi 600
```

### 8. Fast Processing
Balanced quality and speed:
```bash
python border_scale.py document.pdf output.pdf --quality medium
```

### 9. Batch Processing (Skip Confirmation)
```bash
python border_scale.py input.pdf output.pdf -y --outer 1.0 --inner 0.5
```

### 10. Minimal Borders
Thin borders with small margins:
```bash
python border_scale.py document.pdf output.pdf --outer 0.25 --inner 0.1 --border-width 0.5
```

### 11. Professional Report Style
Wide margins for binding and notes:
```bash
python border_scale.py report.pdf final_report.pdf --outer 1.25 --inner 0.75 --border-width 2
```

### 12. A4 Paper with Metric Margins
Standard European formatting:
```bash
python border_scale.py document.pdf output.pdf --outer 20 --inner 15 --unit mm
```

### 13. Stretch to Fit
Fill the border area (may distort content):
```bash
python border_scale.py document.pdf output.pdf --no-preserve-ratio
```

## Quality Modes Explained

### `original` - Vector Preservation
- **Best for**: Text documents, technical drawings, forms
- **Pros**: Maintains vector graphics, text remains searchable
- **Cons**: May not handle complex images well

### `high` - High-Quality Rendering (Default)
- **Best for**: Mixed content (text + images)
- **Pros**: Excellent quality, configurable DPI
- **Cons**: Larger file sizes

### `medium` - Balanced Mode
- **Best for**: Draft documents, quick processing
- **Pros**: Faster processing, smaller files
- **Cons**: Some quality loss possible

### `standard` - PyPDF Mode
- **Best for**: When PyMuPDF is not available
- **Pros**: No extra dependencies
- **Cons**: Basic quality preservation

## Understanding Spacing

```
Page Edge
│
├─── Outer Margin ───┐
│                    │
│   ┌────────────┐   │
│   │   Border   │   │
│   │            │   │
│   │  ┌──────┐  │   │
│   │  │      │  │   │
│   │  │ PDF  │  │   │
│   │  │      │  │   │
│   │  └──────┘  │   │
│   │            │   │
│   └────────────┘   │
│                    │
└────────────────────┘
     ↑          ↑
     │          │
  Outer     Inner
  Margin    Padding
```

## Tips for Best Results

1. **For text-heavy documents**: Use `--quality original` to preserve vector text
2. **For image-heavy documents**: Use `--quality high --dpi 600` for best results
3. **For consistent layouts**: Keep aspect ratio preservation enabled (default)
4. **For print preparation**: Use larger outer margins (1.0" or more)
5. **For digital viewing**: Use smaller margins (0.25" - 0.5")

## Output Example

```
============================================================
📋 BORDER SETTINGS TO BE APPLIED
============================================================

📁 Files:
  • Input:  document.pdf (12.3MB)
  • Output: output.pdf

📐 Spacing:
  • Outer margin:  0.50 inch (36.0 pts)
  • Inner padding: 0.25 inch (18.0 pts)
  • Total spacing: 0.75 inch

🎨 Border Style:
  • Width: 1 pts
  • Color: RGB(0, 0, 0)

⚙️  Quality Settings:
  • Quality mode: HIGH
  • DPI: 300
  • Preserve aspect ratio: Yes

============================================================

❓ Do you want to proceed with these settings?
   Press Enter to continue, or Ctrl+C to cancel...

📄 Reading 'document.pdf'...
Processing 'document.pdf' (100 pages, 12.3MB)
Quality mode: HIGH | DPI: 300
[########################################] 100/100 pages
💾 Saving PDF with quality preservation...
✅ Saved 'output.pdf' (13.1MB)
⏱️  Processing time: 15.23 seconds
```

## Troubleshooting

### PyMuPDF Not Installed
If you see a warning about PyMuPDF, install it for better quality:
```bash
pip install pymupdf
```

### Memory Issues with Large PDFs
For very large PDFs, use medium quality:
```bash
python border_scale.py large.pdf output.pdf --quality medium
```

### Slow Processing
Use standard mode for faster processing:
```bash
python border_scale.py input.pdf output.pdf --quality standard
```

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
```

The script now:
1. Shows all settings BEFORE processing starts
2. Asks for confirmation (can be skipped with `-y` flag)
3. Fixed the PyMuPDF save options error
4. Includes a comprehensive README with all possible commands and explanations

The settings preview shows everything that will be applied, making it clear what the script will do before it starts processing!