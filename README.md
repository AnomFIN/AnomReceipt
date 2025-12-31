# AnomReceipt

**Professional Windows Receipt OCR Application**

> 🎉 **Version 2.0** - Complete Windows redesign with modern GUI, OCR functionality, and bulletproof stability!

## 🪟 Windows Users - Start Here!

**For Windows installation and usage, see:** [WINDOWS_README.md](WINDOWS_README.md)

### Quick Start (Windows)

1. Install Python 3.8+ (check "Add Python to PATH")
2. Run: `.\install.ps1`
3. Launch: `launch.bat` or `python main.py`

That's it! The installer handles everything automatically.

---

## ✨ What's New in Version 2.0

### 🎨 Modern Windows GUI
- **Professional design** - Native Windows feel
- **Dark & Light themes** - Toggle anytime
- **Responsive layout** - Resizable split-view
- **Status indicators** - Visual feedback for all operations

### 🔍 OCR Functionality ("Litteroi Kuvasta")
- **High-quality text extraction** from receipt images
- **Intelligent preprocessing** for better accuracy
- **Structure preservation** - Maintains formatting and hierarchy
- **Multiple formats** - PNG, JPG, JPEG, BMP, TIFF support

### 🛡️ Absolute Stability
- **Never crashes** - Comprehensive error handling
- **User-friendly messages** - No technical jargon
- **Detailed logging** - Everything logged for troubleshooting
- **Graceful recovery** - App continues after errors

### 💪 Professional Quality
- **Clean architecture** - Well-organized codebase
- **Type safety** - Full type annotations
- **Documentation** - Comprehensive docstrings
- **Production-ready** - No hacks or TODOs

---

## 🚀 Features

### Core Features
- **OCR Processing** - Extract text from receipt images
- **Image Enhancement** - Automatic preprocessing for better results
- **Logo Detection** - Identifies and handles non-text elements
- **Text Editing** - Edit extracted text before saving
- **Multiple Export** - Save as text file or copy to clipboard

### Technical Features
- **PySide6/Qt GUI** - Native Windows integration
- **Tesseract OCR** - Industry-standard OCR engine
- **OpenCV Processing** - Advanced image preprocessing
- **Error Handling** - Defensive programming throughout
- **Comprehensive Logging** - Rotating log files with full details

---

## 📋 Requirements

### Windows
- Windows 10 or 11 (64-bit)
- Python 3.8 or higher
- Tesseract OCR (optional, for OCR features)

### Linux (Legacy Support)
- Python 3.8 or higher
- Linux operating system
- Epson TM-T70II printer (or compatible ESC/POS printer)

*Note: Version 2.0 is optimized for Windows. Linux users can still use the legacy features.*

---

## 📦 Installation

### Automated Windows Installation (Recommended)

```powershell
# Clone repository
git clone https://github.com/AnomFIN/AnomReceipt.git
cd AnomReceipt

# Run installer (automatically handles everything)
.\install.ps1

# Launch application
.\launch.bat
# OR
python main.py
```

### Manual Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

---

## 📖 Documentation

- **[Windows Installation & Usage Guide](WINDOWS_README.md)** - Complete guide for Windows users
- **[Legacy README](README.old.md)** - Original Linux/printer documentation  
- **[Project Summary](PROJECT_SUMMARY.md)** - Technical implementation details
- **[Luxury Brands](LUXURY_BRANDS.md)** - Brand template information
- **[Contributing](CONTRIBUTING.md)** - How to contribute
- **[Security](SECURITY.md)** - Security information

---

## 🗂️ Project Structure

```
AnomReceipt/
├── install.ps1              # Windows installer (PowerShell)
├── launch.bat               # Quick launch script (Windows)
├── verify_install.py        # Installation verification
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
│
├── anomreceipt/            # Main application package
│   ├── core/              # Error handling & logging
│   │   ├── logger.py
│   │   └── error_handler.py
│   │
│   ├── gui/               # Modern Windows GUI
│   │   ├── modern_main_window.py  # Main application window
│   │   ├── theme_manager.py       # Dark/Light themes
│   │   └── status_widget.py       # Status indicators
│   │
│   ├── ocr/               # OCR engine
│   │   └── ocr_engine.py
│   │
│   ├── printer/           # Printer support (legacy)
│   ├── templates/         # Receipt templates (legacy)
│   └── locale/            # Internationalization (legacy)
│
├── logs/                   # Application logs
└── venv/                   # Virtual environment
```

---

## 🎯 Usage

### Processing Receipt Images

1. **Load an image**
   - Click "📁 Load Image"
   - Select a receipt image
   - Preview appears on the left

2. **Process with OCR**
   - Click "🔍 Process OCR"
   - Watch the progress
   - Text appears on the right

3. **Edit and Save**
   - Edit the extracted text
   - Save to file or copy to clipboard

See [WINDOWS_README.md](WINDOWS_README.md) for detailed usage instructions.

---

## 🔧 Troubleshooting

### Common Issues

**"PySide6 not found"**
- Run the installer: `.\install.ps1`
- Or: `pip install -r requirements.txt`

**"OCR not working"**
- Install Tesseract OCR
- Download: https://github.com/UB-Mannheim/tesseract/wiki

**"Application won't start"**
- Check logs in `logs/` directory
- Run verification: `python verify_install.py`
- Reinstall: Delete `venv` and run `install.ps1`

For more troubleshooting, see [WINDOWS_README.md](WINDOWS_README.md#troubleshooting).

---

## 📝 Migration from Version 1.x

Version 2.0 introduces significant changes:

### New Features
- Modern Windows GUI with PySide6 (replaced PyQt5)
- OCR functionality for receipt images
- Professional error handling and logging
- Dark/Light theme support

### Legacy Features (Still Available)
- Receipt printing (ESC/POS)
- Template system
- Logo editor
- Multiple language support

### Breaking Changes
- GUI completely redesigned
- PyQt5 → PySide6 migration
- New project structure

---

## 🆘 Support

Need help?

1. Check [WINDOWS_README.md](WINDOWS_README.md)
2. Review logs in `logs/` directory
3. Run `python verify_install.py` to diagnose issues
4. Open an issue on GitHub

---

## 📜 License

This project is open source and available for use and modification.

---

## 👨‍💻 Author

**AnomFIN**

---

## 🙏 Acknowledgments

- **PySide6** - Modern Qt framework for Python
- **Tesseract OCR** - Industry-standard OCR engine
- **OpenCV** - Computer vision library
- **python-escpos** - ESC/POS printer support

---

**Made with 💙 for Windows**

## Project Structure

```
AnomReceipt/
├── anomreceipt/              # Main application package
│   ├── gui/                  # GUI components
│   │   ├── main_window.py   # Main application window
│   │   └── logo_editor.py   # ASCII logo editor
│   ├── printer/              # Printer interface
│   │   └── escpos_printer.py # ESC/POS printer wrapper
│   ├── templates/            # Template management
│   │   └── template_manager.py
│   └── locale/               # Localization
│       └── translator.py     # FI/EN translation system
├── templates/                # Receipt templates
│   ├── companies/            # Company template files (JSON/YAML)
│   └── logos/                # ASCII logo files
├── main.py                   # Application entry point
└── requirements.txt          # Python dependencies
```

## Usage

### Connecting to a Printer

**USB Connection:**
1. Connect your Epson TM-T70II via USB
2. Click "Connect USB" button
3. The default vendor ID (0x04b8) and product ID (0x0202) will be used

**Network Connection:**
1. Click "Connect Network" button
2. Enter the printer's IP address
3. Enter the port (default: 9100)
4. Click OK

### Creating Receipts

1. **Select Company**: Choose a company template from the dropdown
2. **Add Items**: Click "Add Item" to add products/services
   - Enter item name
   - Enter quantity
   - Enter price
3. **Select Payment Method**: Choose from cash, card, MobilePay, or bank
4. **Select Language**: Choose FI or EN for the receipt
5. **Preview**: View the receipt in real-time on the right panel
6. **Print**: Click the "Print" button to send to the printer

### Configuring Receipt Settings

Click the **⚙ Settings** button to customize:
- **Receipt Width**: 32-80 characters (default: 48)
- **Receipt Length**: Maximum lines per receipt (default: 80)
- **Logo Dimensions**: Max width and height for ASCII logos
- **Paper Handling**: Feed lines and auto-cut options
- **Text Formatting**: Bold headers, double-width totals

### Managing Templates

Templates are stored in `templates/companies/` as JSON or YAML files.

**Included Templates:**
- Finnish companies (LähiVakuutus, Kesko, OP, etc.)
- Luxury brands (Louis Vuitton, Gucci, Hermès, Chanel, Prada, Rolex)
- Generic templates for customization

See [LUXURY_BRANDS.md](LUXURY_BRANDS.md) for detailed information about luxury brand templates.

**Example YAML Template:**
```yaml
name: "My Company Oy"
logo_file: "my_logo.txt"

company_info:
  name: "My Company Oy"
  address: "Street Address 123"
  city: "00100 Helsinki"
  vat_id: "1234567-8"
  phone: "+358 40 123 4567"
  email: "info@mycompany.fi"

payment_methods:
  cash:
    EN: "Cash"
    FI: "Käteinen"
  card:
    EN: "Card"
    FI: "Kortti"
  mobilepay:
    EN: "MobilePay"
    FI: "MobilePay"
  bank:
    EN: "Bank Transfer"
    FI: "Tilisiirto"
```

### Creating ASCII Logos

1. Click "Edit Logo" button
2. Browse the **Logo Library** with 26+ pre-designed logos:
   - **Luxury brands**: Louis Vuitton, Gucci, Hermès, Chanel, Prada, Versace, Dior, Burberry, Cartier, Rolex
   - **Finnish companies**: LähiVakuutus, Kesko, OP, Nordea, S-Pankki, Elisa, Telia, Stockmann, HOK-Elanto, Prisma, Alko
   - **Generic templates**: Minimalist borders, simple frames
3. Click on any logo to load it into the editor
4. Customize or create your own ASCII art
5. Click "Save Logo" to save to a file
6. Reference the logo file in your company template
7. Need your existing logo? Click "Import logo image" to load PNG/JPG/BMP/GIF files and auto-convert to ASCII.

**Tips for ASCII Logos:**
- Check max dimensions in Settings (default: 48 chars × 20 lines)
- Use the font-size control to tighten alignment and the bold toggle when tracing outlines
- Browse the library for inspiration
- Test the preview before printing

## Supported Payment Methods

- **Cash** (Käteinen) - Cash payments
- **Card** (Kortti) - Credit/debit card payments
- **MobilePay** - MobilePay mobile payments
- **Bank** (Tilisiirto) - Bank transfers

## Language Support

The application supports two languages:

- **FI** (Finnish) - Suomi
- **EN** (English) - English

You can set different languages for:
- User interface language
- Receipt content language

## Development

### Adding New Templates

1. Create a new JSON or YAML file in `templates/companies/`
2. Follow the template structure shown above
3. Restart the application to load the new template

### Adding New Logos

1. Create ASCII art in a text file
2. Save to `templates/logos/`
3. Reference the file in your company template

### Extending Payment Methods

Edit the template files to add custom payment methods with their translations.

## Troubleshooting

**Printer not found:**
- Check USB connection
- Verify printer is powered on
- Try running with sudo if permission issues occur
- For network printers, verify IP address and port

**Template not loading:**
- Check YAML/JSON syntax
- Verify file is in `templates/companies/` directory
- Check application logs in `anomreceipt.log`

**Preview not updating:**
- Verify items are properly entered
- Check that a company template is selected
- Restart the application

## License

This project is open source and available for use and modification.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Author

AnomFIN
