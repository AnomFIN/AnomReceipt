"""
Receipt template engine for rendering receipts.
"""
from typing import Optional
from decimal import Decimal
from models import ReceiptData, CompanyProfile
import os
import logging

logger = logging.getLogger(__name__)

# Template paths
LOGOS_DIR = os.path.join("templates", "logos")

def get_company_logo(company: CompanyProfile):
    """Resolve company logo path and type.
    Returns (path, type) where type in {'txt','png'} or (None, None) if not found.
    """
    # Explicit file set
    if company.logo_file:
        path = os.path.join(LOGOS_DIR, company.logo_file)
        if os.path.exists(path):
            ext = os.path.splitext(path)[1].lower()
            if ext == '.txt':
                return path, 'txt'
            if ext == '.png':
                return path, 'png'
    # Try default by company safe name
    safe = ''.join(c if c.isalnum() else '_' for c in company.name.lower())
    for ext in ('.png', '.txt'):
        path = os.path.join(LOGOS_DIR, safe + ext)
        if os.path.exists(path):
            return path, ext.lstrip('.')
    return None, None


class ReceiptTemplate:
    """Base class for receipt templates."""
    
    def __init__(self, width: int = 42):
        """
        Initialize template.
        
        Args:
            width: Character width of the receipt (default 42 for TM-T70II)
        """
        self.width = width
    
    def _center(self, text: str) -> str:
        """Center text within receipt width."""
        return text.center(self.width)
    
    def _left_right(self, left: str, right: str) -> str:
        """Align text left and right on same line."""
        available = self.width - len(left)
        return left + right.rjust(available)
    
    def _line(self, char: str = "-") -> str:
        """Create a horizontal line."""
        return char * self.width
    
    def _load_logo(self, company: CompanyProfile) -> list:
        """Load ASCII logo lines if present. PNGs are handled in preview/printer."""
        path, ltype = get_company_logo(company)
        if not path:
            return []
        if ltype == 'png':
            return []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return [line.rstrip() for line in f.readlines()]
        except Exception as e:
            logger.error(f"Failed to load logo {path}: {e}")
            return []
    
    def render(self, data: ReceiptData) -> str:
        """
        Render receipt to text.
        
        Args:
            data: Receipt data to render
            
        Returns:
            Formatted receipt text
        """
        lines = []
        
        # Logo
        logo_lines = self._load_logo(data.company)
        for logo_line in logo_lines:
            lines.append(self._center(logo_line))
        if logo_lines:
            lines.append("")
        
        # Header
        lines.extend(self._render_header(data))
        lines.append("")
        
        # Items
        lines.extend(self._render_items(data))
        lines.append("")
        
        # Totals
        lines.extend(self._render_totals(data))
        lines.append("")
        
        # Footer
        lines.extend(self._render_footer(data))
        
        return "\n".join(lines)
    
    def _render_header(self, data: ReceiptData) -> list:
        """Render receipt header."""
        lines = []
        company = data.company
        
        lines.append(self._center(company.name))
        lines.append(self._center(company.address))
        lines.append(self._center(f"{company.postal_code} {company.city}"))
        
        if company.phone:
            lines.append(self._center(f"Tel: {company.phone}"))
        if company.email:
            lines.append(self._center(company.email))
        
        vat_label = "Y-tunnus" if data.language == "FI" else "VAT ID"
        lines.append(self._center(f"{vat_label}: {company.vat_id}"))
        
        lines.append(self._line("="))
        
        # Receipt info
        date_str = data.date_time.strftime("%d.%m.%Y %H:%M")
        lines.append(self._left_right("Date:", date_str))
        
        if data.invoice_number:
            inv_label = "Lasku nro" if data.language == "FI" else "Invoice no"
            lines.append(self._left_right(f"{inv_label}:", data.invoice_number))
        
        if data.reference_number:
            ref_label = "Viite" if data.language == "FI" else "Reference"
            lines.append(self._left_right(f"{ref_label}:", data.reference_number))
        
        if data.customer_name:
            cust_label = "Asiakas" if data.language == "FI" else "Customer"
            lines.append(self._left_right(f"{cust_label}:", data.customer_name))
        
        lines.append(self._line("="))
        
        return lines
    
    def _render_items(self, data: ReceiptData) -> list:
        """Render receipt items."""
        lines = []
        
        # Headers
        if data.language == "FI":
            header = "Tuote                  Kpl   Hinta    Yht"
        else:
            header = "Product                Qty   Price    Tot"
        lines.append(header)
        lines.append(self._line("-"))
        
        # Items
        for item in data.items:
            # Product name (truncate if too long)
            product = item.product_name[:20].ljust(20)
            qty = f"{float(item.quantity):.1f}".rjust(5)
            price = f"{float(item.unit_price):.2f}".rjust(7)
            total = f"{float(item.total):.2f}".rjust(8)
            
            lines.append(f"{product} {qty} {price} {total}")
            
            # VAT info
            vat_text = f"  (ALV {float(item.vat_rate):.0f}%)" if data.language == "FI" else f"  (VAT {float(item.vat_rate):.0f}%)"
            lines.append(vat_text)
        
        return lines
    
    def _render_totals(self, data: ReceiptData) -> list:
        """Render totals section."""
        lines = []
        lines.append(self._line("="))
        
        # Subtotal
        subtotal_label = "Välisumma" if data.language == "FI" else "Subtotal"
        lines.append(self._left_right(f"{subtotal_label}:", f"{float(data.subtotal):.2f} {data.currency}"))
        
        # VAT breakdown
        breakdown = data.get_vat_breakdown()
        for rate, amounts in sorted(breakdown.items()):
            vat_label = f"ALV {rate:.0f}%" if data.language == "FI" else f"VAT {rate:.0f}%"
            lines.append(self._left_right(f"{vat_label}:", f"{float(amounts['vat']):.2f} {data.currency}"))
        
        lines.append(self._line("-"))
        
        # Total
        total_label = "YHTEENSÄ" if data.language == "FI" else "TOTAL"
        lines.append(self._left_right(f"{total_label}:", f"{float(data.total):.2f} {data.currency}"))
        
        return lines
    
    def _render_footer(self, data: ReceiptData) -> list:
        """Render receipt footer."""
        lines = []
        lines.append(self._line("="))
        
        # Payment method
        payment_label = "Maksutapa" if data.language == "FI" else "Payment method"
        lines.append(self._left_right(f"{payment_label}:", data.payment_method))
        
        # Optional payment details (e.g., card details)
        if data.payment_details:
            details = data.payment_details
            # Standard ordering
            mapping = [
                ("card_type", "Card"),
                ("pan_masked", "PAN"),
                ("auth_code", "Auth"),
                ("aid", "AID"),
                ("app_label", "App"),
                ("tvr", "TVR"),
                ("tsi", "TSI"),
                ("transaction_id", "TransID"),
                ("terminal_id", "Terminal"),
            ]
            for key, label in mapping:
                if details.get(key):
                    lines.append(self._left_right(f"{label}:", str(details[key])))
        
        lines.append("")
        
        # Custom footer or company default
        if data.custom_footer:
            footer_text = data.custom_footer
        elif data.language == "FI" and data.company.default_footer_fi:
            footer_text = data.company.default_footer_fi
        elif data.language == "EN" and data.company.default_footer_en:
            footer_text = data.company.default_footer_en
        else:
            footer_text = "Kiitos käynnistä!" if data.language == "FI" else "Thank you for your visit!"
        
        lines.append(self._center(footer_text))
        
        return lines
