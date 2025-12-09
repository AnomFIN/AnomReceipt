"""
Settings dialog for receipt configuration
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QSpinBox, QPushButton, QGroupBox, QTabWidget,
                             QWidget, QCheckBox)
from PyQt5.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

# Receipt printer constants
MIN_RECEIPT_WIDTH = 32
MAX_RECEIPT_WIDTH = 80
DEFAULT_RECEIPT_WIDTH = 48

MIN_RECEIPT_LENGTH = 50
MAX_RECEIPT_LENGTH = 200
DEFAULT_RECEIPT_LENGTH = 80

MIN_LOGO_WIDTH = 20
MAX_LOGO_WIDTH = 80
DEFAULT_LOGO_WIDTH = 48

MIN_LOGO_HEIGHT = 5
MAX_LOGO_HEIGHT = 30
DEFAULT_LOGO_HEIGHT = 20


class SettingsDialog(QDialog):
    """Dialog for application settings"""
    
    def __init__(self, parent=None, translator=None, current_settings=None):
        super().__init__(parent)
        self.translator = translator
        self.settings = current_settings or {
            'receipt_width': DEFAULT_RECEIPT_WIDTH,
            'receipt_length': DEFAULT_RECEIPT_LENGTH,
            'logo_max_width': DEFAULT_LOGO_WIDTH,
            'logo_max_height': DEFAULT_LOGO_HEIGHT,
            'feed_lines': 3,
            'cut_paper': True,
            'bold_header': True,
            'double_width_total': False
        }
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle(self.tr('settings'))
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Tab widget for different settings categories
        tabs = QTabWidget()
        
        # Receipt settings tab
        receipt_tab = self.create_receipt_tab()
        tabs.addTab(receipt_tab, self.tr('receipt_settings'))
        
        # Logo settings tab
        logo_tab = self.create_logo_tab()
        tabs.addTab(logo_tab, self.tr('logo_settings'))
        
        # Printing settings tab
        print_tab = self.create_print_tab()
        tabs.addTab(print_tab, self.tr('print_settings'))
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton(self.tr('reset_defaults'))
        self.reset_btn.clicked.connect(self.reset_defaults)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.ok_btn = QPushButton('OK')
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def create_receipt_tab(self):
        """Create receipt settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Receipt dimensions group
        dimensions_group = QGroupBox(self.tr('receipt_dimensions'))
        dimensions_layout = QFormLayout()
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(MIN_RECEIPT_WIDTH, MAX_RECEIPT_WIDTH)
        self.width_spin.setSuffix(' ' + self.tr('characters'))
        dimensions_layout.addRow(self.tr('receipt_width') + ':', self.width_spin)
        
        width_info = QLabel(self.tr('width_info'))
        width_info.setWordWrap(True)
        width_info.setStyleSheet("color: gray; font-size: 9pt;")
        dimensions_layout.addRow('', width_info)
        
        self.length_spin = QSpinBox()
        self.length_spin.setRange(MIN_RECEIPT_LENGTH, MAX_RECEIPT_LENGTH)
        self.length_spin.setSuffix(' ' + self.tr('lines'))
        dimensions_layout.addRow(self.tr('receipt_length') + ':', self.length_spin)
        
        length_info = QLabel(self.tr('length_info'))
        length_info.setWordWrap(True)
        length_info.setStyleSheet("color: gray; font-size: 9pt;")
        dimensions_layout.addRow('', length_info)
        
        dimensions_group.setLayout(dimensions_layout)
        layout.addWidget(dimensions_group)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
        
    def create_logo_tab(self):
        """Create logo settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Logo dimensions group
        logo_group = QGroupBox(self.tr('logo_dimensions'))
        logo_layout = QFormLayout()
        
        self.logo_width_spin = QSpinBox()
        self.logo_width_spin.setRange(MIN_LOGO_WIDTH, MAX_LOGO_WIDTH)
        self.logo_width_spin.setSuffix(' ' + self.tr('characters'))
        logo_layout.addRow(self.tr('logo_max_width') + ':', self.logo_width_spin)
        
        logo_width_info = QLabel(self.tr('logo_width_info'))
        logo_width_info.setWordWrap(True)
        logo_width_info.setStyleSheet("color: gray; font-size: 9pt;")
        logo_layout.addRow('', logo_width_info)
        
        self.logo_height_spin = QSpinBox()
        self.logo_height_spin.setRange(MIN_LOGO_HEIGHT, MAX_LOGO_HEIGHT)
        self.logo_height_spin.setSuffix(' ' + self.tr('lines'))
        logo_layout.addRow(self.tr('logo_max_height') + ':', self.logo_height_spin)
        
        logo_height_info = QLabel(self.tr('logo_height_info'))
        logo_height_info.setWordWrap(True)
        logo_height_info.setStyleSheet("color: gray; font-size: 9pt;")
        logo_layout.addRow('', logo_height_info)
        
        logo_group.setLayout(logo_layout)
        layout.addWidget(logo_group)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
        
    def create_print_tab(self):
        """Create printing settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Paper handling group
        paper_group = QGroupBox(self.tr('paper_handling'))
        paper_layout = QFormLayout()
        
        self.feed_lines_spin = QSpinBox()
        self.feed_lines_spin.setRange(0, 10)
        self.feed_lines_spin.setSuffix(' ' + self.tr('lines'))
        paper_layout.addRow(self.tr('feed_lines') + ':', self.feed_lines_spin)
        
        self.cut_paper_check = QCheckBox(self.tr('cut_paper_auto'))
        paper_layout.addRow('', self.cut_paper_check)
        
        paper_group.setLayout(paper_layout)
        layout.addWidget(paper_group)
        
        # Formatting group
        format_group = QGroupBox(self.tr('text_formatting'))
        format_layout = QFormLayout()
        
        self.bold_header_check = QCheckBox(self.tr('bold_header'))
        format_layout.addRow('', self.bold_header_check)
        
        self.double_width_total_check = QCheckBox(self.tr('double_width_total'))
        format_layout.addRow('', self.double_width_total_check)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
        
    def tr(self, key):
        """Translate a key"""
        if self.translator:
            translated = self.translator.translate(key)
            if translated != key:
                return translated
                
        # Fallback translations for settings-specific keys
        fallbacks = {
            'settings': 'Settings',
            'receipt_settings': 'Receipt Settings',
            'logo_settings': 'Logo Settings',
            'print_settings': 'Print Settings',
            'receipt_dimensions': 'Receipt Dimensions',
            'logo_dimensions': 'Logo Dimensions',
            'paper_handling': 'Paper Handling',
            'text_formatting': 'Text Formatting',
            'receipt_width': 'Receipt Width',
            'receipt_length': 'Maximum Receipt Length',
            'logo_max_width': 'Maximum Logo Width',
            'logo_max_height': 'Maximum Logo Height',
            'feed_lines': 'Feed Lines After Print',
            'cut_paper_auto': 'Cut paper automatically',
            'bold_header': 'Bold header text',
            'double_width_total': 'Double width for total',
            'reset_defaults': 'Reset to Defaults',
            'characters': 'chars',
            'lines': 'lines',
            'width_info': 'Standard width is 48 characters. Adjust for your printer model.',
            'length_info': 'Maximum lines per receipt. Adjust based on paper size.',
            'logo_width_info': 'Maximum width for ASCII logos. Should not exceed receipt width.',
            'logo_height_info': 'Maximum height for ASCII logos to prevent excessive paper use.',
        }
        return fallbacks.get(key, key)
        
    def load_settings(self):
        """Load current settings into the UI"""
        self.width_spin.setValue(self.settings.get('receipt_width', 48))
        self.length_spin.setValue(self.settings.get('receipt_length', 80))
        self.logo_width_spin.setValue(self.settings.get('logo_max_width', 48))
        self.logo_height_spin.setValue(self.settings.get('logo_max_height', 20))
        self.feed_lines_spin.setValue(self.settings.get('feed_lines', 3))
        self.cut_paper_check.setChecked(self.settings.get('cut_paper', True))
        self.bold_header_check.setChecked(self.settings.get('bold_header', True))
        self.double_width_total_check.setChecked(self.settings.get('double_width_total', False))
        
    def get_settings(self):
        """Get the current settings from the UI"""
        return {
            'receipt_width': self.width_spin.value(),
            'receipt_length': self.length_spin.value(),
            'logo_max_width': self.logo_width_spin.value(),
            'logo_max_height': self.logo_height_spin.value(),
            'feed_lines': self.feed_lines_spin.value(),
            'cut_paper': self.cut_paper_check.isChecked(),
            'bold_header': self.bold_header_check.isChecked(),
            'double_width_total': self.double_width_total_check.isChecked()
        }
        
    def reset_defaults(self):
        """Reset settings to defaults"""
        self.settings = {
            'receipt_width': DEFAULT_RECEIPT_WIDTH,
            'receipt_length': DEFAULT_RECEIPT_LENGTH,
            'logo_max_width': DEFAULT_LOGO_WIDTH,
            'logo_max_height': DEFAULT_LOGO_HEIGHT,
            'feed_lines': 3,
            'cut_paper': True,
            'bold_header': True,
            'double_width_total': False
        }
        self.load_settings()
