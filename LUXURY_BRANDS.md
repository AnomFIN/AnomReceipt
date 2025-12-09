# Luxury Brand Templates

AnomReceipt includes professional templates for luxury brands, suitable for retail point-of-sale systems and boutique operations.

## Available Luxury Brand Templates

### Fashion Houses

#### **Louis Vuitton**
- Founded: 1854, Paris, France
- Template: `louis_vuitton.yaml`
- Logo: Premium ASCII art with iconic LV monogram
- Suitable for: Leather goods, fashion accessories, luxury travel items

#### **Gucci**
- Founded: 1921, Florence, Italy
- Template: `gucci.yaml`
- Logo: Classic double G design
- Suitable for: Fashion, accessories, leather goods

#### **Hermès**
- Founded: 1837, Paris, France
- Template: `hermes.yaml`
- Logo: Elegant typography with brand heritage
- Suitable for: Luxury leather goods, silk scarves, accessories

#### **Chanel**
- Founded: 1910, Paris, France
- Template: `chanel.json`
- Logo: Iconic interlocking CC monogram
- Suitable for: Fashion, fragrances, accessories, cosmetics

#### **Prada**
- Founded: 1913, Milan, Italy
- Template: `prada.json`
- Logo: Bold typography with Italian heritage
- Suitable for: Fashion, leather goods, eyewear

#### **Burberry**
- Founded: 1856, London, UK
- Template: Available in logo library
- Logo: Classic British styling
- Suitable for: Fashion, outerwear, accessories

#### **Versace**
- Founded: 1978, Milan, Italy
- Template: Available in logo library
- Logo: Medusa head design
- Suitable for: High fashion, accessories

#### **Dior**
- Founded: 1946, Paris, France
- Template: Available in logo library
- Logo: Christian Dior elegance
- Suitable for: Haute couture, fragrances, accessories

### Luxury Timepieces

#### **Rolex**
- Founded: 1905, Geneva, Switzerland
- Template: `rolex.yaml`
- Logo: Crown with five-pointed star design
- Suitable for: Luxury watches, timepieces

#### **Cartier**
- Founded: 1847, Paris, France
- Template: Available in logo library
- Logo: Elegant French luxury design
- Suitable for: Jewelry, watches, accessories

## Usage for Commercial Applications

### For Boutique Owners

These templates are designed to be:
- **Professional**: Premium ASCII art suitable for receipt printers
- **Authentic**: Respectful representation of brand heritage
- **Customizable**: Easy to modify for specific boutique needs

### Integration Steps

1. **Select Your Template**
   ```python
   from anomreceipt.templates import TemplateManager
   
   tm = TemplateManager('templates/companies')
   template = tm.get_template('Louis Vuitton')
   ```

2. **Customize Company Information**
   Edit the YAML/JSON file with your boutique's details:
   ```yaml
   company_info:
     name: "LOUIS VUITTON - HELSINKI"
     address: "Your Boutique Address"
     city: "Your City"
     vat_id: "Your VAT ID"
     phone: "Your Phone"
   ```

3. **Generate Receipts**
   ```python
   receipt = template.generate_receipt(
       items=[{'name': 'Handbag', 'qty': '1', 'price': '2500.00€'}],
       payment_method='card',
       language='EN'
   )
   ```

## Receipt Customization

### Settings Available

Access via Settings Dialog (⚙ Settings button):

- **Receipt Width**: 32-80 characters (default: 48)
- **Receipt Length**: 50-200 lines (default: 80)
- **Logo Max Width**: 20-80 characters (default: 48)
- **Logo Max Height**: 5-30 lines (default: 20)
- **Feed Lines**: 0-10 lines after print
- **Auto Cut**: Automatic paper cutting
- **Bold Header**: Bold formatting for header text
- **Double Width Total**: Emphasize total amount

### Creating Custom Logos

Use the built-in ASCII Logo Editor:

1. Click "Edit Logo" button
2. Browse the logo library (26+ pre-designed logos)
3. Select a luxury brand template
4. Customize or create your own
5. Save to your template

### Logo Library

The application includes pre-designed logos for:

**Fashion & Luxury:**
- Louis Vuitton, Gucci, Hermès, Chanel, Prada
- Burberry, Versace, Dior

**Watches & Jewelry:**
- Rolex, Cartier

**Finnish Brands:**
- LähiVakuutus (LV Insurance)
- Kesko, Prisma, HOK-Elanto
- OP, Nordea, S-Pankki
- Elisa, Telia
- Stockmann, Alko

**Generic Templates:**
- Minimalist border designs
- Simple elegant frames
- Customizable placeholders

## Commercial Licensing Note

**Important:** These templates are provided as examples for the AnomReceipt application. If you plan to use this application commercially for actual luxury brand retailers:

1. **Obtain proper authorization** from the brand owner
2. **Comply with brand guidelines** for representation
3. **Ensure legal compliance** with trademark laws
4. **Contact brands directly** for official point-of-sale systems

This application is suitable for:
- ✓ Demonstration purposes
- ✓ Development and testing
- ✓ Internal retail system prototypes
- ✓ Custom boutique implementations (with brand authorization)

## Technical Specifications

### Receipt Format
- Character encoding: UTF-8
- Box drawing characters: Unicode box-drawing characters
- Print width: Configurable (default 48 characters)
- Printer compatibility: ESC/POS standard

### Supported Payment Methods
All templates support:
- Cash (Käteinen / Cash)
- Credit Card (Luottokortti / Credit Card)
- Mobile Payment (Mobiilimaksu / Mobile Payment)
- Wire Transfer (Tilisiirto / Wire Transfer)

### Language Support
- English (EN)
- Finnish (FI)
- Bilingual receipts with automatic translation

## Receipt Examples

### Louis Vuitton Receipt Structure
```
╔══════════════════════════════════════════════╗
║          L O U I S   V U I T T O N          ║
╚══════════════════════════════════════════════╝

LOUIS VUITTON
Address
City, Country
VAT ID: XXX
Date & Time

------------------------------------------------
Items with prices
------------------------------------------------
Subtotal, VAT, TOTAL
Payment Method
Thank you message
```

### Customization Tips

1. **Adjust width for your printer**:
   - Standard: 48 characters
   - Wide format: 64-80 characters
   - Compact: 32-42 characters

2. **Logo considerations**:
   - Keep within printer width
   - Test print before production
   - Use monospace fonts for editing

3. **Brand compliance**:
   - Follow official brand guidelines
   - Maintain brand color schemes (if color printer)
   - Use approved brand representations

## Support for Brand Implementation

For commercial implementations:

1. **Customization Service**: Contact for template customization
2. **Brand Integration**: Professional assistance available
3. **Training**: User training for boutique staff
4. **Support**: Technical support for deployment

## Future Enhancements

Planned features for luxury retail:

- QR code integration for authentication
- Multi-currency support
- Customer loyalty program integration
- Digital receipt email/SMS
- Signature capture for high-value items
- Serial number tracking
- Return/exchange receipt formatting

---

For questions about commercial use or custom template development, please refer to the main documentation or contact the development team.
