#!/usr/bin/env python3
"""
AnomReceipt - Professional Windows Receipt Application
Main entry point with comprehensive error handling
"""

import sys
from pathlib import Path

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
except ImportError as e:
    print("ERROR: PySide6 is not installed.")
    print("Please run the installer: install.ps1")
    print(f"Details: {e}")
    sys.exit(1)

from anomreceipt.core import setup_logging, get_logger, ErrorHandler
from anomreceipt.gui.modern_main_window import ModernMainWindow


def main():
    """
    Main application entry point.
    Fully defensive with comprehensive error handling.
    """
    logger = None
    app = None
    
    try:
        # Setup logging first
        setup_logging()
        logger = get_logger(__name__)
        logger.info("=" * 80)
        logger.info("AnomReceipt Application Starting")
        logger.info("=" * 80)
        
        # Enable High DPI scaling for modern Windows
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("AnomReceipt")
        app.setOrganizationName("AnomFIN")
        app.setApplicationVersion("2.0.0")
        
        # Set global exception handler
        sys.excepthook = ErrorHandler.handle_exception
        
        logger.info("Creating main window...")
        
        # Create and show main window
        window = ModernMainWindow()
        window.show()
        
        logger.info("Application ready")
        
        # Run application
        exit_code = app.exec()
        
        logger.info(f"Application exiting with code {exit_code}")
        return exit_code
    
    except Exception as e:
        error_msg = f"Fatal error during application startup: {e}"
        
        if logger:
            logger.critical(error_msg, exc_info=True)
        else:
            print(f"\n{error_msg}")
            import traceback
            traceback.print_exc()
        
        try:
            if app:
                ErrorHandler.show_error(
                    "Application Startup Failed",
                    "AnomReceipt failed to start.\n\n"
                    f"Error: {e}\n\n"
                    "What you can do:\n"
                    "• Check the log file for details\n"
                    "• Verify all dependencies are installed\n"
                    "• Run install.ps1 to reinstall\n"
                    "• Contact support if the problem persists"
                )
        except:
            pass
        
        return 1


if __name__ == '__main__':
    sys.exit(main())
