"""
ASCII Logo Editor for receipt logos
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QFileDialog, QLabel, QMessageBox,
                             QListWidget, QSplitter, QGroupBox, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LogoEditor(QDialog):
    """ASCII Logo Editor dialog"""
    
    def __init__(self, parent=None, translator=None, max_width=48, max_height=20):
        super().__init__(parent)
        self.translator = translator
        self.current_logo = ""
        self.max_width = max_width
        self.max_height = max_height
        self.logos_dir = Path('templates/logos')
        self.logos_dir.mkdir(parents=True, exist_ok=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle(self.tr('logo_editor'))
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Info label
        info = QLabel(self.tr('edit_logo_info') + f"\nMax: {self.max_width} chars wide × {self.max_height} lines high")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Splitter for logo library and editor
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Logo library
        library_widget = self.create_library_widget()
        splitter.addWidget(library_widget)
        
        # Right side - Editor
        editor_widget = self.create_editor_widget()
        splitter.addWidget(editor_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
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

        # Import PNG button
        self.import_png_btn = QPushButton('Import PNG')
        self.import_png_btn.clicked.connect(self.import_png_logo)
        button_layout.addWidget(self.import_png_btn)
        
        button_layout.addStretch()
        
        self.ok_btn = QPushButton('OK')
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def create_library_widget(self):
        """Create the logo library widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(self.tr('logo_library'))
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # Logo list
        self.logo_list = QListWidget()
        self.logo_list.itemClicked.connect(self.load_from_library)
        
        # Load available logos
        self.populate_logo_library()
        
        layout.addWidget(self.logo_list)
        
        widget.setLayout(layout)
        return widget
        
    def create_editor_widget(self):
        """Create the editor widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Text editor for ASCII art
        self.logo_text = QTextEdit()
        self.logo_text.setPlaceholderText(f"Enter your ASCII logo here...\nMax width: {self.max_width} characters\nMax height: {self.max_height} lines")
        
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
        
        widget.setLayout(layout)
        return widget
        
    def populate_logo_library(self):
        """Populate the logo library list"""
        self.logo_list.clear()
        
        # Add all logos from the logos directory
        if self.logos_dir.exists():
            for logo_file in sorted(self.logos_dir.glob('*.txt')):
                self.logo_list.addItem(logo_file.stem)
                
    def load_from_library(self, item):
        """Load a logo from the library"""
        logo_name = item.text()
        logo_path = self.logos_dir / f"{logo_name}.txt"
        
        if logo_path.exists():
            try:
                with open(logo_path, 'r', encoding='utf-8') as f:
                    logo_text = f.read()
                self.logo_text.setPlainText(logo_text)
                logger.info(f"Loaded logo from library: {logo_name}")
            except Exception as e:
                logger.error(f"Error loading logo from library: {e}")
                QMessageBox.warning(self, self.tr('error'), f"Failed to load logo: {e}")
        
    def tr(self, key):
        """Translate a key"""
        if self.translator:
            translated = self.translator.translate(key)
            if translated != key:
                return translated
                
        # Fallback translations
        fallbacks = {
            'logo_editor': 'ASCII Logo Editor',
            'logo_library': 'Logo Library',
            'edit_logo_info': 'Create an ASCII logo for receipts.',
            'clear': 'Clear',
            'load_logo': 'Load File',
            'save_logo': 'Save File',
            'error': 'Error',
            'success': 'Success'
        }
        return fallbacks.get(key, key)
        
    def update_stats(self):
        """Update character statistics"""
        text = self.logo_text.toPlainText()
        lines = text.split('\n')
        line_count = len(lines)
        max_length = max(len(line) for line in lines) if lines else 0
        
        self.char_label.setText(f"Lines: {line_count}/{self.max_height} | Max line length: {max_length}/{self.max_width}")
        
        # Warn if line is too long or too many lines
        if max_length > self.max_width or line_count > self.max_height:
            self.char_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.char_label.setStyleSheet("color: green;")
            
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

    def import_png_logo(self):
        """Import a PNG file into templates/logos directory."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Import PNG Logo',
            str(self.logos_dir),
            'PNG Images (*.png)'
        )
        if not file_path:
            return
        try:
            src = Path(file_path)
            dest = self.logos_dir / src.name
            dest.write_bytes(src.read_bytes())
            QMessageBox.information(self, self.tr('success'), f"Imported to {dest}")
            # Refresh library (only shows .txt, but we still import PNG for templates)
        except Exception as e:
            logger.error(f"Error importing PNG: {e}")
            QMessageBox.warning(self, self.tr('error'), f"Failed to import PNG: {e}")
