"""
Settings dialog for printer and application configuration.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QGroupBox,
    QSpinBox, QMessageBox
)
from PyQt5.QtCore import pyqtSignal
from config.settings import Settings
from i18n import get_i18n
from printer.escpos_printer import EpsonTM70Printer


class SettingsDialog(QDialog):
    """Dialog for application settings."""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, settings: Settings, parent=None):
        """
        Initialize settings dialog.
        
        Args:
            settings: Settings instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.settings = settings
        self.i18n = get_i18n()
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle(self.i18n.t("settings_title"))
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Printer settings group
        printer_group = QGroupBox(self.i18n.t("printer_settings"))
        printer_layout = QFormLayout()
        
        # Connection type
        self.connection_type = QComboBox()
        self.connection_type.addItem(self.i18n.t("usb"), "usb")
        self.connection_type.addItem(self.i18n.t("network"), "network")
        self.connection_type.currentIndexChanged.connect(self.on_connection_type_changed)
        printer_layout.addRow(self.i18n.t("connection_type"), self.connection_type)
        
        # Device path (for USB)
        self.device_path = QLineEdit()
        self.device_path.setPlaceholderText("/dev/usb/lp0 or empty for auto-detect")
        self.device_path_label = QLabel(self.i18n.t("device_path"))
        printer_layout.addRow(self.device_path_label, self.device_path)
        
        # IP address (for network)
        self.ip_address = QLineEdit()
        self.ip_address.setPlaceholderText("192.168.1.100")
        self.ip_address_label = QLabel(self.i18n.t("ip_address"))
        printer_layout.addRow(self.ip_address_label, self.ip_address)
        
        # Port (for network)
        self.port = QSpinBox()
        self.port.setRange(1, 65535)
        self.port.setValue(9100)
        self.port_label = QLabel(self.i18n.t("port"))
        printer_layout.addRow(self.port_label, self.port)
        
        # Test connection button
        test_btn = QPushButton(self.i18n.t("test_connection"))
        test_btn.clicked.connect(self.test_printer_connection)
        printer_layout.addRow("", test_btn)
        
        printer_group.setLayout(printer_layout)
        layout.addWidget(printer_group)
        
        # Default settings group
        defaults_group = QGroupBox("Defaults")
        defaults_layout = QFormLayout()
        
        # Default language
        self.default_language = QComboBox()
        self.default_language.addItem("Finnish", "FI")
        self.default_language.addItem("English", "EN")
        defaults_layout.addRow(self.i18n.t("default_language"), self.default_language)
        
        defaults_group.setLayout(defaults_layout)
        layout.addWidget(defaults_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton(self.i18n.t("save"))
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton(self.i18n.t("cancel"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Initial visibility update
        self.on_connection_type_changed()
    
    def load_settings(self):
        """Load current settings into UI."""
        printer_config = self.settings.get_printer_config()
        
        # Connection type
        conn_type = printer_config.get("connection_type", "usb")
        index = self.connection_type.findData(conn_type)
        if index >= 0:
            self.connection_type.setCurrentIndex(index)
        
        # Device path
        device_path = printer_config.get("device_path", "")
        self.device_path.setText(device_path or "")
        
        # IP address
        ip_address = printer_config.get("ip_address", "")
        self.ip_address.setText(ip_address or "")
        
        # Port
        port = printer_config.get("port", 9100)
        self.port.setValue(port)
        
        # Default language
        lang = self.settings.get_default_language()
        index = self.default_language.findData(lang)
        if index >= 0:
            self.default_language.setCurrentIndex(index)
    
    def on_connection_type_changed(self):
        """Handle connection type change."""
        conn_type = self.connection_type.currentData()
        
        # Show/hide fields based on connection type
        is_usb = conn_type == "usb"
        is_network = conn_type == "network"
        
        self.device_path_label.setVisible(is_usb)
        self.device_path.setVisible(is_usb)
        
        self.ip_address_label.setVisible(is_network)
        self.ip_address.setVisible(is_network)
        self.port_label.setVisible(is_network)
        self.port.setVisible(is_network)
    
    def test_printer_connection(self):
        """Test printer connection with current settings."""
        conn_type = self.connection_type.currentData()
        device_path = self.device_path.text() or None
        ip_address = self.ip_address.text() or None
        port = self.port.value()
        
        try:
            printer = EpsonTM70Printer(
                connection_type=conn_type,
                device_path=device_path,
                ip_address=ip_address,
                port=port
            )
            
            if printer.connect():
                printer.disconnect()
                QMessageBox.information(
                    self,
                    self.i18n.t("connection_success"),
                    "Printer connection successful!"
                )
            else:
                QMessageBox.warning(
                    self,
                    self.i18n.t("connection_error"),
                    "Failed to connect to printer. Check your settings."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.i18n.t("connection_error"),
                f"Connection error: {e}"
            )
    
    def save_settings(self):
        """Save settings and close dialog."""
        # Save printer settings
        printer_config = {
            "connection_type": self.connection_type.currentData(),
            "device_path": self.device_path.text() or None,
            "ip_address": self.ip_address.text() or None,
            "port": self.port.value()
        }
        self.settings.set_printer_config(printer_config)
        
        # Save default language
        language = self.default_language.currentData()
        self.settings.set_default_language(language)
        
        # Emit signal
        self.settings_changed.emit()
        
        QMessageBox.information(
            self,
            self.i18n.t("settings_saved"),
            "Settings saved successfully!"
        )
        
        self.accept()
