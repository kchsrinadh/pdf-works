# PDF Border Scale

A powerful Python tool for adding customizable borders to PDF pages while preserving content quality. Scale your PDF content to fit within borders with precise control over spacing, quality, and appearance.

## Features

- 📐 **Dual Spacing Control**: Separate control for outer margin (page edge to border) and inner padding (border to content)
- 🎨 **Customizable Borders**: Adjust border width, color, and style
- 📊 **Quality Preservation**: Multiple quality modes to maintain document fidelity
- 📈 **Real-time Progress**: Visual progress bar with detailed status
- 🔄 **Aspect Ratio Control**: Preserve or stretch content as needed
- 📏 **Multiple Units**: Support for inches, millimeters, and points
- ✅ **Settings Preview**: Review all settings before processing with visual ASCII preview
- 👁️ **Visual Layout Preview**: See exactly how borders will look before processing
- 📄 **Page Range Selection**: Process specific pages or page ranges
- ⌨️ **Intuitive Confirmation**: Simple Enter/any-key confirmation system

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
python border_scale.py document.pdf output.pdf
```
## Output Example

```
============================================================
📋 BORDER SETTINGS TO BE APPLIED
============================================================

📁 Files:
  • Input:  document.pdf (47.9MB)
  • Output: output.pdf

📄 Pages:
  • Processing: All pages (1-514)

📐 Spacing:
  • Outer margin:  0.50 inch (36.0 pts)
  • Inner padding: 0.25 inch (18.0 pts)
  • Total spacing: 0.75 inch

🎨 Border Style:
  • Width: 1 pts
  • Color: RGB(0, 0, 0)

⚙️  Quality Settings:
  • Quality mode: ORIGINAL
  • Preserve aspect ratio: Yes

============================================================

📐 PREVIEW OF BORDER LAYOUT:

────────────────────────────────────────────────────────────
│                                                          │
│                                                          │
│  ████████████████████████████████████████████████████    │
│  █                                                  █    │
│  █  ·············································   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·              PDF CONTENT                  ·   █    │
│  █  ·             ← preserved →                 ·   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·                                           ·   █    │
│  █  ·············································   █    │
│  █                                                  █    │
│  ████████████████████████████████████████████████████    │
│                                                          │
│                                                          │
────────────────────────────────────────────────────────────

LEGEND:
  ─│ Page edges
  █ Border (Black)
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
Processing 'document.pdf' (16 of 100 pages, 12.3MB)
Quality mode: ORIGINAL
[########################################] 16/16 pages
💾 Saving PDF with quality preservation...
✅ Saved 'output.pdf' (2.1MB)
⏱️  Processing time: 3.45 seconds
```


### Process Specific Pages
```bash
python border_scale.py input.pdf output.pdf --pages 1-10
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

### Page Selection
| Option | Default | Description |
|--------|---------|-------------|
| `--pages` | all | Page range to process (e.g., "1-5", "1,3,5", "1-3,7-10") |

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
| `--quality` | **original** | Quality mode: `original`, `high`, `medium`, `standard` |
| `--dpi` | 300 | DPI for rendering (high/medium quality modes) |
| `--no-preserve-ratio` | False | Stretch content to fit (may distort) |

### Other Options
| Option | Description |
|--------|-------------|
| `-y`, `--yes` | Skip confirmation prompt |

## Usage Examples

### 1. Basic Border Addition
Add default borders to all pages:
```bash
python border_scale.py document.pdf output.pdf
```

### 2. Process Specific Pages
First 10 pages only:
```bash
python border_scale.py document.pdf output.pdf --pages 1-10
```

### 3. Multiple Page Ranges
Process pages 1-5, page 10, and pages 15-20:
```bash
python border_scale.py document.pdf output.pdf --pages 1-5,10,15-20
```

### 4. Custom Spacing
Large outer margin with minimal inner padding:
```bash
python border_scale.py document.pdf output.pdf --outer 1.5 --inner 0.1
```

### 5. Metric Units
Using millimeters for precise control:
```bash
python border_scale.py document.pdf output.pdf --outer 25 --inner 10 --unit mm
```

### 6. Colored Border
Red border with 3pt width:
```bash
python border_scale.py document.pdf output.pdf --border-width 3 --border-color "255,0,0"
```

### 7. Blue Border with Custom Spacing
```bash
python border_scale.py document.pdf output.pdf --outer 0.75 --inner 0.5 --border-color "0,0,255"
```

### 8. Process Cover Pages Only
First and last page:
```bash
python border_scale.py document.pdf output.pdf --pages 1,100
```

### 9. High-Resolution Processing
For documents with detailed images:
```bash
python border_scale.py document.pdf output.pdf --quality high --dpi 600
```

### 10. Fast Processing for Drafts
Medium quality with specific pages:
```bash
python border_scale.py document.pdf output.pdf --pages 1-20 --quality medium
```

### 11. Batch Processing (Skip Confirmation)
```bash
python border_scale.py input.pdf output.pdf -y --outer 1.0 --inner 0.5 --pages 1-50
```

### 12. Professional Report Style
Wide margins for binding and notes:
```bash
python border_scale.py report.pdf final_report.pdf --outer 1.25 --inner 0.75 --border-width 2
```

### 13. Chapter Processing
Process specific chapter pages:
```bash
python border_scale.py book.pdf chapter1.pdf --pages 1-35
python border_scale.py book.pdf chapter2.pdf --pages 36-78
```

### 14. Even/Odd Pages (manual selection)
Process even pages:
```bash
python border_scale.py document.pdf even.pdf --pages 2,4,6,8,10,12,14,16,18,20
```

### 15. Skip Middle Pages
Process beginning and end only:
```bash
python border_scale.py document.pdf output.pdf --pages 1-10,90-100
```

## Page Range Syntax

The `--pages` option supports flexible page range specifications:

- **Single page**: `5` - Process only page 5
- **Range**: `1-10` - Process pages 1 through 10
- **Multiple pages**: `1,3,5,7` - Process specific pages
- **Combined**: `1-5,10,15-20` - Mix ranges and individual pages
- **All pages**: `all` or omit the option - Process entire document

## Quality Modes Explained

### `original` - Vector Preservation (Default)
- **Best for**: Text documents, technical drawings, forms
- **Pros**: Maintains vector graphics, text remains searchable, no rasterization
- **Cons**: May not handle complex images well
- **Note**: This is the default mode for maximum quality preservation

### `high` - High-Quality Rendering
- **Best for**: Mixed content (text + images)
- **Pros**: Excellent quality, configurable DPI
- **Cons**: Larger file sizes, converts vectors to raster

### `medium` - Balanced Mode
- **Best for**: Draft documents, quick processing
- **Pros**: Faster processing, smaller files
- **Cons**: Some quality loss possible

### `standard` - PyPDF Mode
- **Best for**: When PyMuPDF is not available
- **Pros**: No extra dependencies
- **Cons**: Basic quality preservation

## Understanding Spacing

### Visual Layout
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

### Interactive Preview
Before processing, the tool shows an ASCII art preview of how your settings will look.

## Interactive Confirmation

The tool provides a clear, interactive confirmation before processing:

```
❓ Do you want to proceed with these settings?
   • Press ENTER to continue
   • Press any other key to cancel

   Waiting for input...
```

- **ENTER key**: Proceeds with processing (shows ✅)
- **Any other key**: Cancels the operation (shows ❌)
- **Skip prompt**: Use `-y` or `--yes` flag to skip confirmation


## Tips for Best Results

1. **For text-heavy documents**: Use `--quality original` (default) to preserve vector text
2. **For image-heavy documents**: Use `--quality high --dpi 600` for best results
3. **For consistent layouts**: Keep aspect ratio preservation enabled (default)
4. **For print preparation**: Use larger outer margins (1.0" or more)
5. **For digital viewing**: Use smaller margins (0.25" - 0.5")
6. **Review settings first**: The preview shows exactly how borders will look before processing
7. **Process in batches**: Use page ranges to process large documents in sections
8. **Test first**: Process a few pages first to verify settings before processing entire document
9. **Quick cancellation**: Press any key other than Enter to cancel at confirmation

## What's New

### Latest Features (Version 3.1)
- **Enhanced Confirmation System**: Clear Enter/any-key confirmation with visual feedback
- **Improved User Experience**: Shows "Waiting for input..." and success/cancel indicators

### Version 3.0
- **Page Range Selection**: Process specific pages or ranges
- **Enhanced Progress Display**: Shows pages being processed vs total
- **Improved Settings Display**: Clear indication of which pages will be processed
- **Flexible Page Syntax**: Support for complex page range specifications

### Version 2.0
- **Visual Preview**: See ASCII art representation of border layout before processing
- **Settings Confirmation**: Review all settings upfront with option to cancel
- **Default Quality Change**: `original` mode is now default for best text preservation
- **Enhanced Progress Display**: Shows quality mode and DPI during processing

## Performance Notes

- **Processing Speed**: Varies by quality mode, file size, and number of pages
  - Original: Fast (vector preservation)
  - High: Slower (rasterization at high DPI)
  - Medium: Moderate
  - Standard: Fast (basic processing)

- **File Size Changes**:
  - Processing fewer pages results in smaller output files
  - Original mode: Usually maintains similar file size per page
  - High mode: May increase file size significantly
  - Medium mode: Moderate increase

## Troubleshooting

### PyMuPDF Not Installed
If you see a warning about PyMuPDF, install it for better quality:
```bash
pip install pymupdf
```

### Invalid Page Range
Ensure page numbers are within document range and properly formatted:
- Correct: `1-10`, `1,3,5`, `1-3,7-10`
- Incorrect: `10-1`, `0-5`, `1-1000` (if document has fewer pages)

### Memory Issues with Large PDFs
Process in smaller batches:
```bash
python border_scale.py large.pdf part1.pdf --pages 1-100
python border_scale.py large.pdf part2.pdf --pages 101-200
```

### Slow Processing
- Use `--quality medium` or `--quality standard` for faster processing
- Process fewer pages at once using page ranges

### Confirmation Not Working
If the interactive confirmation doesn't work on your system:
- Use the `-y` flag to skip confirmation
- The tool will fall back to standard Enter confirmation if key detection fails

## Requirements

### Minimum Requirements
- Python 3.6+
- pypdf
- reportlab

### Recommended Requirements
- Python 3.8+
- pypdf
- reportlab
- pymupdf (for high-quality modes)

### Platform Notes
- **Windows**: Full key detection support via msvcrt
- **Linux/Mac**: Full key detection support via termios
- **Other platforms**: Falls back to Enter-only confirmation

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Changelog

### Version 3.1
- Enhanced confirmation prompt with Enter/any-key system
- Added visual feedback (✅/❌) for user actions
- Improved cross-platform key detection
- Added "Waiting for input..." indicator

### Version 3.0
- Added page range selection with `--pages` option
- Support for complex page range specifications
- Enhanced progress display for partial processing
- Improved settings preview with page information

### Version 2.0
- Changed default quality mode to `original` for better text preservation
- Added visual ASCII preview of border layout
- Added settings confirmation prompt before processing
- Improved progress display with quality mode information