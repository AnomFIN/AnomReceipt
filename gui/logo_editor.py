"""
ASCII logo editor dialog.
"""
import os
import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from i18n import get_i18n

logger = logging.getLogger(__name__)

# Template paths
LOGOS_DIR = os.path.join("templates", "logos")


class LogoEditorDialog(QDialog):
    """Dialog for editing ASCII logos."""
    
    def __init__(self, company_name: str, parent=None):
        """
        Initialize logo editor.
        
        Args:
            company_name: Name of the company
            parent: Parent widget
        """
        super().__init__(parent)
        self.company_name = company_name
        self.i18n = get_i18n()
        self.logo_file = None
        
        self.setup_ui()
        self.load_existing_logo()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle(self.i18n.t("logo_editor_title"))
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        # Instructions
        info_label = QLabel(self.i18n.t("logo_text"))
        layout.addWidget(info_label)
        
        # Logo text editor
        self.logo_editor = QTextEdit()
        self.logo_editor.setFont(QFont("Courier", 10))
        self.logo_editor.setPlaceholderText("Enter ASCII art logo here...")
        self.logo_editor.textChanged.connect(self.update_preview)
        layout.addWidget(self.logo_editor)
        
        # Preview label
        preview_label = QLabel(self.i18n.t("logo_preview"))
        layout.addWidget(preview_label)
        
        # Logo preview
        self.logo_preview = QTextEdit()
        self.logo_preview.setFont(QFont("Courier", 10))
        self.logo_preview.setReadOnly(True)
        self.logo_preview.setMaximumHeight(200)
        layout.addWidget(self.logo_preview)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        load_btn = QPushButton(self.i18n.t("load_logo"))
        load_btn.clicked.connect(self.load_logo)
        button_layout.addWidget(load_btn)
        
        save_btn = QPushButton(self.i18n.t("save_logo"))
        save_btn.clicked.connect(self.save_logo)
        button_layout.addWidget(save_btn)
        
        clear_btn = QPushButton(self.i18n.t("clear_logo"))
        clear_btn.clicked.connect(self.clear_logo)
        button_layout.addWidget(clear_btn)
        
        close_btn = QPushButton(self.i18n.t("cancel"))
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_existing_logo(self):
        """Load existing logo for the company if it exists."""
        # Generate logo filename from company name
        safe_name = "".join(c if c.isalnum() else "_" for c in self.company_name.lower())
        self.logo_file = f"{safe_name}.txt"
        
        logo_path = os.path.join(LOGOS_DIR, self.logo_file)
        if os.path.exists(logo_path):
            try:
                with open(logo_path, 'r', encoding='utf-8') as f:
                    self.logo_editor.setPlainText(f.read())
            except Exception as e:
                logger.error(f"Error loading logo: {e}")
    
    def update_preview(self):
        """Update preview with current logo text."""
        self.logo_preview.setPlainText(self.logo_editor.toPlainText())
    
    def load_logo(self):
        """Load logo from file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Load Logo",
            "templates/logos",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    self.logo_editor.setPlainText(f.read())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load logo: {e}")
    
    def save_logo(self):
        """Save logo to file."""
        logo_text = self.logo_editor.toPlainText()
        
        if not logo_text.strip():
            QMessageBox.warning(self, "Warning", "Logo is empty")
            return
        
        # Ensure logos directory exists
        os.makedirs(LOGOS_DIR, exist_ok=True)
        
        # Save to company-specific file
        logo_path = os.path.join(LOGOS_DIR, self.logo_file)
        
        try:
            with open(logo_path, 'w', encoding='utf-8') as f:
                f.write(logo_text)
            
            QMessageBox.information(
                self,
                self.i18n.t("logo_saved"),
                f"Logo saved to {logo_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save logo: {e}")
    
    def clear_logo(self):
        """Clear logo editor."""
        self.logo_editor.clear()
    
    def get_logo_file(self) -> str:
        """Get the logo filename."""
        return self.logo_file
