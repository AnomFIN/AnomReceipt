"""
Tests for receipt data models.
"""
import pytest
from decimal import Decimal
from datetime import datetime
from models import ReceiptItem, ReceiptData, CompanyProfile


def test_receipt_item_calculations():
    """Test receipt item calculations."""
    item = ReceiptItem(
        product_name="Test Product",
        quantity=Decimal("2"),
        unit_price=Decimal("10.00"),
        vat_rate=Decimal("24")
    )
    
    # Test subtotal
    assert item.subtotal == Decimal("20.00")
    
    # Test VAT amount
    assert item.vat_amount == Decimal("4.80")
    
    # Test total
    assert item.total == Decimal("24.80")


def test_receipt_data_totals():
    """Test receipt data total calculations."""
    company = CompanyProfile(
        name="Test Company",
        address="Test Street 1",
        postal_code="00100",
        city="Helsinki",
        country="Finland",
        vat_id="FI12345678"
    )
    
    item1 = ReceiptItem(
        product_name="Product 1",
        quantity=Decimal("1"),
        unit_price=Decimal("10.00"),
        vat_rate=Decimal("24")
    )
    
    item2 = ReceiptItem(
        product_name="Product 2",
        quantity=Decimal("2"),
        unit_price=Decimal("5.00"),
        vat_rate=Decimal("14")
    )
    
    receipt = ReceiptData(
        company=company,
        items=[item1, item2]
    )
    
    # Test subtotal
    assert receipt.subtotal == Decimal("20.00")
    
    # Test total VAT
    expected_vat = Decimal("2.40") + Decimal("1.40")  # 24% of 10 + 14% of 10
    assert receipt.total_vat == expected_vat
    
    # Test grand total
    expected_total = Decimal("20.00") + expected_vat
    assert receipt.total == expected_total


def test_vat_breakdown():
    """Test VAT breakdown by rate."""
    company = CompanyProfile(
        name="Test Company",
        address="Test Street 1",
        postal_code="00100",
        city="Helsinki",
        country="Finland",
        vat_id="FI12345678"
    )
    
    item1 = ReceiptItem(
        product_name="Product 1",
        quantity=Decimal("1"),
        unit_price=Decimal("10.00"),
        vat_rate=Decimal("24")
    )
    
    item2 = ReceiptItem(
        product_name="Product 2",
        quantity=Decimal("1"),
        unit_price=Decimal("10.00"),
        vat_rate=Decimal("24")
    )
    
    item3 = ReceiptItem(
        product_name="Product 3",
        quantity=Decimal("1"),
        unit_price=Decimal("10.00"),
        vat_rate=Decimal("14")
    )
    
    receipt = ReceiptData(
        company=company,
        items=[item1, item2, item3]
    )
    
    breakdown = receipt.get_vat_breakdown()
    
    # Check 24% VAT
    assert 24.0 in breakdown
    assert breakdown[24.0]['subtotal'] == Decimal("20.00")
    assert breakdown[24.0]['vat'] == Decimal("4.80")
    
    # Check 14% VAT
    assert 14.0 in breakdown
    assert breakdown[14.0]['subtotal'] == Decimal("10.00")
    assert breakdown[14.0]['vat'] == Decimal("1.40")
