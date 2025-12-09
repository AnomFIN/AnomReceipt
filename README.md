# AnomReceipt - Linux Receipt Printing Application

A professional receipt printing application for Linux, designed for **Epson TM-T70II** thermal receipt printers (ESC/POS compatible).

## Features

- **Multi-Company Support**: Pre-configured templates for 5 different companies
- **Bilingual**: Full Finnish (FI) and English (EN) support
- **Reactive GUI**: Real-time receipt preview as you edit
- **Flexible Printing**: USB and Network (IP) printer support
- **Customizable**: ASCII logo editor, custom templates, and company profiles
- **Professional**: VAT calculations, payment methods, invoice numbers
- **Modern Architecture**: Clean, modular Python 3 with PyQt5

## Screenshot

The application features a split-screen interface with input fields on the left and a live receipt preview on the right.

## Requirements

- Python 3.7 or higher
- Linux (tested on Ubuntu/Debian)
- Epson TM-T70II printer (optional - works in simulation mode without hardware)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/AnomFIN/AnomReceipt.git
cd AnomReceipt
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or using a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the application

```bash
python3 main.py
```

## Configuration

### Printer Setup

1. Click the **Settings** button in the main window
2. Choose connection type:
   - **USB**: Leave device path empty for auto-detection, or specify (e.g., `/dev/usb/lp0`)
   - **Network**: Enter printer IP address and port (default: 9100)
3. Click **Test Connection** to verify
4. Click **Save**

### Default Settings

The application stores settings in `config/settings.json`:

```json
{
  "printer": {
    "connection_type": "usb",
    "device_path": null,
    "ip_address": null,
    "port": 9100
  },
  "defaults": {
    "company": "Harjun Raskaskone Oy",
    "language": "FI",
    "currency": "EUR"
  }
}
```

## Usage

### Basic Receipt Printing

1. **Select Company**: Choose from dropdown (5 pre-configured companies)
2. **Select Payment Method**: Cash, Card, MobilePay, Bank transfer, etc.
3. **Add Items**: Click "Add item" and fill in product details
   - Product name
   - Quantity
   - Unit price
   - VAT rate (0%, 10%, 14%, 24%, etc.)
4. **Preview**: Watch the receipt update in real-time
5. **Print**: Click "Print receipt" to send to printer

### Language Toggle

Switch between Finnish and English using the language dropdown. All UI labels and receipt templates update automatically.

### Logo Editor

1. Click **Logo Editor** button
2. Enter or paste ASCII art
3. Preview in real-time
4. Click **Save logo**
5. Logos are stored in `templates/logos/` directory

### Customer Information

Optional fields:
- Customer name
- Reference number
- Invoice number
- Date/time (defaults to current, but editable)

## Pre-configured Companies

1. **Harjun Raskaskone Oy** - Heavy machinery (Tampere)
2. **Helsinki eBike Service Oy** - E-bike service (Helsinki)
3. **JugiSystems** - IT/Cyber solutions (Espoo)
4. **Lähikauppa Mäkelä** - Retail store (Helsinki)
5. **Oulu Marketplace** - Retail store (Oulu)

## Adding a New Company

Edit `templates/companies.py`:

```python
NEW_COMPANY = CompanyProfile(
    name="Your Company Name",
    address="Street Address",
    postal_code="12345",
    city="City",
    country="Finland",
    vat_id="FI12345678",
    phone="+358 12 345 6789",
    email="info@company.com",
    default_language="FI",
    default_currency="EUR",
    default_footer_fi="Finnish footer text",
    default_footer_en="English footer text",
    logo_file="your_logo.txt"  # Optional
)

# Add to COMPANIES dictionary
COMPANIES["Your Company Name"] = NEW_COMPANY
```

## Project Structure

```
AnomReceipt/
├── main.py                 # Application entry point
├── models.py               # Data models (ReceiptData, CompanyProfile, etc.)
├── i18n.py                 # Internationalization (FI/EN)
├── requirements.txt        # Python dependencies
├── config/
│   └── settings.py         # Configuration management
├── gui/
│   ├── main_window.py      # Main application window
│   ├── settings_dialog.py  # Settings dialog
│   └── logo_editor.py      # ASCII logo editor
├── printer/
│   └── escpos_printer.py   # Printer abstraction (USB/Network)
├── templates/
│   ├── template_engine.py  # Receipt template renderer
│   ├── companies.py        # Company profiles
│   └── logos/              # ASCII logo files
│       ├── harjun_raskaskone.txt
│       ├── helsinki_ebike.txt
│       └── jugisystems.txt
└── tests/
    ├── test_models.py      # Unit tests for models
    └── test_template_engine.py  # Unit tests for templates
```

## Testing

Run unit tests:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=. tests/
```

## Troubleshooting

### Printer not detected (USB)

1. Check printer is powered on and connected
2. Check USB permissions: `ls -l /dev/usb/lp*`
3. Add user to `lp` group: `sudo usermod -a -G lp $USER`
4. Logout and login again

### Network printer not responding

1. Verify printer IP address: `ping <printer-ip>`
2. Check port is accessible: `telnet <printer-ip> 9100`
3. Verify printer supports ESC/POS over network
4. Check firewall settings

### Missing dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Python version issues

Ensure Python 3.7+:

```bash
python3 --version
```

## Development

### Code Quality

- Type hints used throughout
- Docstrings on all classes and functions
- Clean separation of concerns (GUI, business logic, printing)
- Modular architecture for easy extension

### Future Enhancements

- [ ] Database support for receipt history
- [ ] PDF export
- [ ] Email receipts
- [ ] Barcode/QR code support
- [ ] Multiple printer profiles
- [ ] Product catalog management
- [ ] Advanced reporting

## License

[Add your license here]

## Support

For issues and feature requests, please use the GitHub issue tracker.

## Credits

Developed for AnomFIN by the AnomReceipt team.
