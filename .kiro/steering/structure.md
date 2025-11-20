---
inclusion: always
---

# Project Structure

## Directory Organization

```
ocr-coretax/
├── input/              # PDF files to process (user data, gitignored)
├── output/             # Generated images from PDFs (user data, gitignored)
├── results/            # Excel output files (user data, gitignored)
├── extracted_txt/      # Extracted text files (user data, gitignored)
├── example/            # Reference images and documentation
├── app/                # Packaged application (UV workspace member)
│   ├── assets/         # Application icons and resources
│   ├── build/          # PyInstaller build artifacts
│   ├── dist/           # Compiled executables
│   └── main.py         # Application entry point
├── upx-5.0.2-win64/    # UPX compression tool
└── [extraction scripts at root]
```

## Core Scripts

### Main Extraction Pipelines

- `main.py`: PDF to image conversion pipeline
- `direct_pdf_extraction.py`: Direct text extraction (fastest, recommended)
- `enhanced_structured_ocr.py`: OCR-based extraction for scanned PDFs
- `structured_ocr_pipeline.py`: Basic structured OCR
- `ocr_pipeline.py`: Basic OCR processing

### UI Applications

- `coretax_extractor_flet.py`: Modern Flet-based GUI (primary UI)
- `coretax_extractor_ui.py`: Alternative UI implementation

### Analysis & Testing Scripts

- `improved_extraction_patterns.py`: Pattern testing and validation
- `analyze_coretax_format.py`: Format analysis
- `compare_extraction_methods.py`: Method comparison
- `test_*.py`: Various test scripts
- `check_*.py`: Validation scripts
- `debug_*.py`: Debugging utilities
- `view_*.py`: Result viewers

### Utility Scripts

- `extract_all_pdfs_to_txt.py`: Batch text extraction
- `pdf_to_text_viewer.py`: Text viewer
- `pdf_raw_text_metadata_viewer.py`: Metadata viewer

## File Naming Conventions

- **Test scripts**: `test_*.py` - Temporary scripts for testing specific functionality
- **Debug scripts**: `debug_*.py` - Debugging and investigation tools
- **View scripts**: `view_*.py` - Result visualization utilities
- **Check scripts**: `check_*.py` - Validation utilities
- **Analysis scripts**: `analyze_*.py` - Format and data analysis

## Output Files

- Excel files: `coretax_extraction_YYYYMMDD_HHMMSS.xlsx`
- Log files: `*.log` (gitignored)
- Images: `page_NNN.png` in subdirectories under `output/`

## Configuration Files

- `pyproject.toml`: Root project dependencies and UV workspace config
- `app/pyproject.toml`: App-specific configuration
- `uv.lock`: Dependency lock file
- `.python-version`: Python version specification
