"""
Main window for the receipt printing application.
"""
from decimal import Decimal
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit,
    QTableWidget, QTableWidgetItem, QGroupBox, QStatusBar,
    QMessageBox, QDateTimeEdit, QFileDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal
from models import ReceiptData, ReceiptItem
from templates.companies import get_company, get_company_names
from templates.template_engine import ReceiptTemplate
from templates.template_engine import get_company_logo, LOGOS_DIR
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
        self.template_engine = ReceiptTemplate(width=self.settings.get_receipt_width())
        
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
        # Payment tracking
        self._last_payment_method = None
        self._visa_details = None
        # Enable preview editing by default
        if hasattr(self, 'edit_toggle'):
            self.edit_toggle.setChecked(True)
    
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

        # Store / POS fields
        self.store_number_edit = QLineEdit()
        self.store_number_edit.textChanged.connect(self.update_preview)
        layout.addRow(self.i18n.t("store_number"), self.store_number_edit)

        self.register_id_edit = QLineEdit()
        self.register_id_edit.textChanged.connect(self.update_preview)
        layout.addRow(self.i18n.t("register_id"), self.register_id_edit)

        self.cashier_name_edit = QLineEdit()
        self.cashier_name_edit.textChanged.connect(self.update_preview)
        layout.addRow(self.i18n.t("cashier_name"), self.cashier_name_edit)

        self.receipt_id_edit = QLineEdit()
        self.receipt_id_edit.textChanged.connect(self.update_preview)
        layout.addRow(self.i18n.t("receipt_id"), self.receipt_id_edit)
        
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
        self.preview_text.setAcceptRichText(True)
        self.preview_text.setFont(QFont("Courier", 10))
        self.preview_text.setReadOnly(True)
        layout.addWidget(self.preview_text)

        # Editing toolbar
        toolbar = QHBoxLayout()
        self.edit_toggle = QPushButton(self.i18n.t("edit_preview"))
        self.edit_toggle.setCheckable(True)
        self.edit_toggle.toggled.connect(self.on_edit_toggle)
        toolbar.addWidget(self.edit_toggle)

        bold_btn = QPushButton(self.i18n.t("bold"))
        bold_btn.clicked.connect(self.make_bold)
        toolbar.addWidget(bold_btn)

        italic_btn = QPushButton(self.i18n.t("italic"))
        italic_btn.clicked.connect(self.make_italic)
        toolbar.addWidget(italic_btn)

        bigger_btn = QPushButton(self.i18n.t("bigger"))
        bigger_btn.clicked.connect(lambda: self.adjust_font_size(1))
        toolbar.addWidget(bigger_btn)

        smaller_btn = QPushButton(self.i18n.t("smaller"))
        smaller_btn.clicked.connect(lambda: self.adjust_font_size(-1))
        toolbar.addWidget(smaller_btn)

        regen_btn = QPushButton(self.i18n.t("regenerate"))
        regen_btn.clicked.connect(self.update_preview_from_data)
        toolbar.addWidget(regen_btn)

        save_btn = QPushButton(self.i18n.t("save_preview"))
        save_btn.clicked.connect(self.save_preview)
        toolbar.addWidget(save_btn)

        load_btn = QPushButton(self.i18n.t("load_preview"))
        load_btn.clicked.connect(self.load_preview)
        toolbar.addWidget(load_btn)

        layout.addLayout(toolbar)
        
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
            self.i18n.t("visa"),
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
        # Load defaults for company extras
        company = get_company(company_name)
        if company:
            self.store_number_edit.setText(getattr(company, 'store_number', '') or '')
            self.register_id_edit.setText(getattr(company, 'register_id', '') or '')
            self.cashier_name_edit.setText(getattr(company, 'default_cashier_name', '') or '')
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
        # If user is editing preview, don't overwrite unless explicit
        if hasattr(self, 'edit_toggle') and self.edit_toggle.isChecked():
            # Still keep totals synced
            self.update_preview_from_data(update_view=False)
            return
        self.update_preview_from_data(update_view=True)

    def update_preview_from_data(self, update_view: bool = True):
        """Build receipt data and optionally update preview area."""
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
        
        # Payment details (random for Visa)
        payment_text = self.payment_combo.currentText()
        pay_details = None
        if 'visa' in payment_text.lower():
            # Keep same details while editing, regenerate when switching to Visa
            from random import randint, choice
            if self._last_payment_method != 'visa' or not self._visa_details:
                last4 = f"{randint(0, 9999):04d}"
                auth = ''.join(choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(6))
                trans_id = f"{randint(10000000, 99999999)}"
                term_id = f"T{randint(100000, 999999)}"
                rrn = ''.join(choice('0123456789') for _ in range(12))
                stan = ''.join(choice('0123456789') for _ in range(6))
                mid = ''.join(choice('0123456789') for _ in range(15))
                expiry = f"{randint(1,12):02d}/{randint(24,29):02d}"
                entry = choice(["CHIP", "CTLS"])  # chip/contactless
                ac = ''.join(choice('0123456789ABCDEF') for _ in range(16))
                self._visa_details = {
                    "card_type": "VISA",
                    "pan_masked": f"**** **** **** {last4}",
                    "expiry": expiry,
                    "auth_code": auth,
                    "aid": "A0000000031010",
                    "app_label": "VISA CREDIT",
                    "tvr": "0000000000",
                    "tsi": "E800",
                    "transaction_id": trans_id,
                    "terminal_id": term_id,
                    "rrn": rrn,
                    "stan": stan,
                    "merchant_id": mid,
                    "entry_mode": entry,
                    "app_cryptogram": ac,
                }
            pay_details = dict(self._visa_details)
            self._last_payment_method = 'visa'
        else:
            self._visa_details = None
            self._last_payment_method = payment_text.lower()

        # Auto-fill receipt id if empty (peek, no commit here)
        if not getattr(self, '_filling_receipt_id', False):
            if not self.receipt_id_edit.text().strip():
                try:
                    self._filling_receipt_id = True
                    self.receipt_id_edit.setText(self.settings.peek_next_receipt_id(company_name))
                finally:
                    self._filling_receipt_id = False

        self.current_receipt = ReceiptData(
            company=company,
            items=items,
            customer_name=self.customer_name.text() or None,
            reference_number=self.reference_number.text() or None,
            invoice_number=self.invoice_number.text() or None,
            date_time=dt,
            payment_method=payment_text,
            language=language,
            currency="EUR",
            payment_details=pay_details,
            store_number=self.store_number_edit.text() or None,
            register_id=self.register_id_edit.text() or None,
            cashier_name=self.cashier_name_edit.text() or None,
            receipt_id=self.receipt_id_edit.text() or None,
        )
        
        # Update totals
        self.subtotal_label.setText(f"{float(self.current_receipt.subtotal):.2f} EUR")
        self.total_vat_label.setText(f"{float(self.current_receipt.total_vat):.2f} EUR")
        self.grand_total_label.setText(f"{float(self.current_receipt.total):.2f} EUR")
        
        # Ensure template width reflects settings
        self.template_engine.width = self.settings.get_receipt_width()
        # Render preview to HTML-pre block to preserve monospacing and allow inline styles
        if update_view:
            receipt_text = self.template_engine.render(self.current_receipt)
            escaped = receipt_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Optional logo image embed
            img_html = ''
            try:
                logo_path, ltype = get_company_logo(self.current_receipt.company)
                if logo_path and ltype == 'png':
                    img_html = f"<div style='text-align:center'><img src='file://{logo_path}' style='max-width:100%;height:auto' /></div>\n"
            except Exception:
                pass
            html = (
                img_html +
                "<pre style=\"font-family: 'Courier New', monospace; font-size: 12px; white-space: pre;\">"
                + escaped + "</pre>"
            )
            self.preview_text.setHtml(html)

    def on_edit_toggle(self, checked: bool):
        self.preview_text.setReadOnly(not checked)

    def make_bold(self):
        cursor = self.preview_text.textCursor()
        if not cursor.hasSelection():
            return
        cursor.mergeCharFormat(self._format(weight=QFont.Bold))

    def make_italic(self):
        cursor = self.preview_text.textCursor()
        if not cursor.hasSelection():
            return
        cursor.mergeCharFormat(self._format(italic=True))

    def adjust_font_size(self, delta: int):
        cursor = self.preview_text.textCursor()
        if not cursor.hasSelection():
            return
        fmt = cursor.charFormat()
        size = fmt.fontPointSize() or 12
        size = max(6, min(48, size + delta))
        cursor.mergeCharFormat(self._format(point_size=size))

    def _format(self, weight=None, italic=None, point_size=None):
        from PyQt5.QtGui import QTextCharFormat
        fmt = QTextCharFormat()
        if weight is not None:
            fmt.setFontWeight(weight)
        if italic is not None:
            fmt.setFontItalic(italic)
        if point_size is not None:
            fmt.setFontPointSize(point_size)
        return fmt

    def save_preview(self):
        path, selected = QFileDialog.getSaveFileName(
            self, self.i18n.t("save_preview"), "", "HTML Files (*.html *.htm);;Text Files (*.txt)"
        )
        if not path:
            return
        try:
            if path.lower().endswith((".html", ".htm")):
                content = self.preview_text.toHtml()
            else:
                content = self.preview_text.toPlainText()
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.status_bar.showMessage("Preview saved", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")

    def load_preview(self):
        path, selected = QFileDialog.getOpenFileName(
            self, self.i18n.t("load_preview"), "", "HTML Files (*.html *.htm);;Text Files (*.txt);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
            if path.lower().endswith((".html", ".htm")):
                self.preview_text.setHtml(data)
            else:
                esc = data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html = (
                    "<pre style=\"font-family: 'Courier New', monospace; font-size: 12px; white-space: pre;\">"
                    + esc + "</pre>"
                )
                self.preview_text.setHtml(html)
            # Keep edit mode on
            if hasattr(self, 'edit_toggle'):
                self.edit_toggle.setChecked(True)
            self.status_bar.showMessage("Preview loaded", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load: {e}")
    
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

        # Ensure receipt id committed
        if not (self.receipt_id_edit.text() or "").strip():
            rid = self.settings.commit_next_receipt_id(self.company_combo.currentText())
            self.receipt_id_edit.setText(rid)
            self.update_preview_from_data(update_view=True)
        else:
            # If field equals today's peek, treat as next and commit
            peek = self.settings.peek_next_receipt_id(self.company_combo.currentText())
            if self.receipt_id_edit.text().strip() == peek:
                rid = self.settings.commit_next_receipt_id(self.company_combo.currentText())
                self.receipt_id_edit.setText(rid)
                self.update_preview_from_data(update_view=True)

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
            
        # Get receipt content: if user edited, send rich text; otherwise plain
        ok = False
        if hasattr(self, 'edit_toggle') and self.edit_toggle.isChecked():
            html = self.preview_text.toHtml()
            try:
                ok = printer.print_rich_html(html)
            except Exception:
                ok = False
        else:
            # If PNG logo exists, print it first
            logo_path, ltype = get_company_logo(self.current_receipt.company)
            if logo_path and ltype == 'png':
                try:
                    printer.print_image(logo_path)
                except Exception:
                    pass
            receipt_text = self.template_engine.render(self.current_receipt)
            ok = printer.print_receipt(receipt_text)
        
        # Print status
        if ok:
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
        # Re-render with possibly new receipt width
        self.update_preview_from_data(update_view=True)
    
    def open_logo_editor(self):
        """Open logo editor dialog."""
        company_name = self.company_combo.currentText()
        dialog = LogoEditorDialog(company_name, self)
        dialog.exec_()
        
        # Update preview in case logo was changed
        self.update_preview()
