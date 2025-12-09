#!/usr/bin/env python3
"""
AnomReceipt - Linux Receipt Printing Application
Main entry point.
"""
import sys
import logging
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("AnomReceipt")
    app.setOrganizationName("AnomFIN")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
