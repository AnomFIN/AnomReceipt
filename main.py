#!/usr/bin/env python3
"""
AnomReceipt - Receipt Printing Application
Main entry point for the application
"""

import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication

from anomreceipt.gui import MainWindow


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('anomreceipt.log')
        ]
    )


def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting AnomReceipt application")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("AnomReceipt")
    app.setOrganizationName("AnomFIN")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
