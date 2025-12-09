"""
ASCII Logo Editor for receipt logos
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QFileDialog, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LogoEditor(QDialog):
    """ASCII Logo Editor dialog"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator
        self.current_logo = ""
        self.logos_dir = Path('templates/logos')
        self.logos_dir.mkdir(parents=True, exist_ok=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle(self.tr('logo_editor'))
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        # Info label
        info = QLabel(self.tr('edit_logo_info'))
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Text editor for ASCII art
        self.logo_text = QTextEdit()
        self.logo_text.setPlaceholderText("Enter your ASCII logo here...\nMax width: 48 characters")
        
        # Use monospace font for proper ASCII art display
        font = QFont("Courier New", 10)
        if not font.exactMatch():
            font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.logo_text.setFont(font)
        self.logo_text.setLineWrapMode(QTextEdit.NoWrap)
        
        layout.addWidget(self.logo_text)
        
        # Character counter
        self.char_label = QLabel("Lines: 0 | Max line length: 0")
        layout.addWidget(self.char_label)
        self.logo_text.textChanged.connect(self.update_stats)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton(self.tr('clear'))
        self.clear_btn.clicked.connect(self.clear_logo)
        button_layout.addWidget(self.clear_btn)
        
        self.load_btn = QPushButton(self.tr('load_logo'))
        self.load_btn.clicked.connect(self.load_logo)
        button_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton(self.tr('save_logo'))
        self.save_btn.clicked.connect(self.save_logo)
        button_layout.addWidget(self.save_btn)
        
        button_layout.addStretch()
        
        self.ok_btn = QPushButton('OK')
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def tr(self, key):
        """Translate a key"""
        if self.translator:
            return self.translator.translate(key)
        return key
        
    def tr_info(self, key):
        """Get info text"""
        if key == 'edit_logo_info':
            if self.translator and self.translator.get_language() == 'FI':
                return "Luo ASCII-logo kuitille. Suositeltu leveys: 48 merkkiä."
            return "Create an ASCII logo for receipts. Recommended width: 48 characters."
        return ""
        
    def update_stats(self):
        """Update character statistics"""
        text = self.logo_text.toPlainText()
        lines = text.split('\n')
        line_count = len(lines)
        max_length = max(len(line) for line in lines) if lines else 0
        
        self.char_label.setText(f"Lines: {line_count} | Max line length: {max_length}")
        
        # Warn if line is too long
        if max_length > 48:
            self.char_label.setStyleSheet("color: red;")
        else:
            self.char_label.setStyleSheet("")
            
    def clear_logo(self):
        """Clear the logo text"""
        self.logo_text.clear()
        
    def load_logo(self):
        """Load logo from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr('load_logo'),
            str(self.logos_dir),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    logo_text = f.read()
                self.logo_text.setPlainText(logo_text)
                logger.info(f"Loaded logo from {file_path}")
            except Exception as e:
                logger.error(f"Error loading logo: {e}")
                QMessageBox.warning(self, self.tr('error'), f"Failed to load logo: {e}")
                
    def save_logo(self):
        """Save logo to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr('save_logo'),
            str(self.logos_dir),
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.logo_text.toPlainText())
                logger.info(f"Saved logo to {file_path}")
                QMessageBox.information(self, self.tr('success'), "Logo saved successfully!")
            except Exception as e:
                logger.error(f"Error saving logo: {e}")
                QMessageBox.warning(self, self.tr('error'), f"Failed to save logo: {e}")
                
    def get_logo(self):
        """Get the current logo text"""
        return self.logo_text.toPlainText()
        
    def set_logo(self, logo_text):
        """Set the logo text"""
        self.logo_text.setPlainText(logo_text)
