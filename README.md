# AnomReceipt

A modern Python 3 Qt-based receipt printing application for Epson TM-T70II (ESC/POS) printers.

## Features

- **Reactive Qt GUI** - Modern, responsive user interface built with PyQt5
- **Multiple Printer Connections** - Support for both USB and Network (IP) connections
- **Live Text Preview** - Real-time preview of receipts before printing
- **Bilingual Support** - Full FI/EN language toggle for both UI and receipts
- **Template System** - JSON/YAML-based templates for multiple companies
- **Payment Methods** - Support for cash, card, MobilePay, and bank transfers
- **Advanced Logo Editor** - Built-in editor with library of 26+ pre-designed logos
- **Configurable Settings** - Adjust receipt width, length, logo dimensions, and formatting
- **Luxury Brand Templates** - Pre-built templates for Louis Vuitton, Gucci, Hermès, Chanel, Prada, Rolex, and more
- **Clean, Modular Code** - Well-organized codebase following Python best practices

## Requirements

- Python 3.7 or higher
- Linux operating system
- Epson TM-T70II printer (or compatible ESC/POS printer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AnomFIN/AnomReceipt.git
cd AnomReceipt
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python3 main.py
```

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

**Tips for ASCII Logos:**
- Check max dimensions in Settings (default: 48 chars × 20 lines)
- Use the character counter to stay within limits
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
