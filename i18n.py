"""
Internationalization support for Finnish and English.
"""

# Translation dictionaries
TRANSLATIONS = {
    "FI": {
        # Main window
        "app_title": "AnomReceipt - Kuitin Tulostus",
        "company": "Yritys",
        "template": "Pohja",
        "payment_method": "Maksutapa",
        "language": "Kieli",
        "customer_name": "Asiakkaan nimi",
        "reference": "Viite",
        "invoice_number": "Laskun numero",
        "date_time": "Päivämäärä ja aika",
        "preview": "Esikatselu",
        "print": "Tulosta kuitti",
        "test_print": "Testaa tulostin",
        "settings": "Asetukset",
        "logo_editor": "Logo-editori",
        "add_item": "Lisää rivi",
        "remove_item": "Poista rivi",
        
        # Items table
        "product": "Tuote",
        "quantity": "Määrä",
        "unit_price": "Yks. hinta",
        "vat_rate": "ALV-%",
        "total": "Yhteensä",
        
        # Totals
        "subtotal": "Välisumma",
        "total_vat": "ALV yhteensä",
        "grand_total": "Yhteensä",
        
        # Payment methods
        "cash": "Käteinen",
        "card": "Kortti",
        "visa": "Visa",
        "mobilepay": "MobilePay",
        "bank_transfer": "Pankkisiirto",
        "other": "Muu",
        # Preview editing
        "edit_preview": "Muokkaa esikatselua",
        "bold": "Lihavoi",
        "italic": "Kursivoi",
        "bigger": "Suurempi fontti",
        "smaller": "Pienempi fontti",
        "regenerate": "Päivitä datasta",
        
        # Settings dialog
        "settings_title": "Asetukset",
        "printer_settings": "Tulostimen asetukset",
        "connection_type": "Yhteystyyppi",
        "usb": "USB",
        "network": "Verkko",
        "device_path": "Laitepolku",
        "ip_address": "IP-osoite",
        "port": "Portti",
        "test_connection": "Testaa yhteys",
        "default_company": "Oletusyritys",
        "default_language": "Oletuskieli",
        "save": "Tallenna",
        "cancel": "Peruuta",
        
        # Logo editor
        "logo_editor_title": "Logo-editori",
        "logo_text": "Logo (ASCII-taide)",
        "logo_preview": "Esikatselu",
        "load_logo": "Lataa logo",
        "save_logo": "Tallenna logo",
        "clear_logo": "Tyhjennä",
        "import_png_logo": "Tuo PNG-logo",
        
        # Messages
        "print_success": "Kuitti tulostettu onnistuneesti",
        "print_error": "Virhe tulostuksessa",
        "test_success": "Testitulostus onnistui",
        "test_error": "Testitulostus epäonnistui",
        "connection_success": "Yhteys muodostettu",
        "connection_error": "Yhteys epäonnistui",
        "settings_saved": "Asetukset tallennettu",
        "logo_saved": "Logo tallennettu",
        "no_items": "Lisää vähintään yksi tuote",
    },
    "EN": {
        # Main window
        "app_title": "AnomReceipt - Receipt Printing",
        "company": "Company",
        "template": "Template",
        "payment_method": "Payment method",
        "language": "Language",
        "customer_name": "Customer name",
        "reference": "Reference",
        "invoice_number": "Invoice number",
        "date_time": "Date and time",
        "preview": "Preview",
        "print": "Print receipt",
        "test_print": "Test printer",
        "settings": "Settings",
        "logo_editor": "Logo editor",
        "add_item": "Add item",
        "remove_item": "Remove item",
        
        # Items table
        "product": "Product",
        "quantity": "Quantity",
        "unit_price": "Unit price",
        "vat_rate": "VAT %",
        "total": "Total",
        
        # Totals
        "subtotal": "Subtotal",
        "total_vat": "Total VAT",
        "grand_total": "Total",
        
        # Payment methods
        "cash": "Cash",
        "card": "Card",
        "visa": "Visa",
        "mobilepay": "MobilePay",
        "bank_transfer": "Bank transfer",
        "other": "Other",
        # Preview editing
        "edit_preview": "Edit preview",
        "bold": "Bold",
        "italic": "Italic",
        "bigger": "Font bigger",
        "smaller": "Font smaller",
        "regenerate": "Regenerate from data",
        
        # Settings dialog
        "settings_title": "Settings",
        "printer_settings": "Printer settings",
        "connection_type": "Connection type",
        "usb": "USB",
        "network": "Network",
        "device_path": "Device path",
        "ip_address": "IP address",
        "port": "Port",
        "test_connection": "Test connection",
        "default_company": "Default company",
        "default_language": "Default language",
        "save": "Save",
        "cancel": "Cancel",
        
        # Logo editor
        "logo_editor_title": "Logo Editor",
        "logo_text": "Logo (ASCII art)",
        "logo_preview": "Preview",
        "load_logo": "Load logo",
        "save_logo": "Save logo",
        "clear_logo": "Clear",
        "import_png_logo": "Import PNG logo",
        
        # Messages
        "print_success": "Receipt printed successfully",
        "print_error": "Printing error",
        "test_success": "Test print successful",
        "test_error": "Test print failed",
        "connection_success": "Connection established",
        "connection_error": "Connection failed",
        "settings_saved": "Settings saved",
        "logo_saved": "Logo saved",
        "no_items": "Add at least one item",
    }
}


class I18n:
    """Internationalization helper."""
    
    def __init__(self, language: str = "FI"):
        """
        Initialize i18n.
        
        Args:
            language: Language code ("FI" or "EN")
        """
        self.language = language
    
    def set_language(self, language: str):
        """Set current language."""
        if language in TRANSLATIONS:
            self.language = language
    
    def t(self, key: str) -> str:
        """
        Translate a key.
        
        Args:
            key: Translation key
            
        Returns:
            Translated string or key if not found
        """
        return TRANSLATIONS.get(self.language, {}).get(key, key)
    
    def __call__(self, key: str) -> str:
        """Allow calling instance directly."""
        return self.t(key)


# Global instance
_i18n = I18n()


def get_i18n() -> I18n:
    """Get global i18n instance."""
    return _i18n


def t(key: str) -> str:
    """Shorthand for translation."""
    return _i18n.t(key)
