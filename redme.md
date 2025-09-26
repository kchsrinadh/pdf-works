# PDF Works

A collection of Python tools for PDF manipulation and processing.

## Available Tools

### [Border Scale](./border_scale/)
Add customizable borders to PDF pages while preserving content quality.

```bash
cd border_scale
python border_scale.py input.pdf output.pdf
```

Features:
- Adjustable outer margins and inner padding
- Visual preview before processing
- Page range selection
- Multiple quality modes

[Full documentation →](./border_scale/readme.md)

---

*More tools will be added as time permits.*

## Installation

```bash
# Basic dependencies
pip install pypdf reportlab

# Optional for better quality
pip install pymupdf
```

## Getting Started

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/pdf-works.git
   cd pdf-works
   ```

2. Navigate to the tool you want to use
   ```bash
   cd border_scale
   ```

3. Run the tool (use --help for options)
   ```bash
   python border_scale.py input.pdf output.pdf --help
   ```

## Repository Structure

```
pdf-works/
├── border_scale/
│   ├── border_scale.py
│   ├── readme.md
│   └── example files
└── README.md
```

## License

MIT License

## Contributing

Feel free to submit issues or pull requests if you find bugs or have suggestions.
