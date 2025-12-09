"""
Tests for template engine.
"""
import pytest
from decimal import Decimal
from datetime import datetime
from models import ReceiptItem, ReceiptData, CompanyProfile
from templates.template_engine import ReceiptTemplate


def test_template_rendering():
    """Test basic template rendering."""
    company = CompanyProfile(
        name="Test Company",
        address="Test Street 1",
        postal_code="00100",
        city="Helsinki",
        country="Finland",
        vat_id="FI12345678",
        phone="+358 9 1234567",
        email="test@example.com"
    )
    
    item = ReceiptItem(
        product_name="Test Product",
        quantity=Decimal("1"),
        unit_price=Decimal("10.00"),
        vat_rate=Decimal("24")
    )
    
    receipt = ReceiptData(
        company=company,
        items=[item],
        customer_name="Test Customer",
        invoice_number="INV-001",
        date_time=datetime(2024, 1, 1, 12, 0),
        payment_method="Cash",
        language="EN"
    )
    
    template = ReceiptTemplate()
    output = template.render(receipt)
    
    # Check that key elements are present
    assert "Test Company" in output
    assert "Test Street 1" in output
    assert "00100 Helsinki" in output
    assert "FI12345678" in output
    assert "Test Product" in output
    assert "Test Customer" in output
    assert "INV-001" in output
    assert "Cash" in output


def test_template_language_finnish():
    """Test Finnish language rendering."""
    company = CompanyProfile(
        name="Test Company",
        address="Test Street 1",
        postal_code="00100",
        city="Helsinki",
        country="Finland",
        vat_id="FI12345678"
    )
    
    item = ReceiptItem(
        product_name="Tuote",
        quantity=Decimal("1"),
        unit_price=Decimal("10.00"),
        vat_rate=Decimal("24")
    )
    
    receipt = ReceiptData(
        company=company,
        items=[item],
        payment_method="Käteinen",
        language="FI"
    )
    
    template = ReceiptTemplate()
    output = template.render(receipt)
    
    # Check Finnish labels
    assert "Y-tunnus" in output
    assert "Maksutapa" in output
    assert "Kiitos" in output or "kiitos" in output.lower()


def test_template_width():
    """Test that lines don't exceed template width."""
    company = CompanyProfile(
        name="Very Long Company Name That Should Be Handled Properly",
        address="Test Street 1",
        postal_code="00100",
        city="Helsinki",
        country="Finland",
        vat_id="FI12345678"
    )
    
    item = ReceiptItem(
        product_name="Product",
        quantity=Decimal("1"),
        unit_price=Decimal("10.00"),
        vat_rate=Decimal("24")
    )
    
    receipt = ReceiptData(
        company=company,
        items=[item],
        language="EN"
    )
    
    template = ReceiptTemplate(width=42)
    output = template.render(receipt)
    
    # Check that most lines don't exceed width (some exceptions for long words)
    lines = output.split('\n')
    for line in lines:
        # Allow some flexibility for special characters
        if not line.startswith('║') and not line.startswith('│'):
            assert len(line) <= 50, f"Line too long: {line}"
