"""
ESC/POS printer abstraction for Epson TM-T70II.
"""
from typing import Optional
import logging

try:
    from escpos.printer import Usb, Network, Dummy
except ImportError:
    # Fallback if python-escpos is not installed
    Usb = None
    Network = None
    Dummy = None


logger = logging.getLogger(__name__)


class EpsonTM70Printer:
    """
    Printer abstraction for Epson TM-T70II thermal receipt printer.
    Supports USB and Network connections.
    """
    
    # Common Epson vendor/product IDs for TM-T70II
    DEFAULT_VENDOR_ID = 0x04b8
    DEFAULT_PRODUCT_ID = 0x0202
    
    def __init__(self, connection_type: str = "usb", 
                 device_path: Optional[str] = None,
                 ip_address: Optional[str] = None,
                 port: int = 9100):
        """
        Initialize printer connection.
        
        Args:
            connection_type: "usb" or "network"
            device_path: USB device path (optional)
            ip_address: Printer IP address for network connection
            port: Network port (default 9100 for ESC/POS)
        """
        self.connection_type = connection_type
        self.device_path = device_path
        self.ip_address = ip_address
        self.port = port
        self.printer = None
        self._is_connected = False
    
    def connect(self) -> bool:
        """
        Connect to the printer.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.connection_type == "usb":
                if not Usb:
                    logger.error("python-escpos not installed")
                    return False
                
                if self.device_path:
                    # Use specific device path if provided
                    self.printer = Usb(0, 0, 0, device_path=self.device_path)
                else:
                    # Use default Epson TM-T70II IDs
                    self.printer = Usb(
                        self.DEFAULT_VENDOR_ID,
                        self.DEFAULT_PRODUCT_ID
                    )
            
            elif self.connection_type == "network":
                if not Network:
                    logger.error("python-escpos not installed")
                    return False
                
                if not self.ip_address:
                    logger.error("IP address required for network connection")
                    return False
                
                self.printer = Network(self.ip_address, self.port)
            
            else:
                logger.error(f"Unknown connection type: {self.connection_type}")
                return False
            
            self._is_connected = True
            logger.info(f"Connected to printer via {self.connection_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to printer: {e}")
            self._is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from printer."""
        if self.printer:
            try:
                self.printer.close()
                logger.info("Disconnected from printer")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
            finally:
                self.printer = None
                self._is_connected = False
    
    def is_connected(self) -> bool:
        """Check if printer is connected."""
        return self._is_connected
    
    def print_text(self, text: str) -> bool:
        """
        Print plain text.
        
        Args:
            text: Text to print
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected or not self.printer:
            logger.error("Printer not connected")
            return False
        
        try:
            self.printer.text(text)
            self.printer.cut()
            logger.info("Text printed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to print text: {e}")
            return False
    
    def print_receipt(self, receipt_text: str) -> bool:
        """
        Print a formatted receipt.
        
        Args:
            receipt_text: Formatted receipt text
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_connected or not self.printer:
            logger.error("Printer not connected")
            return False
        
        try:
            # Set font to monospaced
            self.printer.set(font='a', width=1, height=1)
            
            # Print the receipt
            self.printer.text(receipt_text + "\n\n")
            
            # Cut paper
            self.printer.cut()
            
            logger.info("Receipt printed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to print receipt: {e}")
            return False
    
    def test_print(self) -> bool:
        """
        Perform a test print.
        
        Returns:
            True if successful, False otherwise
        """
        test_text = """
========================================
        PRINTER TEST
========================================
Epson TM-T70II Test Print

Connection: {}
Date: {}

If you can read this, the printer
is working correctly!

========================================
""".format(self.connection_type, 
           __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        return self.print_text(test_text)
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


class DummyPrinter(EpsonTM70Printer):
    """
    Dummy printer for testing without hardware.
    Simulates printer operations and logs output.
    """
    
    def __init__(self):
        """Initialize dummy printer."""
        super().__init__(connection_type="dummy")
        self.last_output = ""
    
    def connect(self) -> bool:
        """Simulate connection."""
        self._is_connected = True
        logger.info("Dummy printer connected (simulation mode)")
        return True
    
    def disconnect(self):
        """Simulate disconnection."""
        self._is_connected = False
        logger.info("Dummy printer disconnected")
    
    def print_text(self, text: str) -> bool:
        """Simulate text printing."""
        self.last_output = text
        logger.info(f"Dummy printer output:\n{text}")
        return True
    
    def print_receipt(self, receipt_text: str) -> bool:
        """Simulate receipt printing."""
        self.last_output = receipt_text
        logger.info(f"Dummy printer receipt:\n{receipt_text}")
        return True
    
    def test_print(self) -> bool:
        """Simulate test print."""
        test_text = "DUMMY PRINTER TEST - No hardware connected"
        self.last_output = test_text
        logger.info(f"Dummy printer test: {test_text}")
        return True
