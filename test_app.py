#!/usr/bin/env python3
"""
Test script for AnomReceipt application
Tests all core functionality without requiring a printer
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from anomreceipt.printer import ESCPOSPrinter
from anomreceipt.templates import TemplateManager, ReceiptTemplate
from anomreceipt.locale import Translator


def test_printer():
    """Test printer module"""
    print("Testing Printer Module...")
    printer = ESCPOSPrinter()
    
    assert not printer.is_connected(), "Printer should not be connected initially"
    print("  ✓ Printer initialization OK")
    print("  ✓ Connection status check OK")
    

def test_templates():
    """Test template system"""
    print("\nTesting Template System...")
    
    tm = TemplateManager('templates/companies')
    templates = tm.list_templates()
    
    assert len(templates) > 0, "Should have at least one template"
    print(f"  ✓ Found {len(templates)} templates")
    
    for template_name in templates:
        template = tm.get_template(template_name)
        assert template is not None, f"Template {template_name} should load"
        assert template.company_info, "Template should have company info"
        print(f"  ✓ Template '{template_name}' loads correctly")
        
        # Test receipt generation
        items = [{'name': 'Test', 'qty': '1', 'price': '10.00€'}]
        receipt = template.generate_receipt(items, 'cash', 'EN')
        
        assert 'header' in receipt, "Receipt should have header"
        assert 'items' in receipt, "Receipt should have items"
        assert 'footer' in receipt, "Receipt should have footer"
        print(f"  ✓ Receipt generation OK for '{template_name}'")
        

def test_translations():
    """Test translation system"""
    print("\nTesting Translation System...")
    
    trans_en = Translator('EN')
    trans_fi = Translator('FI')
    
    # Test key translations
    assert trans_en.translate('print') == 'Print', "English translation should work"
    assert trans_fi.translate('print') == 'Tulosta', "Finnish translation should work"
    print("  ✓ English translations OK")
    print("  ✓ Finnish translations OK")
    
    # Test language switching
    trans = Translator('EN')
    assert trans.get_language() == 'EN', "Initial language should be EN"
    trans.set_language('FI')
    assert trans.get_language() == 'FI', "Language should switch to FI"
    print("  ✓ Language switching OK")


def test_gui_imports():
    """Test GUI component imports"""
    print("\nTesting GUI Components...")
    
    import os
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    from PyQt5.QtWidgets import QApplication
    from anomreceipt.gui import MainWindow, LogoEditor
    
    app = QApplication(sys.argv)
    
    # Test main window
    window = MainWindow()
    assert window.windowTitle(), "Window should have a title"
    print("  ✓ MainWindow initialization OK")
    
    # Test logo editor
    editor = LogoEditor(window)
    assert editor.windowTitle(), "Editor should have a title"
    print("  ✓ LogoEditor initialization OK")
    

def main():
    """Run all tests"""
    print("=" * 60)
    print("AnomReceipt - Test Suite")
    print("=" * 60)
    
    try:
        test_printer()
        test_templates()
        test_translations()
        test_gui_imports()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
