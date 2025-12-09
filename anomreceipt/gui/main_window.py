"""
Main window for AnomReceipt application
Provides reactive Qt GUI for receipt printing
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QTextEdit, QGroupBox,
                             QMessageBox, QDialog, QFormLayout, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase
import logging

from ..printer import ESCPOSPrinter
from ..templates import TemplateManager
from ..locale import Translator
from .logo_editor import LogoEditor

logger = logging.getLogger(__name__)


class NetworkDialog(QDialog):
    """Dialog for network printer connection"""
    
    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator
        self.host = None
        self.port = 9100
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(self.tr('connect_network'))
        
        layout = QFormLayout()
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("192.168.1.100")
        layout.addRow(self.tr('host') + ':', self.host_input)
        
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(9100)
        layout.addRow(self.tr('port') + ':', self.port_input)
        
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton('OK')
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
        
    def tr(self, key):
        """Translate a key"""
        if self.translator:
            return self.translator.translate(key)
        return key
        
    def get_values(self):
        """Get the host and port values"""
        return self.host_input.text(), self.port_input.value()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.translator = Translator('EN')
        self.printer = ESCPOSPrinter()
        self.template_manager = TemplateManager()
        self.current_template = None
        self.items = []
        
        self.setup_ui()
        self.update_preview()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle(self.translator.translate('app_title'))
        self.setMinimumSize(1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        
        # Left panel - Controls
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Preview
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
        central_widget.setLayout(main_layout)
        
    def create_left_panel(self):
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Language toggle
        lang_group = QGroupBox(self.translator.translate('settings'))
        lang_layout = QHBoxLayout()
        
        lang_label = QLabel(self.translator.translate('language') + ':')
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['EN', 'FI'])
        self.lang_combo.currentTextChanged.connect(self.change_ui_language)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        
        receipt_lang_label = QLabel(self.translator.translate('receipt_language') + ':')
        self.receipt_lang_combo = QComboBox()
        self.receipt_lang_combo.addItems(['EN', 'FI'])
        self.receipt_lang_combo.currentTextChanged.connect(self.update_preview)
        lang_layout.addWidget(receipt_lang_label)
        lang_layout.addWidget(self.receipt_lang_combo)
        
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        
        # Printer connection
        printer_group = QGroupBox(self.translator.translate('printer_status'))
        printer_layout = QVBoxLayout()
        
        self.status_label = QLabel(self.translator.translate('not_connected'))
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        printer_layout.addWidget(self.status_label)
        
        btn_layout = QHBoxLayout()
        self.usb_btn = QPushButton(self.translator.translate('connect_usb'))
        self.usb_btn.clicked.connect(self.connect_usb)
        btn_layout.addWidget(self.usb_btn)
        
        self.network_btn = QPushButton(self.translator.translate('connect_network'))
        self.network_btn.clicked.connect(self.connect_network)
        btn_layout.addWidget(self.network_btn)
        
        self.disconnect_btn = QPushButton(self.translator.translate('disconnect'))
        self.disconnect_btn.clicked.connect(self.disconnect_printer)
        self.disconnect_btn.setEnabled(False)
        btn_layout.addWidget(self.disconnect_btn)
        
        printer_layout.addLayout(btn_layout)
        printer_group.setLayout(printer_layout)
        layout.addWidget(printer_group)
        
        # Company selection
        company_group = QGroupBox(self.translator.translate('company'))
        company_layout = QVBoxLayout()
        
        self.company_combo = QComboBox()
        self.load_companies()
        self.company_combo.currentTextChanged.connect(self.change_company)
        company_layout.addWidget(self.company_combo)
        
        self.logo_btn = QPushButton(self.translator.translate('edit_logo'))
        self.logo_btn.clicked.connect(self.open_logo_editor)
        company_layout.addWidget(self.logo_btn)
        
        company_group.setLayout(company_layout)
        layout.addWidget(company_group)
        
        # Payment method
        payment_group = QGroupBox(self.translator.translate('payment_method'))
        payment_layout = QVBoxLayout()
        
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(['cash', 'card', 'mobilepay', 'bank'])
        self.payment_combo.currentTextChanged.connect(self.update_preview)
        payment_layout.addWidget(self.payment_combo)
        
        payment_group.setLayout(payment_layout)
        layout.addWidget(payment_group)
        
        # Items table
        items_group = QGroupBox(self.translator.translate('items'))
        items_layout = QVBoxLayout()
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(3)
        self.items_table.setHorizontalHeaderLabels([
            self.translator.translate('item_name'),
            self.translator.translate('quantity'),
            self.translator.translate('price')
        ])
        self.items_table.horizontalHeader().setStretchLastSection(True)
        items_layout.addWidget(self.items_table)
        
        items_btn_layout = QHBoxLayout()
        self.add_item_btn = QPushButton(self.translator.translate('add_item'))
        self.add_item_btn.clicked.connect(self.add_item)
        items_btn_layout.addWidget(self.add_item_btn)
        
        self.remove_item_btn = QPushButton(self.translator.translate('remove_item'))
        self.remove_item_btn.clicked.connect(self.remove_item)
        items_btn_layout.addWidget(self.remove_item_btn)
        
        items_layout.addLayout(items_btn_layout)
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Print button
        self.print_btn = QPushButton(self.translator.translate('print'))
        self.print_btn.clicked.connect(self.print_receipt)
        self.print_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; padding: 10px;")
        layout.addWidget(self.print_btn)
        
        panel.setLayout(layout)
        return panel
        
    def create_right_panel(self):
        """Create the right preview panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Preview label
        preview_label = QLabel(self.translator.translate('preview'))
        preview_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(preview_label)
        
        # Preview text area
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        
        # Use monospace font for proper receipt preview
        font = QFont("Courier New", 10)
        if not font.exactMatch():
            font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.preview_text.setFont(font)
        self.preview_text.setLineWrapMode(QTextEdit.NoWrap)
        
        layout.addWidget(self.preview_text)
        
        panel.setLayout(layout)
        return panel
        
    def load_companies(self):
        """Load available company templates"""
        templates = self.template_manager.list_templates()
        self.company_combo.clear()
        
        if templates:
            self.company_combo.addItems(templates)
            self.current_template = self.template_manager.get_template(templates[0])
        else:
            self.company_combo.addItem(self.translator.translate('select_company'))
            
    def change_company(self, company_name):
        """Change the current company template"""
        self.current_template = self.template_manager.get_template(company_name)
        self.update_preview()
        
    def change_ui_language(self, language):
        """Change the UI language"""
        self.translator.set_language(language)
        self.update_ui_texts()
        self.update_preview()
        
    def update_ui_texts(self):
        """Update all UI texts with current language"""
        self.setWindowTitle(self.translator.translate('app_title'))
        # Update button texts and labels
        # This would be more complete in a real application
        
    def open_logo_editor(self):
        """Open the logo editor dialog"""
        editor = LogoEditor(self, self.translator)
        
        # Load current logo if available
        if self.current_template and self.current_template.logo:
            editor.set_logo(self.current_template.logo)
            
        if editor.exec_() == QDialog.Accepted:
            logo = editor.get_logo()
            if self.current_template:
                self.current_template.logo = logo
                self.update_preview()
                
    def add_item(self):
        """Add a new item row"""
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        # Add default values
        self.items_table.setItem(row, 0, QTableWidgetItem(""))
        self.items_table.setItem(row, 1, QTableWidgetItem("1"))
        self.items_table.setItem(row, 2, QTableWidgetItem("0.00"))
        
        # Connect to update preview when cell changes
        self.items_table.cellChanged.connect(self.update_preview)
        
    def remove_item(self):
        """Remove selected item row"""
        current_row = self.items_table.currentRow()
        if current_row >= 0:
            self.items_table.removeRow(current_row)
            self.update_preview()
            
    def get_items_from_table(self):
        """Get items from the table"""
        items = []
        for row in range(self.items_table.rowCount()):
            name_item = self.items_table.item(row, 0)
            qty_item = self.items_table.item(row, 1)
            price_item = self.items_table.item(row, 2)
            
            if name_item and price_item:
                name = name_item.text()
                qty = qty_item.text() if qty_item else "1"
                price = price_item.text()
                
                if name and price:
                    items.append({
                        'name': name,
                        'qty': qty,
                        'price': f"{price}€"
                    })
        return items
        
    def update_preview(self):
        """Update the receipt preview"""
        if not self.current_template:
            self.preview_text.setPlainText("Please select a company template")
            return
            
        items = self.get_items_from_table()
        if not items:
            items = [{'name': 'Sample Item', 'qty': '1', 'price': '10.00€'}]
            
        payment_method = self.payment_combo.currentText()
        receipt_language = self.receipt_lang_combo.currentText()
        
        receipt_data = self.current_template.generate_receipt(
            items=items,
            payment_method=payment_method,
            language=receipt_language
        )
        
        # Format preview text
        preview = []
        
        # Logo
        if receipt_data.get('logo'):
            preview.append(receipt_data['logo'])
            preview.append('')
            
        # Header
        if receipt_data.get('header'):
            for line in receipt_data['header']:
                preview.append(line)
                
        # Items
        preview.append('-' * 48)
        if receipt_data.get('items'):
            for item in receipt_data['items']:
                name = item.get('name', '')
                price = item.get('price', '')
                qty = item.get('qty', '')
                
                if qty:
                    line = f"{qty}x {name}"
                else:
                    line = name
                    
                spaces = 48 - len(line) - len(price)
                if spaces > 0:
                    line += ' ' * spaces
                line += price
                
                preview.append(line)
                
        preview.append('-' * 48)
        
        # Footer
        if receipt_data.get('footer'):
            for line in receipt_data['footer']:
                preview.append(line)
                
        self.preview_text.setPlainText('\n'.join(preview))
        
    def connect_usb(self):
        """Connect to USB printer"""
        if self.printer.connect_usb():
            self.status_label.setText(f"{self.translator.translate('connected')} (USB)")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.disconnect_btn.setEnabled(True)
            self.usb_btn.setEnabled(False)
            self.network_btn.setEnabled(False)
            QMessageBox.information(self, self.translator.translate('success'),
                                  self.translator.translate('connect_success'))
        else:
            QMessageBox.warning(self, self.translator.translate('error'),
                              self.translator.translate('connect_error'))
                              
    def connect_network(self):
        """Connect to network printer"""
        dialog = NetworkDialog(self, self.translator)
        if dialog.exec_() == QDialog.Accepted:
            host, port = dialog.get_values()
            if host and self.printer.connect_network(host, port):
                self.status_label.setText(f"{self.translator.translate('connected')} ({host}:{port})")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                self.disconnect_btn.setEnabled(True)
                self.usb_btn.setEnabled(False)
                self.network_btn.setEnabled(False)
                QMessageBox.information(self, self.translator.translate('success'),
                                      self.translator.translate('connect_success'))
            else:
                QMessageBox.warning(self, self.translator.translate('error'),
                                  self.translator.translate('connect_error'))
                                  
    def disconnect_printer(self):
        """Disconnect from printer"""
        self.printer.disconnect()
        self.status_label.setText(self.translator.translate('not_connected'))
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.disconnect_btn.setEnabled(False)
        self.usb_btn.setEnabled(True)
        self.network_btn.setEnabled(True)
        
    def print_receipt(self):
        """Print the receipt"""
        if not self.printer.is_connected():
            QMessageBox.warning(self, self.translator.translate('error'),
                              "Please connect to a printer first")
            return
            
        if not self.current_template:
            QMessageBox.warning(self, self.translator.translate('error'),
                              "Please select a company template")
            return
            
        items = self.get_items_from_table()
        if not items:
            QMessageBox.warning(self, self.translator.translate('error'),
                              "Please add at least one item")
            return
            
        payment_method = self.payment_combo.currentText()
        receipt_language = self.receipt_lang_combo.currentText()
        
        receipt_data = self.current_template.generate_receipt(
            items=items,
            payment_method=payment_method,
            language=receipt_language
        )
        
        if self.printer.print_receipt(receipt_data):
            QMessageBox.information(self, self.translator.translate('success'),
                                  self.translator.translate('print_success'))
        else:
            QMessageBox.warning(self, self.translator.translate('error'),
                              self.translator.translate('print_error'))
