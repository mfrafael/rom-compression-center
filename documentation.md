# ROM Compression Center - Technical Documentation (PySide6 Version)

This documentation defines the technical foundation, design principles, and structure for contributing to the **ROM Compression Center**, a desktop GUI app focused on optimizing and recompressing ROM files for retro game collectors using **Python + PySide6**.

---

## ✨ Project Overview

**Name:** ROM Compression Center  
**Stack:** Python + PySide6  
**Language:** English (code + docs)  
**Target Platform:** Windows (with future support for macOS/Linux)  
**Purpose:** Provide a user-friendly GUI to scan folders of ROMs, detect their platforms, and recommend optimal compression formats (e.g. CHD for PS2, CSO for PSP, ZIP for GBA).

---

## ⚙️ Technologies Used

### Backend / UI Layer

- **Python 3.10+**
- **PySide6 (Qt for Python)**: GUI toolkit
- **subprocess**: to interface with external compression tools
- **os / pathlib**: file system navigation

### External CLI Tools (Required for Full Functionality)

- **CHDMan** – compress ISOs to CHD (PS1, PS2, etc.)
- **7-Zip CLI** – for ZIP/7z compression and extraction
- **maxcso** – for CSO compression (PSP)
- **nsz** – for Nintendo Switch compression/decompression

---

## 📁 Recommended Folder Structure

```
rom-compression-center/
├── assets/               # Icons, images, logos
├── compression/          # Interfaces to tools like chdman, maxcso
├── core/                 # Logic for platform detection, size calc
├── ui/                   # PySide6 GUI components
│   ├── file_tree.py
│   └── settings_dialog.py
├── tests/                # Unit tests (TBD)
├── main.py               # App entry point
├── requirements.txt
└── README.md
```

---

## ✅ Getting Started

### 1. Requirements

- Python 3.10+
- Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Launch App

```bash
python main.py
```

---

## 🌐 App Functionality (MVP)

1. **Directory Picker** – Allow the user to choose one or more ROM folders.
2. **Platform Detection** – Based on folder name heuristics or file extension.
3. **Compression Suggestions** – Recommend better formats for each file.
4. **One-Click Compress / Decompress / Recompress** – Use external tools via subprocess.
5. **Size Preview** – Show original vs compressed size.

---

## 📋 Development Guidelines

### Python Style

- Use type hints (`def fn(arg: str) -> int:`)
- Follow [PEP8](https://peps.python.org/pep-0008/)
- Prefer `pathlib.Path` over `os.path`

### PySide6 / Qt

- Use `.ui` files via Qt Designer when needed
- Separate logic from UI code (MVC-style)

### Compression Interfaces

- Wrap each external tool in its own Python class/module
- Provide clear logs and error reporting

---

## 🧪 Testing (WIP)

- Add test cases to `tests/` folder
- Validate compression logic with small sample files

---

## 📦 Distribution

To package as an executable:

```bash
pyinstaller --noconsole --onefile main.py
```

(WIP: better PySide6 packaging planned)

---

## ❓ TODO

- Auto-detect installed compression tools
- Option to drag-and-drop folders into app
- Save logs of operations per session
- Optional preview of compressed file contents

---

## 🔗 References

- [PySide6 Docs](https://doc.qt.io/qtforpython/)
- [CHDMan Guide](https://wiki.recalbox.com/en/tutorials/games/chdman)
- [maxcso](https://github.com/unknownbrackets/maxcso)
- [7-Zip CLI](https://sevenzip.osdn.jp/chm/cmdline/)
- [NSZ Tools](https://github.com/nicoboss/nsz)

---

This documentation will evolve alongside the app. Keep it updated with every milestone and design change.

---

## 🚦 Project Progress Summary

### ✅ Completed Work

- Windows platform fully supported; codebase prepared for future macOS/Linux support.
- PySide6 GUI implemented: tables, buttons, status bar, progress bar, confirmation dialogs.
- Automatic ROM and platform detection, with separation of compressed and uncompressed files.
- Queue system for compress/decompress actions, supporting multiple platforms (Nintendo Switch, PS2, PSP, GBA, etc.).

- Persistent user settings (e.g., detailed log, compression preferences) stored in YAML config.
- Confirmation dialogs for destructive actions (e.g., deleting originals after compression).
- Real-time UI updates during queue processing.
- Removal of redundant code and unused files.
- All debug print statements removed from main files.
- Technical documentation and recommended folder structure provided.

### 🕗 Remaining Tasks

- Full macOS/Linux support: compatibility testing and adjustments.
- Auto-detection of installed external compression tools.
- Drag-and-drop folder support in the GUI.
- Save detailed logs for each compression/decompression session.
- Preview contents of compressed files in the UI.
- Add more automated tests in the `tests/` folder.
- Improve app packaging for distribution (PyInstaller, PySide6 dependencies).
- Refactor and document interfaces for each compression tool (MVC-style).
- Optional: add multi-language support for the UI.
- Enhance visual feedback (e.g., per-file progress bar, per-row status).

- Integration with external CLI tools via subprocess (CHDMan, maxcso, 7-Zip CLI, NSZ).

---

_Last updated: August 2025_