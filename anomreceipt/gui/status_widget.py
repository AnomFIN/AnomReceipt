"""
Status widget for displaying application status with visual indicators.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class StatusWidget(QWidget):
    """
    Professional status widget with icons and colors.
    Shows processing, success, error, warning, and info states.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup UI
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Icon label
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(16, 16)
        layout.addWidget(self.icon_label)
        
        # Message label
        self.message_label = QLabel("Ready")
        message_font = QFont("Segoe UI", 10)
        self.message_label.setFont(message_font)
        layout.addWidget(self.message_label)
        
        layout.addStretch()
        
        # Timer for auto-clearing messages
        self.clear_timer = QTimer(self)
        self.clear_timer.timeout.connect(self.clear_status)
        
        # Default state
        self.show_info("Ready")
    
    def show_processing(self, message: str):
        """Show processing status."""
        self.icon_label.setText("⏳")
        self.message_label.setText(message)
        self.message_label.setStyleSheet("color: #3498db;")
        self.clear_timer.stop()
    
    def show_success(self, message: str, auto_clear: bool = True):
        """Show success status."""
        self.icon_label.setText("✓")
        self.message_label.setText(message)
        self.message_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        if auto_clear:
            self.clear_timer.start(5000)  # Clear after 5 seconds
    
    def show_error(self, message: str, auto_clear: bool = False):
        """Show error status."""
        self.icon_label.setText("✗")
        self.message_label.setText(message)
        self.message_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        if auto_clear:
            self.clear_timer.start(10000)  # Clear after 10 seconds
    
    def show_warning(self, message: str, auto_clear: bool = True):
        """Show warning status."""
        self.icon_label.setText("⚠")
        self.message_label.setText(message)
        self.message_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        
        if auto_clear:
            self.clear_timer.start(7000)  # Clear after 7 seconds
    
    def show_info(self, message: str, auto_clear: bool = False):
        """Show info status."""
        self.icon_label.setText("ℹ")
        self.message_label.setText(message)
        self.message_label.setStyleSheet("color: #7f8c8d;")
        
        if auto_clear:
            self.clear_timer.start(5000)  # Clear after 5 seconds
    
    def clear_status(self):
        """Clear status and return to ready state."""
        self.show_info("Ready")
        self.clear_timer.stop()
