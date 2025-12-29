# AnomReceipt - Windows Installation Guide

**Professional Receipt OCR Application for Windows**

## 🚀 Quick Start

### Prerequisites

- **Windows 10 or 11** (64-bit)
- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
  - ⚠️ During installation, **check "Add Python to PATH"**
- **Tesseract OCR** (optional, for OCR features) - [Download Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### Installation

1. **Download or Clone this repository:**
   ```powershell
   git clone https://github.com/AnomFIN/AnomReceipt.git
   cd AnomReceipt
   ```

2. **Run the installer:**
   
   **Interactive Mode (Recommended):**
   ```powershell
   .\install.ps1
   ```
   
   **Silent Mode:**
   ```powershell
   .\install.ps1 -Silent
   ```

3. **Launch the application:**
   - Double-click `launch.bat`
   - OR run: `.\venv\Scripts\python.exe main.py`

### What the Installer Does

✅ Checks Python version (minimum 3.8)  
✅ Verifies pip and venv availability  
✅ Creates isolated virtual environment  
✅ Installs all required packages  
✅ Verifies all imports work correctly  
✅ Checks for Tesseract OCR (optional)  
✅ Creates convenient launch script  
✅ Professional logging throughout

**The installer is 100% automated and bulletproof** - it handles all edge cases and will tell you exactly what to do if anything fails.

## 📋 Features

### 🎨 Professional Windows GUI
- **Modern design** that looks like a paid Windows application
- **Dark and light themes** - toggle anytime with the theme button
- **Responsive layout** - resizable split-view interface
- **Clean typography** - professional fonts and spacing
- **Visual status indicators** - processing, success, error, warning states

### 🔍 Advanced OCR ("Litteroi Kuvasta")
- **High-quality text extraction** from receipt images
- **Intelligent preprocessing** for better accuracy
- **Structure preservation** - maintains headings, spacing, hierarchy
- **Logo detection** - identifies and handles non-text elements
- **Multiple format support** - PNG, JPG, JPEG, BMP, TIFF
- **Real-time progress** - see what's happening during processing

### 🛡️ Absolute Stability
- **Never crashes** - comprehensive error handling
- **User-friendly messages** - no technical jargon
- **Detailed logging** - everything logged to file for troubleshooting
- **Graceful recovery** - app continues running after errors
- **No stack traces** visible to users

### 💪 Professional Quality
- **Clean architecture** - well-organized, maintainable code
- **Type hints** - full type annotations throughout
- **Documentation** - comprehensive docstrings
- **No hacks or TODOs** - production-ready code

## 🎯 Usage

### Processing Receipt Images

1. **Load Image**
   - Click "📁 Load Image" button
   - Select a receipt image (PNG, JPG, JPEG, BMP, TIFF)
   - Image preview appears on the left

2. **Process with OCR**
   - Click "🔍 Process OCR" button
   - Watch progress bar and status messages
   - Extracted text appears on the right

3. **Edit and Save**
   - Edit the extracted text if needed
   - Click "💾 Save Text" to save to file
   - Click "📋 Copy" to copy to clipboard
   - Click "🗑️ Clear" to start over

### Themes

- Click the **🌓 Theme** button in the top-right to toggle between dark and light themes
- Your preference is saved automatically

## 📂 Project Structure

```
AnomReceipt/
├── install.ps1              # Windows installer (PowerShell)
├── launch.bat               # Quick launch script
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── anomreceipt/
│   ├── core/               # Error handling & logging
│   ├── gui/                # Modern Windows GUI
│   ├── ocr/                # OCR engine
│   ├── printer/            # Printer support (legacy)
│   ├── templates/          # Receipt templates (legacy)
│   └── locale/             # Internationalization (legacy)
├── logs/                    # Application logs
└── venv/                    # Virtual environment
```

## 🔧 Troubleshooting

### Installation Issues

**"Python is not recognized"**
- Python is not installed or not in PATH
- Install Python from python.org
- Make sure to check "Add Python to PATH" during installation

**"pip is not available"**
- Run: `python -m ensurepip --default-pip`
- Or reinstall Python with pip option enabled

**"Package installation failed"**
- Check your internet connection
- Try running installer again
- Check logs in `anomreceipt_install.log`

### Runtime Issues

**"OCR features are disabled"**
- Tesseract OCR is not installed
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install and restart the application

**"Application won't start"**
- Check `logs/anomreceipt_YYYYMMDD.log` for details
- Verify virtual environment: `venv\Scripts\python.exe --version`
- Try reinstalling: delete `venv` folder and run `install.ps1` again

**"Low OCR accuracy"**
- Ensure image is clear and well-lit
- Try preprocessing the image externally
- Use higher resolution images

## 📝 Logs

Application logs are saved to:
- **Install logs:** `anomreceipt_install.log`
- **Runtime logs:** `logs/anomreceipt_YYYYMMDD.log`

Logs include:
- All operations and their results
- Error details with full stack traces
- User actions and system events
- Performance metrics

## 🆘 Support

If you encounter any issues:

1. Check the log files first
2. Try reinstalling with `install.ps1`
3. Verify all prerequisites are met
4. Open an issue on GitHub with:
   - Description of the problem
   - Relevant log excerpts
   - Your system info (Windows version, Python version)

## 🔐 Security

- No data is sent to external servers
- All processing happens locally
- Logs contain no sensitive information
- No credentials or secrets in code

## 📜 License

This project is open source and available for use and modification.

## 👨‍💻 Author

**AnomFIN**

---

**Made with 💙 for Windows**
