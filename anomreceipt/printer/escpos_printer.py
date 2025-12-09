"""
ESC/POS Printer interface for Epson TM-T70II
Supports USB and network (IP) connections
"""

from escpos.printer import Usb, Network
from escpos.exceptions import USBNotFoundError
import logging

logger = logging.getLogger(__name__)


class ESCPOSPrinter:
    """Wrapper for ESC/POS printer operations"""
    
    def __init__(self):
        self.printer = None
        self.connection_type = None
        
    def connect_usb(self, vendor_id=0x04b8, product_id=0x0202):
        """
        Connect to printer via USB
        Default IDs are for Epson TM-T70II
        """
        try:
            self.printer = Usb(vendor_id, product_id)
            self.connection_type = "USB"
            logger.info(f"Connected to USB printer (VID: {hex(vendor_id)}, PID: {hex(product_id)})")
            return True
        except USBNotFoundError as e:
            logger.error(f"USB printer not found: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to USB printer: {e}")
            return False
            
    def connect_network(self, host, port=9100):
        """
        Connect to printer via network (IP)
        Default port 9100 is standard for ESC/POS network printers
        """
        try:
            self.printer = Network(host, port)
            self.connection_type = "Network"
            logger.info(f"Connected to network printer at {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to network printer: {e}")
            return False
            
    def is_connected(self):
        """Check if printer is connected"""
        return self.printer is not None
        
    def disconnect(self):
        """Disconnect from printer"""
        if self.printer:
            try:
                self.printer.close()
            except:
                pass
            self.printer = None
            self.connection_type = None
            logger.info("Disconnected from printer")
            
    def print_text(self, text, align='left', bold=False, double_width=False, double_height=False):
        """Print text with formatting"""
        if not self.is_connected():
            logger.warning("Cannot print: not connected")
            return False
            
        try:
            # Set alignment
            if align == 'center':
                self.printer.set(align='center')
            elif align == 'right':
                self.printer.set(align='right')
            else:
                self.printer.set(align='left')
                
            # Set text formatting
            if bold or double_width or double_height:
                width = 2 if double_width else 1
                height = 2 if double_height else 1
                self.printer.set(
                    bold=bold,
                    double_width=double_width,
                    double_height=double_height,
                    width=width,
                    height=height
                )
                
            self.printer.text(text)
            
            # Reset formatting
            self.printer.set()
            return True
        except Exception as e:
            logger.error(f"Error printing text: {e}")
            return False
            
    def print_line(self, char='-', length=48):
        """Print a line separator"""
        if self.is_connected():
            self.print_text(char * length + '\n')
            
    def print_logo(self, logo_text):
        """Print ASCII logo"""
        if self.is_connected():
            self.printer.set(align='center')
            for line in logo_text.split('\n'):
                self.print_text(line + '\n')
            self.printer.set(align='left')
            
    def feed_lines(self, lines=1):
        """Feed paper by specified number of lines"""
        if self.is_connected():
            for _ in range(lines):
                self.printer.text('\n')
                
    def cut_paper(self, partial=True):
        """Cut paper (partial cut by default)"""
        if self.is_connected():
            try:
                if partial:
                    self.printer.cut(mode='PART')
                else:
                    self.printer.cut(mode='FULL')
                return True
            except Exception as e:
                logger.error(f"Error cutting paper: {e}")
                return False
        return False
        
    def print_receipt(self, receipt_data):
        """
        Print a complete receipt from structured data
        
        receipt_data structure:
        {
            'logo': 'ASCII logo text',
            'header': ['Line 1', 'Line 2'],
            'items': [{'name': 'Item', 'price': '10.00'}],
            'footer': ['Line 1', 'Line 2'],
            'cut': True
        }
        """
        if not self.is_connected():
            return False
            
        try:
            # Print logo if present
            if receipt_data.get('logo'):
                self.print_logo(receipt_data['logo'])
                self.feed_lines(1)
                
            # Print header
            if receipt_data.get('header'):
                for line in receipt_data['header']:
                    self.print_text(line + '\n', align='center', bold=True)
                self.print_line()
                
            # Print items
            if receipt_data.get('items'):
                for item in receipt_data['items']:
                    name = item.get('name', '')
                    price = item.get('price', '')
                    qty = item.get('qty', '')
                    
                    if qty:
                        line = f"{qty}x {name}"
                    else:
                        line = name
                        
                    # Format line with price on the right
                    spaces = 48 - len(line) - len(price)
                    if spaces > 0:
                        line += ' ' * spaces
                    line += price
                    
                    self.print_text(line + '\n')
                    
                self.print_line()
                
            # Print footer
            if receipt_data.get('footer'):
                for line in receipt_data['footer']:
                    self.print_text(line + '\n')
                    
            # Feed and cut
            self.feed_lines(3)
            if receipt_data.get('cut', True):
                self.cut_paper()
                
            return True
        except Exception as e:
            logger.error(f"Error printing receipt: {e}")
            return False
