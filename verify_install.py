#!/usr/bin/env python3
"""
Verification script for AnomReceipt installation.
Tests that all components are working correctly.
"""

import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_result(test_name, success, message=""):
    """Print test result."""
    status = "✓ PASS" if success else "✗ FAIL"
    color = "\033[92m" if success else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} - {test_name}")
    if message:
        print(f"       {message}")


def test_python_version():
    """Test Python version."""
    version = sys.version_info
    required = (3, 8)
    success = version >= required
    message = f"Python {version.major}.{version.minor}.{version.micro}"
    print_result("Python Version", success, message)
    return success


def test_pyside6():
    """Test PySide6 import."""
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
        print_result("PySide6", True, "All Qt modules imported successfully")
        return True
    except ImportError as e:
        print_result("PySide6", False, f"Import failed: {e}")
        return False


def test_ocr_dependencies():
    """Test OCR dependencies."""
    all_success = True
    
    try:
        import cv2
        print_result("OpenCV (cv2)", True, f"Version {cv2.__version__}")
    except ImportError as e:
        print_result("OpenCV (cv2)", False, str(e))
        all_success = False
    
    try:
        import numpy
        print_result("NumPy", True, f"Version {numpy.__version__}")
    except ImportError as e:
        print_result("NumPy", False, str(e))
        all_success = False
    
    try:
        import pytesseract
        print_result("PyTesseract", True, "Imported successfully")
    except ImportError as e:
        print_result("PyTesseract", False, str(e))
        all_success = False
    
    try:
        from PIL import Image
        print_result("Pillow (PIL)", True, "Imported successfully")
    except ImportError as e:
        print_result("Pillow (PIL)", False, str(e))
        all_success = False
    
    return all_success


def test_core_modules():
    """Test core application modules."""
    all_success = True
    
    try:
        from anomreceipt.core import setup_logging, get_logger, ErrorHandler
        print_result("Core - Logging", True, "Imported successfully")
    except ImportError as e:
        print_result("Core - Logging", False, str(e))
        all_success = False
    
    try:
        from anomreceipt.core import with_error_handling, safe_execute
        print_result("Core - Error Handling", True, "Imported successfully")
    except ImportError as e:
        print_result("Core - Error Handling", False, str(e))
        all_success = False
    
    return all_success


def test_ocr_module():
    """Test OCR module."""
    try:
        from anomreceipt.ocr import OCREngine, OCRResult
        print_result("OCR Module", True, "Imported successfully")
        
        # Test instantiation
        engine = OCREngine()
        print_result("OCR Engine Creation", True, "Engine instantiated")
        return True
    except Exception as e:
        print_result("OCR Module", False, str(e))
        return False


def test_gui_modules():
    """Test GUI modules."""
    all_success = True
    
    try:
        from anomreceipt.gui.modern_main_window import ModernMainWindow
        print_result("GUI - Main Window", True, "Imported successfully")
    except ImportError as e:
        print_result("GUI - Main Window", False, str(e))
        all_success = False
    
    try:
        from anomreceipt.gui.theme_manager import ThemeManager
        print_result("GUI - Theme Manager", True, "Imported successfully")
    except ImportError as e:
        print_result("GUI - Theme Manager", False, str(e))
        all_success = False
    
    try:
        from anomreceipt.gui.status_widget import StatusWidget
        print_result("GUI - Status Widget", True, "Imported successfully")
    except ImportError as e:
        print_result("GUI - Status Widget", False, str(e))
        all_success = False
    
    return all_success


def test_tesseract():
    """Test Tesseract OCR installation."""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print_result("Tesseract OCR", True, f"Version {version} installed")
        return True
    except Exception as e:
        print_result("Tesseract OCR", False, 
                    "Not installed (optional - OCR features will be disabled)")
        return False


def test_logging():
    """Test logging system."""
    try:
        from anomreceipt.core import setup_logging, get_logger
        
        # Setup logging
        setup_logging()
        logger = get_logger(__name__)
        
        # Test logging
        logger.info("Test log message")
        
        # Check if log file exists
        log_dir = Path("logs")
        if log_dir.exists():
            print_result("Logging System", True, f"Logs directory: {log_dir}")
            return True
        else:
            print_result("Logging System", False, "Logs directory not created")
            return False
    except Exception as e:
        print_result("Logging System", False, str(e))
        return False


def main():
    """Run all verification tests."""
    print_header("AnomReceipt Installation Verification")
    print("\nTesting all components...\n")
    
    results = {}
    
    # Run tests
    print_header("Python Environment")
    results['python'] = test_python_version()
    
    print_header("Core Dependencies")
    results['pyside6'] = test_pyside6()
    
    print_header("OCR Dependencies")
    results['ocr_deps'] = test_ocr_dependencies()
    
    print_header("Application Modules")
    results['core'] = test_core_modules()
    results['ocr'] = test_ocr_module()
    results['gui'] = test_gui_modules()
    
    print_header("Optional Components")
    results['tesseract'] = test_tesseract()
    
    print_header("System Features")
    results['logging'] = test_logging()
    
    # Summary
    print_header("Verification Summary")
    
    required_tests = ['python', 'pyside6', 'ocr_deps', 'core', 'ocr', 'gui', 'logging']
    optional_tests = ['tesseract']
    
    required_passed = sum(1 for test in required_tests if results.get(test, False))
    optional_passed = sum(1 for test in optional_tests if results.get(test, False))
    
    total_required = len(required_tests)
    total_optional = len(optional_tests)
    
    print(f"\nRequired Tests: {required_passed}/{total_required} passed")
    print(f"Optional Tests: {optional_passed}/{total_optional} passed")
    
    if required_passed == total_required:
        print("\n✓ All required components are working correctly!")
        print("✓ AnomReceipt is ready to use!")
        
        if optional_passed < total_optional:
            print("\n⚠ Note: Some optional components are not available:")
            if not results.get('tesseract', False):
                print("  - Tesseract OCR: Install for OCR functionality.")
                print("    Download: https://github.com/UB-Mannheim/tesseract/wiki")
        
        print("\nTo start the application:")
        print("  • Double-click launch.bat")
        print("  • Or run: python main.py")
        
        return 0
    else:
        print("\n✗ Some required components failed!")
        print("\nWhat to do:")
        print("  1. Check the error messages above.")
        print("  2. Run install.ps1 again.")
        print("  3. Check anomreceipt_install.log for details.")
        
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n✗ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
