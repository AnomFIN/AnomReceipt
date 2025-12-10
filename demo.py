#!/usr/bin/env python3
"""
Demo script showing AnomReceipt functionality.
"""
from decimal import Decimal
from datetime import datetime
from models import ReceiptItem, ReceiptData
from templates.companies import get_company, get_company_names
from templates.template_engine import ReceiptTemplate
from printer.escpos_printer import DummyPrinter


def print_separator():
    """Print a separator line."""
    print("\n" + "="*60 + "\n")


def demo_company_profiles():
    """Demonstrate company profiles."""
    print("Available Companies:")
    print_separator()
    
    for company_name in get_company_names():
        company = get_company(company_name)
        print(f"Company: {company.name}")
        print(f"  Address: {company.address}, {company.postal_code} {company.city}")
        print(f"  VAT ID: {company.vat_id}")
        print(f"  Default Language: {company.default_language}")
        if company.logo_file:
            print(f"  Logo: {company.logo_file}")
        print()


def demo_receipt_rendering():
    """Demonstrate receipt rendering."""
    print_separator()
    print("Receipt Rendering Demo - Helsinki eBike Service")
    print_separator()
    
    # Get company
    company = get_company("Helsinki eBike Service Oy")
    
    # Create items
    items = [
        ReceiptItem("eBike Battery 36V", Decimal("1"), Decimal("299.00"), Decimal("24")),
        ReceiptItem("Brake adjustment", Decimal("1"), Decimal("45.00"), Decimal("24")),
        ReceiptItem("Chain lubricant", Decimal("2"), Decimal("8.50"), Decimal("24"))
    ]
    
    # Create receipt
    receipt = ReceiptData(
        company=company,
        items=items,
        customer_name="Matti Meikäläinen",
        invoice_number="2025-001",
        date_time=datetime(2025, 12, 9, 14, 30),
        payment_method="MobilePay",
        language="FI"
    )
    
    # Render
    template = ReceiptTemplate()
    output = template.render(receipt)
    
    print(output)
    
    # Show calculations
    print("\n" + "-"*60)
    print(f"Subtotal: {float(receipt.subtotal):.2f} EUR")
    print(f"Total VAT: {float(receipt.total_vat):.2f} EUR")
    print(f"Grand Total: {float(receipt.total):.2f} EUR")
    
    # VAT breakdown
    print("\nVAT Breakdown:")
    for rate, amounts in receipt.get_vat_breakdown().items():
        print(f"  {rate:.0f}%: {float(amounts['vat']):.2f} EUR on {float(amounts['subtotal']):.2f} EUR")


def demo_english_receipt():
    """Demonstrate English receipt."""
    print_separator()
    print("English Receipt Demo - JugiSystems")
    print_separator()
    
    # Get company
    company = get_company("JugiSystems")
    
    # Create items
    items = [
        ReceiptItem("Server Setup", Decimal("1"), Decimal("500.00"), Decimal("24")),
        ReceiptItem("Security Audit", Decimal("4"), Decimal("150.00"), Decimal("24")),
    ]
    
    # Create receipt
    receipt = ReceiptData(
        company=company,
        items=items,
        customer_name="Tech Company Ltd",
        reference_number="REF-2025-123",
        invoice_number="INV-2025-456",
        date_time=datetime.now(),
        payment_method="Bank transfer",
        language="EN"
    )
    
    # Render
    template = ReceiptTemplate()
    output = template.render(receipt)
    
    print(output)


def demo_printer():
    """Demonstrate printer functionality."""
    print_separator()
    print("Printer Demo (Dummy Mode)")
    print_separator()
    
    # Create dummy printer
    printer = DummyPrinter()
    printer.connect()
    
    # Test print
    print("Performing test print...")
    printer.test_print()
    
    print(f"\nLast output from dummy printer:")
    print(printer.last_output)
    
    printer.disconnect()


def main():
    """Run all demos."""
    print("="*60)
    print("AnomReceipt - Demonstration")
    print("="*60)
    
    demo_company_profiles()
    demo_receipt_rendering()
    demo_english_receipt()
    demo_printer()
    
    print_separator()
    print("Demo completed!")
    print("\nTo launch the GUI application, run: python3 main.py")


if __name__ == "__main__":
    main()
