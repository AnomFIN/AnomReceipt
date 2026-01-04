#!/usr/bin/env python3
"""
AnomReceipt - Professional Receipt Printing Application
Main entry point with comprehensive error handling
"""

import sys
import traceback
from pathlib import Path

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
except ImportError as e:
    print("ERROR: PyQt5 is not installed.")
    print("Please run: pip install -r requirements.txt")
    print(f"Details: {e}")
    sys.exit(1)

from anomreceipt.gui.main_window import MainWindow


def main():
    """
    Main application entry point.
    Fully defensive with comprehensive error handling.
    """
    app = None
    
    try:
        # Enable High DPI scaling for modern displays
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("AnomReceipt")
        app.setOrganizationName("AnomFIN")
        app.setApplicationVersion("2.0.0")
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Run application
        exit_code = app.exec()
        
        return exit_code
    
    except Exception as e:
        error_msg = f"Fatal error during application startup: {e}"
        print(f"\n{error_msg}")
        traceback.print_exc()
        
        return 1


if __name__ == '__main__':
    sys.exit(main())
