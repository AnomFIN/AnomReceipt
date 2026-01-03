"""
ESC/POS Printer interface for Epson TM-T70II
Supports USB and network (IP) connections
"""

from escpos.printer import Usb, Network
from escpos.exceptions import USBNotFoundError
import logging
import re

logger = logging.getLogger(__name__)

# Barcode markup regex pattern (matches >BARCODE TYPE DATA>)
# Allows digits and uppercase letters for data (most barcode types use these)
BARCODE_MARKUP_PATTERN = r'^>BARCODE\s+([A-Z0-9-]+)\s+([A-Z0-9]+)>(.*)$'


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
            
    def print_barcode(self, data: str, barcode_type: str = 'EAN13') -> bool:
        """
        Print a barcode.
        
        Args:
            data: Barcode data (e.g., '1234567890123' for EAN13)
            barcode_type: Type of barcode (EAN13, EAN8, UPC-A, CODE39, etc.)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Cannot print barcode: not connected")
            return False
        
        try:
            # Center the barcode
            try:
                self.printer.set(align='center')
            except Exception:
                pass
            
            # Print the barcode
            # python-escpos supports various barcode types
            self.printer.barcode(data, barcode_type)
            
            # Reset alignment
            try:
                self.printer.set(align='left')
            except Exception:
                pass
            
            logger.info(f"Barcode printed: {barcode_type} - {data}")
            return True
        except Exception as e:
            logger.error(f"Error printing barcode: {e}")
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
        
    def _parse_barcode_markup(self, text: str) -> tuple:
        """
        Parse barcode markup from text.
        
        Markup format: >BARCODE TYPE DATA>
        Examples:
          >BARCODE EAN13 1234567890123>
          >BARCODE CODE39 ABC123>
          >BARCODE EAN8 12345678>
        
        Args:
            text: Text that may contain barcode markup
        
        Returns:
            Tuple of (is_barcode, barcode_type, barcode_data, remaining_text)
            If not a barcode, returns (False, None, None, text)
        """
        # Match barcode markup pattern using shared constant
        match = re.match(BARCODE_MARKUP_PATTERN, text.strip())
        
        if match:
            barcode_type = match.group(1)
            barcode_data = match.group(2)
            remaining = match.group(3).strip()
            
            # Validate barcode data based on type
            valid, error = self._validate_barcode(barcode_type, barcode_data)
            if not valid:
                logger.warning(f"Invalid barcode data for {barcode_type}: {error}")
                return False, None, None, text
            
            return True, barcode_type, barcode_data, remaining
        
        return False, None, None, text
    
    def _validate_barcode(self, barcode_type: str, data: str) -> tuple:
        """
        Validate barcode data for a given barcode type.
        
        Args:
            barcode_type: Type of barcode (EAN13, EAN8, etc.)
            data: Barcode data to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        barcode_type = barcode_type.upper()
        
        # EAN13 requires exactly 13 digits
        if barcode_type == 'EAN13':
            if len(data) != 13 or not data.isdigit():
                return False, "EAN13 requires exactly 13 digits"
        
        # EAN8 requires exactly 8 digits
        elif barcode_type == 'EAN8':
            if len(data) != 8 or not data.isdigit():
                return False, "EAN8 requires exactly 8 digits"
        
        # UPC-A requires exactly 12 digits (supports multiple format variations)
        elif barcode_type in ['UPC-A', 'UPCA', 'UPC_A']:
            if len(data) != 12 or not data.isdigit():
                return False, "UPC-A requires exactly 12 digits"
        
        # CODE39 allows alphanumeric but has length limits
        elif barcode_type in ['CODE39', 'CODE-39']:
            if len(data) > 43:
                return False, "CODE39 data too long (max 43 characters)"
            # CODE39 supports: 0-9, A-Z, and special chars (-, ., $, /, +, %, space)
            # Hyphen at end of character class for clarity
            if not re.match(r'^[0-9A-Z. $/+%-]+$', data):
                return False, "CODE39 supports only: 0-9, A-Z, -, ., $, /, +, %, space"
        
        # CODE128 has more flexibility
        elif barcode_type in ['CODE128', 'CODE-128']:
            if len(data) > 80:
                return False, "CODE128 data too long (max 80 characters)"
        
        # For other types, just check length isn't excessive
        else:
            if len(data) > 100:
                return False, "Barcode data too long"
        
        return True, None
    
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
                    # Check for barcode markup
                    is_barcode, bc_type, bc_data, remaining = self._parse_barcode_markup(line)
                    if is_barcode:
                        # Print the barcode
                        if not self.print_barcode(bc_data, bc_type):
                            logger.warning(f"Failed to print barcode, falling back to text")
                            # Fallback: print as text
                            if not self.print_text(line + '\n', align='center', bold=True):
                                return False
                        # Print any remaining text on the line
                        if remaining:
                            if not self.print_text(remaining + '\n', align='center', bold=True):
                                return False
                    else:
                        # Regular text line
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
                    # Check for barcode markup
                    is_barcode, bc_type, bc_data, remaining = self._parse_barcode_markup(line)
                    if is_barcode:
                        # Print the barcode
                        if not self.print_barcode(bc_data, bc_type):
                            logger.warning(f"Failed to print barcode, falling back to text")
                            # Fallback: print as text
                            if not self.print_text(line + '\n'):
                                return False
                        # Print any remaining text on the line
                        if remaining:
                            if not self.print_text(remaining + '\n'):
                                return False
                    else:
                        # Regular text line
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
    
    def print_rich_html(self, html: str) -> bool:
        """
        Print HTML with formatting (bold, italic, font size).
        Supports <b>/<strong>, <i>/<em>, and font-size styling.
        
        Args:
            html: HTML content to print
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Cannot print HTML: not connected")
            return False
        
        try:
            from html.parser import HTMLParser
            
            class _Parser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.segments = []  # list of (text|('IMG',path)|('BARCODE',type,data), bold, italic, scale)
                    self.bold = False
                    self.italic = False
                    self.scale = 1
                    self._buf = []
                
                def flush(self):
                    if self._buf:
                        text = ''.join(self._buf)
                        self.segments.append((text, self.bold, self.italic, self.scale))
                        self._buf = []
                
                def handle_starttag(self, tag, attrs):
                    if tag in ('b', 'strong'):
                        self.flush()
                        self.bold = True
                    elif tag in ('i', 'em'):
                        self.flush()
                        self.italic = True
                    elif tag == 'br':
                        self._buf.append('\n')
                    elif tag in ('p', 'div'):
                        self._buf.append('\n')
                    elif tag == 'img':
                        # Output pending text then add image segment
                        self.flush()
                        src = dict(attrs).get('src')
                        if src and src.startswith('file://'):
                            path = src[len('file://'):]
                            self.segments.append((('IMG', path), self.bold, self.italic, self.scale))
                    elif tag == 'span':
                        # Look for style font-size
                        style = dict(attrs).get('style', '')
                        size = None
                        for part in style.split(';'):
                            if 'font-size' in part:
                                try:
                                    size_val = part.split(':', 1)[1].strip()
                                    if size_val.endswith('px'):
                                        size = int(float(size_val[:-2]))
                                    else:
                                        size = int(float(size_val))
                                except Exception:
                                    pass
                        if size:
                            self.flush()
                            # Map size to scale multiplier
                            if size >= 18:
                                scale = 2
                            else:
                                scale = 1
                            self.scale = max(1, min(8, scale))
                
                def handle_endtag(self, tag):
                    if tag in ('b', 'strong'):
                        self.flush()
                        self.bold = False
                    elif tag in ('i', 'em'):
                        self.flush()
                        self.italic = False
                    elif tag == 'span':
                        self.flush()
                        self.scale = 1
                    elif tag in ('p', 'div'):
                        self._buf.append('\n')
                
                def handle_data(self, data):
                    self._buf.append(data)
                
                def close(self):
                    self.flush()
                    super().close()
            
            parser = _Parser()
            parser.feed(html)
            parser.close()
            
            # Print each segment with appropriate formatting
            for seg, bold, italic, scale in parser.segments:
                # Handle image
                if isinstance(seg, tuple) and seg and seg[0] == 'IMG':
                    path = seg[1]
                    if not self.print_image(path):
                        logger.warning(f"Failed to print image: {path}")
                    continue
                
                # Handle barcode (detect barcode markup in text)
                text = seg
                if text:
                    # Check for barcode markup
                    is_barcode, bc_type, bc_data, remaining = self._parse_barcode_markup(text.strip())
                    if is_barcode:
                        if not self.print_barcode(bc_data, bc_type):
                            logger.warning(f"Failed to print barcode, printing as text")
                            # Fallback to text
                            if not self.print_text(text, bold=bold):
                                return False
                        if remaining:
                            if not self.print_text(remaining, bold=bold):
                                return False
                        continue
                
                # Skip empty text segments
                if not text or not text.strip():
                    continue
                
                # Print text with formatting
                # Map italic to nothing (most ESC/POS printers don't support italic)
                # Use double_width and double_height for scale
                double_width = (scale >= 2)
                double_height = (scale >= 2)
                
                if not self.print_text(text, bold=bold, double_width=double_width, double_height=double_height):
                    return False
            
            # Feed and cut
            if self.is_connected():
                self.feed_lines(3)
                self.cut_paper()
            
            return True
        except Exception as e:
            logger.error(f"Error printing HTML: {e}", exc_info=True)
            return False
