# ROM Compression Center

A desktop GUI app for optimizing and recompressing ROM files for retro game collectors. Built with Python and PySide6, it provides a user-friendly interface to scan ROM folders, detect platforms, and recommend optimal compression formats.

## Features

- Directory picker for ROM folders
- Platform detection (PS2, PSP, GBA, Nintendo Switch, etc.)
- Compression suggestions and one-click compress/decompress/recompress
- Real-time size preview (original vs compressed)
- Persistent user settings (YAML)
- Confirmation dialogs for destructive actions
- Integration with external CLI tools: CHDMan, maxcso, 7-Zip CLI, NSZ
- Real-time UI updates during queue processing

## Technologies

- Python 3.10+
- PySide6 (Qt for Python)
- subprocess, os, pathlib
- External tools: CHDMan, maxcso, 7-Zip CLI, NSZ

## Getting Started

1. Install Python 3.10+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the app:
   ```bash
   python main.py
   ```

## Folder Structure

```
rom-compression-center/
├── assets/               # Icons, images, logos
├── compression/          # Interfaces to tools like chdman, maxcso
├── core/                 # Logic for platform detection, size calc
├── ui/                   # PySide6 GUI components
├── tests/                # Unit tests
├── main.py               # App entry point
├── requirements.txt
└── README.md
```

## Project Status

See `documentation.md` for a detailed summary of completed work and remaining tasks.

## License

MIT License

---

For more information, see the full documentation in `documentation.md` or visit the [GitHub repository](https://github.com/mfrafael/rom-compression-center).
