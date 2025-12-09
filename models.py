"""
Data models for receipt printing application.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


@dataclass
class CompanyProfile:
    """Company profile with business information."""
    
    name: str
    address: str
    postal_code: str
    city: str
    country: str
    vat_id: str  # Y-tunnus in Finland
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    default_language: str = "FI"
    default_currency: str = "EUR"
    default_template: Optional[str] = None
    default_footer_fi: Optional[str] = None
    default_footer_en: Optional[str] = None
    logo_file: Optional[str] = None


@dataclass
class ReceiptItem:
    """Single line item on a receipt."""
    
    product_name: str
    quantity: Decimal
    unit_price: Decimal
    vat_rate: Decimal  # As percentage, e.g., 24.0 for 24%
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal (price * quantity) without VAT."""
        return self.quantity * self.unit_price
    
    @property
    def vat_amount(self) -> Decimal:
        """Calculate VAT amount."""
        return self.subtotal * (self.vat_rate / Decimal(100))
    
    @property
    def total(self) -> Decimal:
        """Calculate total including VAT."""
        return self.subtotal + self.vat_amount


@dataclass
class ReceiptData:
    """Complete receipt data."""
    
    company: CompanyProfile
    items: List[ReceiptItem] = field(default_factory=list)
    customer_name: Optional[str] = None
    reference_number: Optional[str] = None
    invoice_number: Optional[str] = None
    date_time: datetime = field(default_factory=datetime.now)
    payment_method: str = "Cash"
    language: str = "FI"
    currency: str = "EUR"
    custom_footer: Optional[str] = None
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate total before VAT."""
        return sum(item.subtotal for item in self.items)
    
    @property
    def total_vat(self) -> Decimal:
        """Calculate total VAT amount."""
        return sum(item.vat_amount for item in self.items)
    
    @property
    def total(self) -> Decimal:
        """Calculate grand total including VAT."""
        return sum(item.total for item in self.items)
    
    def get_vat_breakdown(self) -> dict:
        """Get VAT breakdown by rate."""
        breakdown = {}
        for item in self.items:
            rate = float(item.vat_rate)
            if rate not in breakdown:
                breakdown[rate] = {
                    'subtotal': Decimal(0),
                    'vat': Decimal(0)
                }
            breakdown[rate]['subtotal'] += item.subtotal
            breakdown[rate]['vat'] += item.vat_amount
        return breakdown
