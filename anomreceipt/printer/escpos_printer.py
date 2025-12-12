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
            try:
                self.printer = Usb(vendor_id, product_id, profile="TM-T88III")
            except TypeError:
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
            except Exception as e:
                logger.warning(f"Error during printer disconnect: {e}")
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
            # Invalidate device to avoid further errors in chain
            self.printer = None
            return False
            
    def print_line(self, char='-', length=48):
        """Print a line separator"""
        if self.is_connected():
            self.print_text(char * length + '\n')
            
    def print_logo(self, logo_text) -> bool:
        """Print ASCII logo"""
        if not self.is_connected():
            return False
        try:
            self.printer.set(align='center')
            for line in logo_text.split('\n'):
                if not self.print_text(line + '\n'):
                    return False
            self.printer.set(align='left')
            return True
        except Exception as e:
            logger.error(f"Error printing logo: {e}")
            self.printer = None
            return False

    def _profile_media_width(self) -> int:
        try:
            prof = getattr(self.printer, 'profile', None)
            if prof is not None:
                data = getattr(prof, 'profile_data', None) or {}
                media = data.get('media') or {}
                width_px = (media.get('width') or {}).get('pixel')
                if isinstance(width_px, int) and width_px > 0:
                    return width_px
        except Exception:
            pass
        return 384

    def print_image(self, image_path: str):
        """Print a raster image (PNG/JPEG). Uses Pillow to ensure compatibility."""
        if not self.is_connected():
            logger.warning("Cannot print: not connected")
            return False
        try:
            from PIL import Image
            img = Image.open(image_path)
            target_w = self._profile_media_width()
            if img.width > target_w:
                ratio = target_w / float(img.width)
                new_h = max(1, int(img.height * ratio))
                img = img.resize((int(target_w), new_h), Image.LANCZOS)
            img = img.convert('1')
            try:
                self.printer.set(align='center')
            except Exception:
                pass
            try:
                self.printer.image(img)
            except Exception:
                self.printer.image(image_path)
            try:
                self.printer.set(align='left')
            except Exception:
                pass
            return True
        except Exception as e:
            logger.error(f"Error printing image: {e}")
            return False
            
    def feed_lines(self, lines=1):
        """Feed paper by specified number of lines"""
        if self.is_connected():
            for _ in range(lines):
                try:
                    self.printer.text('\n')
                except Exception as e:
                    logger.error(f"Error feeding lines: {e}")
                    self.printer = None
                    break
                
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
        
    def print_receipt(self, receipt_data, width: int = 48):
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
            # Print logo image if present
            if receipt_data.get('logo_image') and self.is_connected():
                if not self.print_image(receipt_data['logo_image']):
                    return False
                self.feed_lines(1)
            # Print ASCII logo if present
            if receipt_data.get('logo'):
                if not self.print_logo(receipt_data['logo']):
                    return False
                self.feed_lines(1)
                
            # Utility to wrap a line to chunks of given width
            def wrap_line(s: str, w: int):
                out = []
                i = 0
                while i < len(s):
                    out.append(s[i:i+w])
                    i += w
                return out or ['']

            # Print header
            if receipt_data.get('header'):
                for line in receipt_data['header']:
                    for chunk in wrap_line(line, width):
                        if not self.print_text(chunk + '\n', align='center', bold=True):
                            return False
                self.print_line(length=width)
                
            # Print items
            if receipt_data.get('items'):
                for item in receipt_data['items']:
                    name = item.get('name', '')
                    price = item.get('price', '')
                    qty = item.get('qty', '')
                    base = f"{qty}x {name}" if qty else name
                    # Right-align price at the end; truncate left if needed
                    if width > len(price):
                        left_space = width - len(price)
                        left = base[:left_space].ljust(left_space)
                        line = left + price
                    else:
                        line = (base + ' ' + price)[:width]

                    if not self.print_text(line + '\n'):
                        return False
                    
                self.print_line()
                
            # Print footer
            if receipt_data.get('footer'):
                for line in receipt_data['footer']:
                    for chunk in wrap_line(line, width):
                        if not self.print_text(chunk + '\n'):
                            return False
                    
            # Feed and cut
            if self.is_connected():
                self.feed_lines(3)
                if receipt_data.get('cut', True):
                    self.cut_paper()
                
            return True
        except Exception as e:
            logger.error(f"Error printing receipt: {e}")
            return False
