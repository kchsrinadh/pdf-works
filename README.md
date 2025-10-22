# PDF Works

A collection of Python tools for PDF manipulation and processing.

## Available Tools

### [BBox](./bbox/)
Add customizable borders, page numbers, and titles to PDF pages while preserving content quality.

```bash
cd bbox
python bbox.py input.pdf output.pdf
```

Features:
- Adjustable outer margins and inner padding
- Multiple border styles (rounded, solid, dashed, dotted)
- Flexible page numbering with custom formats
- Document title support (from metadata or custom text)
- Visual preview before processing
- Page range selection
- Multiple quality modes
- YAML configuration support
- Standalone binary available

[Full documentation →](./bbox/README.md)

---

*More tools will be added as time permits.*

## Installation

```bash
# Navigate to specific tool directory
cd bbox

# Install dependencies
pip install -r requirements.txt
```

## Getting Started

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/pdf-works.git
   cd pdf-works
   ```

2. Navigate to the tool you want to use
   ```bash
   cd bbox
   ```

3. Install requirements
   ```bash
   pip install -r requirements.txt
   ```

4. Run the tool (use --help for options)
   ```bash
   python bbox.py input.pdf output.pdf --help
   ```

## Using Pre-built Binaries

Download pre-built executables from releases:
- Windows: `bbox.exe`
- Linux/Mac: `bbox`

No Python installation required for binaries.

## Repository Structure

```
pdf-works/
├── bbox/
│   ├── bbox.py
│   ├── config.yaml
│   ├── requirements.txt
│   ├── README.md
│   └── dist/
│       └── bbox.exe (or bbox for Linux/Mac)
└── README.md
```

## License

MIT License

## Contributing

Feel free to submit issues or pull requests if you find bugs or have suggestions.