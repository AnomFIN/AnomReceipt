# Quick Start Guide

This guide will help you get started with AnomReceipt in minutes.

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python3 test_app.py
```

You should see all tests passing.

## Running the Application

### Start the GUI

```bash
python3 main.py
```

### First-Time Setup

1. **Select UI Language**: Choose between EN (English) or FI (Finnish)
2. **Connect Printer**:
   - For USB: Click "Connect USB"
   - For Network: Click "Connect Network" and enter IP address
3. **Select Company**: Choose a company template from the dropdown
4. **Select Receipt Language**: Choose the language for printed receipts

## Creating Your First Receipt

### Step-by-Step

1. **Add Items**:
   - Click "Add Item" button
   - Enter item name (e.g., "Coffee")
   - Enter quantity (e.g., "2")
   - Enter price (e.g., "3.50")
   - Repeat for more items

2. **Select Payment Method**:
   - Choose from: Cash, Card, MobilePay, or Bank Transfer

3. **Preview**:
   - Watch the live preview update on the right side
   - Verify all information is correct

4. **Print**:
   - Click the green "Print" button
   - Receipt will be sent to the printer

## Creating Your Own Company Template

### 1. Create a YAML file

Create a new file in `templates/companies/mycompany.yaml`:

```yaml
name: "My Company Name"
logo_file: "mylogo.txt"

company_info:
  name: "My Company Name"
  address: "Street Address 123"
  city: "00100 City"
  vat_id: "1234567-8"
  phone: "+358 40 123 4567"
  email: "info@mycompany.com"

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

### 2. Create a Logo (Optional)

1. Click "Edit Logo" button in the application
2. Create your ASCII art (max 48 characters wide)
3. Click "Save Logo" and name it `mylogo.txt`
4. The logo will be saved to `templates/logos/`

### 3. Restart the Application

The new template will appear in the company dropdown.

## Tips

### ASCII Logo Design

- Keep width to 48 characters maximum
- Use online ASCII art generators for inspiration
- Test in the preview before printing
- Monospace fonts work best

### Receipt Width

- Maximum line width: 48 characters
- Receipt printer will wrap longer lines
- Keep item names under 30 characters for best results

### Payment Methods

All four payment methods are pre-configured:
- **Cash** (Käteinen): For cash payments
- **Card** (Kortti): For credit/debit cards
- **MobilePay**: For MobilePay transactions
- **Bank** (Tilisiirto): For bank transfers

### Language Support

- **UI Language**: Changes button labels, menus, etc.
- **Receipt Language**: Changes the text on printed receipts
- Both can be set independently

## Troubleshooting

### Printer Not Found

**USB:**
- Check cable connection
- Verify printer is powered on
- Try: `lsusb` to see if printer is detected
- You may need to run with sudo for USB access

**Network:**
- Verify printer IP address
- Test with: `ping <printer-ip>`
- Check firewall settings
- Ensure printer is on the same network

### Templates Not Loading

- Check file syntax (YAML/JSON)
- Ensure files are in `templates/companies/`
- Check application log: `anomreceipt.log`
- Verify file permissions

### Preview Not Updating

- Ensure a company template is selected
- Check that items have valid prices
- Try removing and re-adding items
- Restart the application

## Advanced Usage

### Testing Without a Printer

You can use the application without a printer:
1. Don't connect to any printer
2. Use the live preview feature
3. All functionality works except actual printing

### Custom Payment Methods

Edit your company template to add custom payment methods:

```yaml
payment_methods:
  custom_method:
    EN: "Custom Payment"
    FI: "Erikoismaksutapa"
```

### Multiple Locations

Create separate template files for each location:
- `location1.yaml`
- `location2.yaml`
- etc.

Switch between them using the company dropdown.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore example templates in `templates/companies/`
- Customize logos in `templates/logos/`
- Check logs in `anomreceipt.log` for debugging

## Getting Help

- Check the logs: `anomreceipt.log`
- Verify all tests pass: `python3 test_app.py`
- Review example templates for reference
- Ensure all dependencies are installed

## Summary

That's it! You now know how to:
- ✓ Install and run AnomReceipt
- ✓ Connect to USB and network printers
- ✓ Create receipts with items
- ✓ Switch between languages
- ✓ Create custom company templates
- ✓ Design ASCII logos

Happy printing! 🎉
