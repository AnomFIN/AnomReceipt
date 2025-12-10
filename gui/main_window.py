"""
Main window for the receipt printing application.
"""
from decimal import Decimal
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit,
    QTableWidget, QTableWidgetItem, QGroupBox, QStatusBar,
    QMessageBox, QDateTimeEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal
from models import ReceiptData, ReceiptItem
from templates.companies import get_company, get_company_names
from templates.template_engine import ReceiptTemplate
from config.settings import Settings
from i18n import get_i18n
from printer.escpos_printer import EpsonTM70Printer, DummyPrinter
from gui.settings_dialog import SettingsDialog
from gui.logo_editor import LogoEditorDialog


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        # Initialize components
        self.settings = Settings()
        self.i18n = get_i18n()
        self.i18n.set_language(self.settings.get_default_language())
        self.template_engine = ReceiptTemplate()
        
        # Receipt data
        self.current_receipt = None
        
        # Flag to prevent updates during initialization
        self._initializing = True
        
        self.setup_ui()
        self.load_default_company()
        
        # Enable updates
        self._initializing = False
        
        # Update preview initially
        self.update_preview()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle(self.i18n.t("app_title"))
        
        # Set window size from settings
        width = self.settings.get("ui.window_width", 1200)
        height = self.settings.get("ui.window_height", 800)
        self.resize(width, height)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel - Input fields
        left_panel = QVBoxLayout()
        left_panel.addWidget(self.create_company_section())
        left_panel.addWidget(self.create_payment_section())
        left_panel.addWidget(self.create_receipt_info_section())
        left_panel.addWidget(self.create_items_section())
        left_panel.addWidget(self.create_totals_section())
        left_panel.addStretch()
        
        # Right panel - Preview and buttons
        right_panel = QVBoxLayout()
        right_panel.addWidget(self.create_preview_section())
        right_panel.addWidget(self.create_button_section())
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 1)
        
        central_widget.setLayout(main_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_company_section(self) -> QGroupBox:
        """Create company selection section."""
        group = QGroupBox(self.i18n.t("company"))
        layout = QFormLayout()
        
        # Company dropdown
        self.company_combo = QComboBox()
        self.company_combo.addItems(get_company_names())
        self.company_combo.currentTextChanged.connect(self.on_company_changed)
        layout.addRow(self.i18n.t("company"), self.company_combo)
        
        group.setLayout(layout)
        return group
    
    def create_payment_section(self) -> QGroupBox:
        """Create payment and language section."""
        group = QGroupBox(self.i18n.t("payment_method"))
        layout = QFormLayout()
        
        # Payment method dropdown
        self.payment_combo = QComboBox()
        self.update_payment_methods()
        self.payment_combo.currentTextChanged.connect(self.update_preview)
        layout.addRow(self.i18n.t("payment_method"), self.payment_combo)
        
        # Language toggle
        self.language_combo = QComboBox()
        self.language_combo.addItem("Suomi", "FI")
        self.language_combo.addItem("English", "EN")
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        layout.addRow(self.i18n.t("language"), self.language_combo)
        
        group.setLayout(layout)
        return group
    
    def create_receipt_info_section(self) -> QGroupBox:
        """Create receipt information section."""
        group = QGroupBox("Receipt Info")
        layout = QFormLayout()
        
        # Customer name
        self.customer_name = QLineEdit()
        self.customer_name.textChanged.connect(self.update_preview)
        layout.addRow(self.i18n.t("customer_name"), self.customer_name)
        
        # Reference number
        self.reference_number = QLineEdit()
        self.reference_number.textChanged.connect(self.update_preview)
        layout.addRow(self.i18n.t("reference"), self.reference_number)
        
        # Invoice number
        self.invoice_number = QLineEdit()
        self.invoice_number.textChanged.connect(self.update_preview)
        layout.addRow(self.i18n.t("invoice_number"), self.invoice_number)
        
        # Date/time
        self.date_time_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_time_edit.setCalendarPopup(True)
        self.date_time_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        self.date_time_edit.dateTimeChanged.connect(self.update_preview)
        layout.addRow(self.i18n.t("date_time"), self.date_time_edit)
        
        group.setLayout(layout)
        return group
    
    def create_items_section(self) -> QGroupBox:
        """Create items table section."""
        group = QGroupBox("Items")
        layout = QVBoxLayout()
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            self.i18n.t("product"),
            self.i18n.t("quantity"),
            self.i18n.t("unit_price"),
            self.i18n.t("vat_rate"),
            self.i18n.t("total")
        ])
        self.items_table.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.items_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton(self.i18n.t("add_item"))
        add_btn.clicked.connect(self.add_item_row)
        button_layout.addWidget(add_btn)
        
        remove_btn = QPushButton(self.i18n.t("remove_item"))
        remove_btn.clicked.connect(self.remove_item_row)
        button_layout.addWidget(remove_btn)
        
        layout.addLayout(button_layout)
        
        group.setLayout(layout)
        
        # Add initial row
        self.add_item_row()
        
        return group
    
    def create_totals_section(self) -> QGroupBox:
        """Create totals display section."""
        group = QGroupBox(self.i18n.t("total"))
        layout = QFormLayout()
        
        # Subtotal
        self.subtotal_label = QLabel("0.00 EUR")
        self.subtotal_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addRow(self.i18n.t("subtotal"), self.subtotal_label)
        
        # Total VAT
        self.total_vat_label = QLabel("0.00 EUR")
        self.total_vat_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addRow(self.i18n.t("total_vat"), self.total_vat_label)
        
        # Grand total
        self.grand_total_label = QLabel("0.00 EUR")
        self.grand_total_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addRow(self.i18n.t("grand_total"), self.grand_total_label)
        
        group.setLayout(layout)
        return group
    
    def create_preview_section(self) -> QGroupBox:
        """Create receipt preview section."""
        group = QGroupBox(self.i18n.t("preview"))
        layout = QVBoxLayout()
        
        # Preview text area
        self.preview_text = QTextEdit()
        self.preview_text.setFont(QFont("Courier", 9))
        self.preview_text.setReadOnly(True)
        layout.addWidget(self.preview_text)
        
        group.setLayout(layout)
        return group
    
    def create_button_section(self) -> QWidget:
        """Create button toolbar section."""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Print button
        print_btn = QPushButton(self.i18n.t("print"))
        print_btn.clicked.connect(self.print_receipt)
        print_btn.setMinimumHeight(40)
        layout.addWidget(print_btn)
        
        # Test print button
        test_btn = QPushButton(self.i18n.t("test_print"))
        test_btn.clicked.connect(self.test_print)
        layout.addWidget(test_btn)
        
        # Logo editor button
        logo_btn = QPushButton(self.i18n.t("logo_editor"))
        logo_btn.clicked.connect(self.open_logo_editor)
        layout.addWidget(logo_btn)
        
        # Settings button
        settings_btn = QPushButton(self.i18n.t("settings"))
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)
        
        widget.setLayout(layout)
        return widget
    
    def load_default_company(self):
        """Load default company from settings."""
        default_company = self.settings.get_default_company()
        if default_company:
            index = self.company_combo.findText(default_company)
            if index >= 0:
                self.company_combo.setCurrentIndex(index)
        
        # Set default language
        default_lang = self.settings.get_default_language()
        index = self.language_combo.findData(default_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
    
    def update_payment_methods(self):
        """Update payment method dropdown based on language."""
        current = self.payment_combo.currentText()
        self.payment_combo.clear()
        
        methods = [
            self.i18n.t("cash"),
            self.i18n.t("card"),
            self.i18n.t("mobilepay"),
            self.i18n.t("bank_transfer"),
            self.i18n.t("other")
        ]
        
        self.payment_combo.addItems(methods)
        
        # Restore selection if possible
        index = self.payment_combo.findText(current)
        if index >= 0:
            self.payment_combo.setCurrentIndex(index)
    
    def on_company_changed(self, company_name: str):
        """Handle company selection change."""
        self.update_preview()
    
    def on_language_changed(self, index: int):
        """Handle language change."""
        language = self.language_combo.currentData()
        self.i18n.set_language(language)
        
        # Update UI labels
        self.setWindowTitle(self.i18n.t("app_title"))
        self.update_payment_methods()
        
        # Update preview
        self.update_preview()
    
    def add_item_row(self):
        """Add a new item row to the table."""
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        # Set default values
        self.items_table.setItem(row, 0, QTableWidgetItem("Product"))
        self.items_table.setItem(row, 1, QTableWidgetItem("1"))
        self.items_table.setItem(row, 2, QTableWidgetItem("0.00"))
        self.items_table.setItem(row, 3, QTableWidgetItem("24"))
        
        # Total column (read-only)
        total_item = QTableWidgetItem("0.00")
        total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
        self.items_table.setItem(row, 4, total_item)
        
        self.update_item_total(row)
    
    def remove_item_row(self):
        """Remove selected item row."""
        current_row = self.items_table.currentRow()
        if current_row >= 0:
            self.items_table.removeRow(current_row)
            self.update_preview()
    
    def on_item_changed(self, item: QTableWidgetItem):
        """Handle item cell change."""
        row = item.row()
        self.update_item_total(row)
        self.update_preview()
    
    def update_item_total(self, row: int):
        """Update total for a specific item row."""
        try:
            qty = Decimal(self.items_table.item(row, 1).text())
            price = Decimal(self.items_table.item(row, 2).text())
            vat_rate = Decimal(self.items_table.item(row, 3).text())
            
            subtotal = qty * price
            vat_amount = subtotal * (vat_rate / Decimal(100))
            total = subtotal + vat_amount
            
            self.items_table.item(row, 4).setText(f"{float(total):.2f}")
        except (ValueError, AttributeError):
            pass
    
    def get_receipt_items(self) -> list:
        """Get receipt items from table."""
        items = []
        
        for row in range(self.items_table.rowCount()):
            try:
                product = self.items_table.item(row, 0).text()
                qty = Decimal(self.items_table.item(row, 1).text())
                price = Decimal(self.items_table.item(row, 2).text())
                vat_rate = Decimal(self.items_table.item(row, 3).text())
                
                if product.strip():
                    items.append(ReceiptItem(
                        product_name=product,
                        quantity=qty,
                        unit_price=price,
                        vat_rate=vat_rate
                    ))
            except (ValueError, AttributeError):
                continue
        
        return items
    
    def update_preview(self):
        """Update receipt preview and totals."""
        # Skip if still initializing
        if hasattr(self, '_initializing') and self._initializing:
            return
        
        # Get current company
        company_name = self.company_combo.currentText()
        company = get_company(company_name)
        
        if not company:
            return
        
        # Get current language
        language = self.language_combo.currentData()
        
        # Build receipt data
        items = self.get_receipt_items()
        
        # Get date/time
        qt_datetime = self.date_time_edit.dateTime()
        dt = datetime(
            qt_datetime.date().year(),
            qt_datetime.date().month(),
            qt_datetime.date().day(),
            qt_datetime.time().hour(),
            qt_datetime.time().minute()
        )
        
        self.current_receipt = ReceiptData(
            company=company,
            items=items,
            customer_name=self.customer_name.text() or None,
            reference_number=self.reference_number.text() or None,
            invoice_number=self.invoice_number.text() or None,
            date_time=dt,
            payment_method=self.payment_combo.currentText(),
            language=language,
            currency="EUR"
        )
        
        # Update totals
        self.subtotal_label.setText(f"{float(self.current_receipt.subtotal):.2f} EUR")
        self.total_vat_label.setText(f"{float(self.current_receipt.total_vat):.2f} EUR")
        self.grand_total_label.setText(f"{float(self.current_receipt.total):.2f} EUR")
        
        # Render preview
        receipt_text = self.template_engine.render(self.current_receipt)
        self.preview_text.setPlainText(receipt_text)
    
    def print_receipt(self):
        """Print the current receipt."""
        if not self.current_receipt or not self.current_receipt.items:
            QMessageBox.warning(
                self,
                "Warning",
                self.i18n.t("no_items")
            )
            return
        
        # Get printer configuration
        printer_config = self.settings.get_printer_config()
        
        try:
            printer = EpsonTM70Printer(
                connection_type=printer_config.get("connection_type", "usb"),
                device_path=printer_config.get("device_path"),
                ip_address=printer_config.get("ip_address"),
                port=printer_config.get("port", 9100)
            )
            
            if not printer.connect():
                # Fallback to dummy printer if connection fails
                QMessageBox.warning(
                    self,
                    "Printer Connection Failed",
                    "Could not connect to printer. Using simulation mode."
                )
                printer = DummyPrinter()
                printer.connect()
            
            # Get receipt text
            receipt_text = self.template_engine.render(self.current_receipt)
            
            # Print
            if printer.print_receipt(receipt_text):
                self.status_bar.showMessage(self.i18n.t("print_success"), 3000)
            else:
                self.status_bar.showMessage(self.i18n.t("print_error"), 3000)
            
            printer.disconnect()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                self.i18n.t("print_error"),
                f"Print error: {e}"
            )
            self.status_bar.showMessage(f"Error: {e}", 5000)
    
    def test_print(self):
        """Perform a test print."""
        printer_config = self.settings.get_printer_config()
        
        try:
            printer = EpsonTM70Printer(
                connection_type=printer_config.get("connection_type", "usb"),
                device_path=printer_config.get("device_path"),
                ip_address=printer_config.get("ip_address"),
                port=printer_config.get("port", 9100)
            )
            
            if not printer.connect():
                # Fallback to dummy printer
                printer = DummyPrinter()
                printer.connect()
            
            if printer.test_print():
                self.status_bar.showMessage(self.i18n.t("test_success"), 3000)
                QMessageBox.information(self, "Test Print", self.i18n.t("test_success"))
            else:
                self.status_bar.showMessage(self.i18n.t("test_error"), 3000)
            
            printer.disconnect()
            
        except Exception as e:
            QMessageBox.critical(self, "Test Error", f"Test print error: {e}")
    
    def open_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self.settings, self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec_()
    
    def on_settings_changed(self):
        """Handle settings changes."""
        # Reload language if changed
        language = self.settings.get_default_language()
        self.i18n.set_language(language)
        index = self.language_combo.findData(language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        self.status_bar.showMessage(self.i18n.t("settings_saved"), 3000)
    
    def open_logo_editor(self):
        """Open logo editor dialog."""
        company_name = self.company_combo.currentText()
        dialog = LogoEditorDialog(company_name, self)
        dialog.exec_()
        
        # Update preview in case logo was changed
        self.update_preview()
