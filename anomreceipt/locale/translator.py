"""
Simple translation system for Finnish and English
"""


class Translator:
    """Handles translations between Finnish and English"""
    
    TRANSLATIONS = {
        'EN': {
            'app_title': 'AnomReceipt - Receipt Printer',
            'company': 'Company',
            'select_company': 'Select Company',
            'payment_method': 'Payment Method',
            'cash': 'Cash',
            'card': 'Card',
            'mobilepay': 'MobilePay',
            'bank': 'Bank Transfer',
            'items': 'Items',
            'add_item': 'Add Item',
            'remove_item': 'Remove Item',
            'item_name': 'Item Name',
            'price': 'Price',
            'quantity': 'Quantity',
            'preview': 'Preview',
            'print': 'Print',
            'connect_usb': 'Connect USB',
            'connect_network': 'Connect Network',
            'disconnect': 'Disconnect',
            'printer_status': 'Printer Status',
            'not_connected': 'Not Connected',
            'connected': 'Connected',
            'host': 'Host/IP',
            'port': 'Port',
            'logo_editor': 'ASCII Logo Editor',
            'edit_logo': 'Edit Logo',
            'save_logo': 'Save Logo',
            'load_logo': 'Load Logo',
            'clear': 'Clear',
            'settings': 'Settings',
            'language': 'Language',
            'receipt_language': 'Receipt Language',
            'success': 'Success',
            'error': 'Error',
            'print_success': 'Receipt printed successfully!',
            'print_error': 'Failed to print receipt',
            'connect_success': 'Connected to printer',
            'connect_error': 'Failed to connect to printer',
            'total': 'Total',
            'subtotal': 'Subtotal',
            'vat': 'VAT 24%',
        },
        'FI': {
            'app_title': 'AnomReceipt - Kuittitulostin',
            'company': 'Yritys',
            'select_company': 'Valitse Yritys',
            'payment_method': 'Maksutapa',
            'cash': 'Käteinen',
            'card': 'Kortti',
            'mobilepay': 'MobilePay',
            'bank': 'Tilisiirto',
            'items': 'Tuotteet',
            'add_item': 'Lisää Tuote',
            'remove_item': 'Poista Tuote',
            'item_name': 'Tuotteen Nimi',
            'price': 'Hinta',
            'quantity': 'Määrä',
            'preview': 'Esikatselu',
            'print': 'Tulosta',
            'connect_usb': 'Yhdistä USB',
            'connect_network': 'Yhdistä Verkko',
            'disconnect': 'Katkaise Yhteys',
            'printer_status': 'Tulostimen Tila',
            'not_connected': 'Ei Yhteyttä',
            'connected': 'Yhdistetty',
            'host': 'Osoite/IP',
            'port': 'Portti',
            'logo_editor': 'ASCII Logo Editori',
            'edit_logo': 'Muokkaa Logoa',
            'save_logo': 'Tallenna Logo',
            'load_logo': 'Lataa Logo',
            'clear': 'Tyhjennä',
            'settings': 'Asetukset',
            'language': 'Kieli',
            'receipt_language': 'Kuitin Kieli',
            'success': 'Onnistui',
            'error': 'Virhe',
            'print_success': 'Kuitti tulostettu onnistuneesti!',
            'print_error': 'Kuitin tulostus epäonnistui',
            'connect_success': 'Yhdistetty tulostimeen',
            'connect_error': 'Tulostimeen yhdistäminen epäonnistui',
            'total': 'Yhteensä',
            'subtotal': 'Veroton yhteensä',
            'vat': 'ALV 24%',
        }
    }
    
    def __init__(self, language='EN'):
        self.language = language
        
    def set_language(self, language):
        """Set the current language"""
        if language in self.TRANSLATIONS:
            self.language = language
            return True
        return False
        
    def get_language(self):
        """Get the current language"""
        return self.language
        
    def translate(self, key):
        """Translate a key to the current language"""
        return self.TRANSLATIONS.get(self.language, {}).get(key, key)
        
    def t(self, key):
        """Shorthand for translate"""
        return self.translate(key)
