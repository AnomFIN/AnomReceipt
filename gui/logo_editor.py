"""
ASCII logo editor dialog.
"""
import os
import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QFileDialog, QMessageBox, QToolButton, QSpinBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from i18n import get_i18n
from templates.logo_converter import image_to_ascii, LogoConversionError

logger = logging.getLogger(__name__)

# Ship intelligence, not excuses.

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
        self.logo_width = 42
        self._bold_enabled = False

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

        formatting_bar = QHBoxLayout()

        self.bold_btn = QToolButton()
        self.bold_btn.setText(self.i18n.t("bold"))
        self.bold_btn.setCheckable(True)
        self.bold_btn.clicked.connect(self.toggle_bold)
        formatting_bar.addWidget(self.bold_btn)

        size_label = QLabel(self.i18n.t("font_size"))
        formatting_bar.addWidget(size_label)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 32)
        self.font_size_spin.setValue(10)
        self.font_size_spin.valueChanged.connect(self.change_font_size)
        formatting_bar.addWidget(self.font_size_spin)

        formatting_bar.addStretch()
        layout.addLayout(formatting_bar)

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

        import_btn = QPushButton(self.i18n.t("import_logo_image"))
        import_btn.clicked.connect(self.import_image_logo)
        button_layout.addWidget(import_btn)

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

    def toggle_bold(self):
        """Toggle bold font for editor and preview."""
        self._bold_enabled = self.bold_btn.isChecked()
        weight = QFont.Bold if self._bold_enabled else QFont.Normal
        for widget in (self.logo_editor, self.logo_preview):
            font = widget.font()
            font.setWeight(weight)
            widget.setFont(font)

    def change_font_size(self, size: int):
        """Adjust font size for both editor and preview."""
        if size <= 0:
            return
        for widget in (self.logo_editor, self.logo_preview):
            font = widget.font()
            font.setPointSize(size)
            widget.setFont(font)
    
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

    def import_image_logo(self):
        """Import an image logo and convert to ASCII."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            self.i18n.t("import_logo_image"),
            "templates/logos",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)",
        )

        if not file_name:
            return

        try:
            ascii_logo = image_to_ascii(file_name, width=self.logo_width)
            self.logo_editor.setPlainText(ascii_logo)
            self.update_preview()
        except LogoConversionError as exc:
            logger.error("Logo import failed: %s", exc)
            QMessageBox.warning(self, self.i18n.t("import_logo_image"), str(exc))
    
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
