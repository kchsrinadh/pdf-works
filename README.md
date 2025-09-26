
# PDF Works

A collection of Python tools for PDF manipulation and processing.

## Available Tools

### [BoundaryBox](./boundary-box/)
Add customizable borders and margins to PDF pages while preserving content quality.

```bash
cd boundary-box
python boundary-box.py input.pdf output.pdf
```

Features:
- Adjustable outer margins and inner padding
- Multiple border styles (rounded, solid, dashed, dotted)
- Visual preview before processing
- Page range selection
- Multiple quality modes
- YAML configuration support

[Full documentation →](./boundary-box/README.md)

---

*More tools will be added as time permits.*

## Installation

```bash
# Navigate to specific tool directory
cd boundary-box

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
   cd boundary-box
   ```

3. Install requirements
   ```bash
   pip install -r requirements.txt
   ```

4. Run the tool (use --help for options)
   ```bash
   python boundary-box.py input.pdf output.pdf --help
   ```

## Repository Structure

```
pdf-works/
├── boundary-box/
│   ├── boundary-box.py
│   ├── config.yaml
│   ├── requirements.txt
│   ├── README.md
│   └── example files
└── README.md
```

## License

MIT License

## Contributing

Feel free to submit issues or pull requests if you find bugs or have suggestions.
