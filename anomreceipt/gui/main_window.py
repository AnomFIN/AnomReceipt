"""
Main window for AnomReceipt application
Provides reactive Qt GUI for receipt printing
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QTextEdit, QGroupBox,
                             QMessageBox, QDialog, QFormLayout, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QFontDatabase
import logging
import math
import re
import threading

from ..printer import ESCPOSPrinter
from ..templates import TemplateManager
from ..locale import Translator
from .logo_editor import LogoEditor
from .settings_dialog import SettingsDialog
try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    requests = None
    BeautifulSoup = None

logger = logging.getLogger(__name__)

# Barcode markup regex patterns (shared constants)
# Pattern uses anchors (^ and $) for exact matching with re.match()
# Data part uses uppercase A-Z and 0-9 to match validation rules
BARCODE_MARKUP_PATTERN = r'^>BARCODE\s+([A-Z0-9-]+)\s+([A-Z0-9]+)>(.*)$'

# Image replacement characters that appear when HTML <img> tags are converted to plain text
IMAGE_REPLACEMENT_CHARS = ['?', '�', '☐', '⊠', '▯', '□']


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
        
        # Settings
        self.settings = {
            'receipt_width': 48,
            'receipt_length': 80,
            'logo_max_width': 48,
            'logo_max_height': 20,
            'feed_lines': 3,
            'cut_paper': True,
            'bold_header': True,
            'double_width_total': False
        }
        
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
        lang_layout = QVBoxLayout()
        
        # Language selectors
        lang_row = QHBoxLayout()
        lang_label = QLabel(self.translator.translate('language') + ':')
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['EN', 'FI'])
        self.lang_combo.currentTextChanged.connect(self.change_ui_language)
        lang_row.addWidget(lang_label)
        lang_row.addWidget(self.lang_combo)
        
        receipt_lang_label = QLabel(self.translator.translate('receipt_language') + ':')
        self.receipt_lang_combo = QComboBox()
        self.receipt_lang_combo.addItems(['EN', 'FI'])
        self.receipt_lang_combo.currentTextChanged.connect(self.update_preview)
        lang_row.addWidget(receipt_lang_label)
        lang_row.addWidget(self.receipt_lang_combo)
        lang_layout.addLayout(lang_row)
        
        # Settings button
        self.settings_btn = QPushButton('⚙ ' + self.translator.translate('settings'))
        self.settings_btn.clicked.connect(self.open_settings)
        lang_layout.addWidget(self.settings_btn)
        
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

        # Auto-fetch company info button
        self.fetch_info_btn = QPushButton('Fetch company info')
        self.fetch_info_btn.clicked.connect(self.fetch_company_info)
        company_layout.addWidget(self.fetch_info_btn)

        # Find nearest store by postal/city
        nearest_row = QHBoxLayout()
        self.find_store_input = QLineEdit()
        self.find_store_input.setPlaceholderText('Postinumero tai paikkakunta')
        nearest_row.addWidget(self.find_store_input)
        self.find_store_btn = QPushButton('Find nearest store')
        self.find_store_btn.clicked.connect(self.find_nearest_store)
        nearest_row.addWidget(self.find_store_btn)
        company_layout.addLayout(nearest_row)
        
        company_group.setLayout(company_layout)
        layout.addWidget(company_group)
        
        # Payment method
        payment_group = QGroupBox(self.translator.translate('payment_method'))
        payment_layout = QVBoxLayout()
        
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(['cash', 'card', 'visa', 'mobilepay', 'bank'])
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

        # Chain-styled logo generators
        self.gen_logo_puuilo_btn = QPushButton('Generate PUUILO logo')
        self.gen_logo_puuilo_btn.clicked.connect(self.generate_puuilo_logo)
        self.gen_logo_puuilo_btn.setVisible(False)
        layout.addWidget(self.gen_logo_puuilo_btn)

        self.gen_logo_tokmanni_btn = QPushButton('Generate TOKMANNI logo')
        self.gen_logo_tokmanni_btn.clicked.connect(self.generate_tokmanni_logo)
        self.gen_logo_tokmanni_btn.setVisible(False)
        layout.addWidget(self.gen_logo_tokmanni_btn)

        self.gen_logo_motonet_btn = QPushButton('Generate MOTONET logo')
        self.gen_logo_motonet_btn.clicked.connect(self.generate_motonet_logo)
        self.gen_logo_motonet_btn.setVisible(False)
        layout.addWidget(self.gen_logo_motonet_btn)
        
        panel.setLayout(layout)
        return panel

    def generate_puuilo_logo(self):
        try:
            from PIL import Image, ImageDraw, ImageFont
        except Exception:
            QMessageBox.warning(self, 'Pillow missing', 'Pillow not installed; cannot generate image.')
            return
        company_name = self.company_combo.currentText()
        W, H = 384, 120
        img = Image.new('RGB', (W, H), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        text = 'PUUILO'
        try:
            font = ImageFont.truetype('DejaVuSans-Bold.ttf', 72)
        except Exception:
            font = ImageFont.load_default()
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            tw, th = draw.textsize(text, font=font)
        x = (W - tw) / 2
        y = (H - th) / 2
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        from pathlib import Path
        logos_dir = Path('templates/logos')
        logos_dir.mkdir(parents=True, exist_ok=True)
        out_name = 'puuilo_auto.png'
        out_path = logos_dir / out_name
        img.save(str(out_path))
        ok = self.template_manager.save_logo_file(company_name, out_name)
        if ok:
            if self.current_template:
                self.current_template.logo = ''
                self.current_template.logo_image = str(out_path)
            self.update_preview_force()
            QMessageBox.information(self, 'OK', f'Generated logo set for {company_name}.')
        else:
            QMessageBox.warning(self, 'Error', 'Failed to update template with new logo.')

    def _generate_banner_logo(self, text: str, bg_rgb: tuple, fg_rgb: tuple, filename: str):
        try:
            from PIL import Image, ImageDraw, ImageFont
        except Exception:
            QMessageBox.warning(self, 'Pillow missing', 'Pillow not installed; cannot generate image.')
            return False
        W, H = 384, 120
        img = Image.new('RGB', (W, H), color=bg_rgb)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype('DejaVuSans-Bold.ttf', 72)
        except Exception:
            font = ImageFont.load_default()
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            tw, th = draw.textsize(text, font=font)
        x = (W - tw) / 2
        y = (H - th) / 2
        draw.text((x, y), text, fill=fg_rgb, font=font)
        from pathlib import Path
        logos_dir = Path('templates/logos')
        logos_dir.mkdir(parents=True, exist_ok=True)
        out_path = logos_dir / filename
        img.save(str(out_path))
        company_name = self.company_combo.currentText()
        ok = self.template_manager.save_logo_file(company_name, filename)
        if ok:
            if self.current_template:
                self.current_template.logo = ''
                self.current_template.logo_image = str(out_path)
            self.update_preview_force()
            QMessageBox.information(self, 'OK', f'Generated logo set for {company_name}.')
            return True
        else:
            QMessageBox.warning(self, 'Error', 'Failed to update template with new logo.')
            return False

    def generate_tokmanni_logo(self):
        # Tokmanni: white text on deep red background
        self._generate_banner_logo('TOKMANNI', (200, 0, 0), (255, 255, 255), 'tokmanni_auto.png')

    def generate_motonet_logo(self):
        # Motonet: white text on red background
        self._generate_banner_logo('MOTONET', (180, 0, 0), (255, 255, 255), 'motonet_auto.png')

    # --- Company info fetching ---
    def fetch_company_info(self):
        name = self.company_combo.currentText()
        if not name or not self.current_template:
            return
        if not requests or not BeautifulSoup:
            QMessageBox.warning(self, 'Missing deps', 'Install requests and beautifulsoup4 to use auto-fetch.')
            return

        self.fetch_info_btn.setEnabled(False)
        self.fetch_info_btn.setText('Fetching…')

        def worker():
            try:
                info = self._scrape_company_info(name)
            except Exception as e:
                info = None
                logging.exception(e)
            def finalize():
                self.fetch_info_btn.setEnabled(True)
                self.fetch_info_btn.setText('Fetch company info')
                if not info:
                    QMessageBox.warning(self, 'No data', 'Could not fetch company info.')
                    return
                # Update template in memory
                self.current_template.company_info.update(info)
                self.update_preview_force()
                # Ask to persist
                res = QMessageBox.question(self, 'Save', 'Save company info into template file?')
                if res == QMessageBox.Yes:
                    ok = self.template_manager.save_company_info(name, info)
                    if ok:
                        QMessageBox.information(self, 'Saved', 'Company info saved.')
                    else:
                        QMessageBox.warning(self, 'Error', 'Failed to save template.')
            QTimer.singleShot(0, finalize)

        threading.Thread(target=worker, daemon=True).start()

    def _scrape_company_info(self, name: str) -> dict:
        # Known domains for chains
        domains = {
            'puuilo': 'https://www.puuilo.fi',
            'tokmanni': 'https://www.tokmanni.fi',
            'motonet': 'https://www.motonet.fi',
        }
        base = None
        for key, dom in domains.items():
            if key in name.lower():
                base = dom
                break
        candidates = []
        if base:
            candidates = [
                base,
                base + '/yhteystiedot',
                base + '/asiakaspalvelu',
                base + '/contact',
                base + '/yritys',
            ]
        else:
            # Fallback search via DuckDuckGo HTML to avoid JS
            q = requests.utils.quote(f"{name} yhteystiedot")
            candidates = [f"https://duckduckgo.com/html/?q={q}"]

        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
        html = ''
        url_found = None
        for url in candidates:
            try:
                r = requests.get(url, headers=headers, timeout=20)
                if r.status_code == 200:
                    if 'duckduckgo.com' in url:
                        soup = BeautifulSoup(r.text, 'html.parser')
                        a = soup.select_one('a.result__a, a.result__url')
                        if a and a.get('href'):
                            url_found = a.get('href')
                            rr = requests.get(url_found, headers=headers, timeout=20)
                            if rr.status_code == 200:
                                html = rr.text
                                break
                    else:
                        html = r.text
                        url_found = url
                        break
            except Exception:
                continue
        if not html:
            return {}
        soup = BeautifulSoup(html, 'html.parser')
        text = ' '\
            .join(x.get_text(" ", strip=True) for x in soup.find_all(['p','li','div','span']))
        # Phone regex (Finnish)
        m_phone = re.search(r'(\+358\s?\d[\d\s\-]{5,15}|0\d[\d\s\-]{5,15})', text)
        phone = m_phone.group(0) if m_phone else ''
        # Address: look for postal code pattern and preceding token
        m_addr = re.search(r'([A-Za-zÅÄÖåäö0-9\-\. ]+?)\s(\d{5}\s+[A-Za-zÅÄÖåäö\- ]+)', text)
        address = ''
        city = ''
        if m_addr:
            address = m_addr.group(1).strip()
            city = m_addr.group(2).strip()
        info = {}
        if address:
            info['address'] = address
        if city:
            info['city'] = city
        if phone:
            info['phone'] = phone
        return info

    # --- Nearest store via OSM ---
    def find_nearest_store(self):
        query = (self.find_store_input.text() or '').strip()
        name = self.company_combo.currentText()
        if not query or not name or not requests:
            return
        self.find_store_btn.setEnabled(False)
        self.find_store_btn.setText('Searching…')

        def worker():
            result = None
            try:
                loc = self._geocode(query)
                if loc:
                    # 1) Try chain-specific store list scraping
                    scraped = self._scrape_chain_stores(name)
                    if scraped:
                        nearest = self._nearest_from_scraped(scraped, loc['lat'], loc['lon'])
                        if nearest:
                            result = nearest
                    # 2) Fallback to OSM Overpass
                    if not result:
                        stores = self._overpass_find_stores(name, loc['lat'], loc['lon'])
                        if stores:
                            stores.sort(key=lambda s: s.get('dist', 1e9))
                            result = stores[0]
            except Exception as e:
                logging.exception(e)

            def finalize():
                self.find_store_btn.setEnabled(True)
                self.find_store_btn.setText('Find nearest store')
                if not result:
                    QMessageBox.warning(self, 'No match', 'Store not found nearby.')
                    return
                street = result.get('addr:street', '')
                hn = result.get('addr:housenumber', '')
                postcode = result.get('addr:postcode', '')
                city = result.get('addr:city', '') or result.get('addr:town', '') or result.get('addr:village', '')
                phone = result.get('contact:phone') or result.get('phone') or ''

                address_line = (street + (' ' + hn if hn else '')).strip()
                city_line = (' '.join([postcode, city])).strip()

                info = {}
                if address_line:
                    info['address'] = address_line
                if city_line:
                    info['city'] = city_line
                if phone:
                    info['phone'] = phone

                if not info:
                    QMessageBox.information(self, 'Result', 'Found store, but no address tags in OSM.')
                    return
                # Update current template and preview
                self.current_template.company_info.update(info)
                self.update_preview_force()
                # Offer save to template file
                res = QMessageBox.question(self, 'Save', 'Save store info into template file?')
                if res == QMessageBox.Yes:
                    ok = self.template_manager.save_company_info(name, info)
                    if ok:
                        QMessageBox.information(self, 'Saved', 'Store info saved.')
            QTimer.singleShot(0, finalize)

        threading.Thread(target=worker, daemon=True).start()

    def _geocode(self, text: str):
        headers = {'User-Agent': 'AnomReceipt/1.0 (geocode)'}
        params = {'format': 'json', 'q': text, 'limit': 1, 'accept-language': 'fi', 'countrycodes': 'fi'}
        r = requests.get('https://nominatim.openstreetmap.org/search', params=params, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
        arr = r.json()
        if not arr:
            return None
        return {'lat': float(arr[0]['lat']), 'lon': float(arr[0]['lon'])}

    def _scrape_chain_stores(self, chain_name: str):
        if not requests or not BeautifulSoup:
            return []
        chain = chain_name.lower()
        sources = []
        if 'puuilo' in chain:
            sources = ['https://www.puuilo.fi/myymalat', 'https://www.puuilo.fi/yhteystiedot']
        elif 'tokmanni' in chain:
            sources = ['https://www.tokmanni.fi/myymalat', 'https://www.tokmanni.fi/yhteystiedot']
        elif 'motonet' in chain:
            sources = ['https://www.motonet.fi/kaupat', 'https://www.motonet.fi/yritys']
        headers = {'User-Agent': 'AnomReceipt/1.0 (store-scrape)'}
        stores = []
        for url in sources:
            try:
                r = requests.get(url, headers=headers, timeout=12)
                if r.status_code != 200:
                    continue
                soup = BeautifulSoup(r.text, 'html.parser')
                text = '\n'.join(x.get_text(' ', strip=True) for x in soup.find_all(['p','li','div','span','a']))
                # Very simple pattern: lines containing Finnish postal code
                matches = re.findall(r'([A-Za-zÅÄÖåäö0-9\-\. ]+?)\s(\d{5})\s+([A-Za-zÅÄÖåäö\- ]+)', text)
                for m in matches:
                    street = m[0].strip()
                    postcode = m[1].strip()
                    city = m[2].strip()
                    # Try to find a phone near match
                    phone_match = re.search(r'(\+358\s?\d[\d\s\-]{5,15}|0\d[\d\s\-]{5,15})', text)
                    phone = phone_match.group(0) if phone_match else ''
                    stores.append({'addr:street': street, 'addr:postcode': postcode, 'addr:city': city, 'phone': phone})
                if stores:
                    break
            except Exception:
                continue
        return stores

    def _nearest_from_scraped(self, stores, lat, lon):
        # Geocode at most 8 stores to keep usage light
        best = None
        headers = {'User-Agent': 'AnomReceipt/1.0 (geocode)'}
        for s in stores[:8]:
            addr = (s.get('addr:street') or '')
            pc = s.get('addr:postcode') or ''
            city = s.get('addr:city') or ''
            q = ' '.join(filter(None, [addr, pc, city, 'Suomi']))
            try:
                r = requests.get('https://nominatim.openstreetmap.org/search', params={'format':'json','q':q,'limit':1,'countrycodes':'fi'}, headers=headers, timeout=10)
                if r.status_code != 200:
                    continue
                arr = r.json()
                if not arr:
                    continue
                slat, slon = float(arr[0]['lat']), float(arr[0]['lon'])
                dist = self._haversine(lat, lon, slat, slon)
                t = dict(s)
                t['dist'] = dist
                if not best or dist < best.get('dist', 1e9):
                    best = t
            except Exception:
                continue
        return best

    def _overpass_find_stores(self, chain_name: str, lat: float, lon: float):
        headers = {'User-Agent': 'AnomReceipt/1.0 (overpass)'}
        safe = chain_name.replace('"', '\\"')
        radius = 50000  # 50km
        query = f"""
        [out:json][timeout:25];
        (
          node["name"~"{safe}",i](around:{radius},{lat},{lon});
          way["name"~"{safe}",i](around:{radius},{lat},{lon});
          relation["name"~"{safe}",i](around:{radius},{lat},{lon});
        );
        out center tags;
        """
        endpoints = [
            'https://overpass-api.de/api/interpreter',
            'https://overpass.kumi.systems/api/interpreter',
            'https://overpass.openstreetmap.ru/api/interpreter'
        ]
        data = None
        for ep in endpoints:
            try:
                r = requests.post(ep, data=query.encode('utf-8'), headers=headers, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    break
            except requests.exceptions.RequestException:
                continue
        if not data:
            return []
        elems = data.get('elements', [])
        stores = []
        for e in elems:
            tags = e.get('tags', {})
            if not tags:
                continue
            # Use center for ways/relations
            clat = e.get('lat') or (e.get('center') or {}).get('lat')
            clon = e.get('lon') or (e.get('center') or {}).get('lon')
            if not (clat and clon):
                continue
            dist = self._haversine(lat, lon, float(clat), float(clon))
            # Keep only stores matching chain brand strongly when possible
            nm = (tags.get('brand') or tags.get('name') or '').lower()
            if any(k in nm for k in chain_name.lower().split()):
                tags_copy = dict(tags)
                tags_copy['dist'] = dist
                stores.append(tags_copy)
        return stores

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
        
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

        # Editing toolbar below preview
        tool_row = QHBoxLayout()
        self.edit_toggle = QPushButton('Edit')
        self.edit_toggle.setCheckable(True)
        self.edit_toggle.toggled.connect(lambda v: self.preview_text.setReadOnly(not v))
        tool_row.addWidget(self.edit_toggle)

        self.regen_btn = QPushButton('Päivitä kuitti')
        self.regen_btn.clicked.connect(self.update_preview_force)
        tool_row.addWidget(self.regen_btn)

        self.save_btn = QPushButton('Save preview')
        self.save_btn.clicked.connect(self.save_preview)
        tool_row.addWidget(self.save_btn)

        self.load_btn = QPushButton('Load preview')
        self.load_btn.clicked.connect(self.load_preview)
        tool_row.addWidget(self.load_btn)

        tool_row.addStretch()
        layout.addLayout(tool_row)

        # Default to editable preview for freeform editing
        self.edit_toggle.setChecked(True)
        
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
        low = (company_name or '').lower()
        if hasattr(self, 'gen_logo_puuilo_btn'):
            self.gen_logo_puuilo_btn.setVisible('puuilo' in low)
        if hasattr(self, 'gen_logo_tokmanni_btn'):
            self.gen_logo_tokmanni_btn.setVisible('tokmanni' in low)
        if hasattr(self, 'gen_logo_motonet_btn'):
            self.gen_logo_motonet_btn.setVisible('motonet' in low)
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
        
    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self, self.translator, self.settings)
        
        if dialog.exec_() == QDialog.Accepted:
            self.settings = dialog.get_settings()
            self.update_preview()
            logger.info(f"Settings updated: {self.settings}")
            
    def open_logo_editor(self):
        """Open the logo editor dialog"""
        editor = LogoEditor(
            self, 
            self.translator,
            max_width=self.settings.get('logo_max_width', 48),
            max_height=self.settings.get('logo_max_height', 20)
        )
        
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
        # If user is editing manually, do not overwrite contents.
        if hasattr(self, 'edit_toggle') and self.edit_toggle.isChecked():
            return
        return self.update_preview_force()

    def update_preview_force(self):
        """Regenerate preview from current form data regardless of edit mode."""
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
        
        # Logo handling (PNG image + optional ASCII)
        img_html = ''
        if receipt_data.get('logo_image'):
            img_html = f"<div style='text-align:center'><img src='file://{receipt_data['logo_image']}' style='max-width:100%;height:auto' /></div>\n"
        if receipt_data.get('logo'):
            preview.append(receipt_data['logo'])
            preview.append('')
            
        # Header
        if receipt_data.get('header'):
            for line in receipt_data['header']:
                preview.append(line)
                
        # Items
        receipt_width = self.settings.get('receipt_width', 48)
        separator_line = '-' * receipt_width
        
        preview.append(separator_line)
        if receipt_data.get('items'):
            for item in receipt_data['items']:
                name = item.get('name', '')
                price = item.get('price', '')
                qty = item.get('qty', '')

                base = f"{qty}x {name}" if qty else name
                # Ensure price is right-aligned at configured width. If content too long,
                # truncate left part to keep the price visible.
                if receipt_width > len(price):
                    left_space = receipt_width - len(price)
                    left = base[:left_space].ljust(left_space)
                    line = left + price
                else:
                    # Fallback: just cut to width
                    line = (base + ' ' + price)[:receipt_width]

                preview.append(line)
                
        preview.append(separator_line)
        
        # Footer
        if receipt_data.get('footer'):
            for line in receipt_data['footer']:
                preview.append(line)
        
        # Visa transaction details if selected
        if self.payment_combo.currentText().lower() == 'visa':
            from random import randint, choice
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
            preview.extend([
                '',
                f"Card: VISA",
                f"PAN: **** **** **** {last4}",
                f"Expiry: {expiry}",
                f"Auth: {auth}",
                f"AID: A0000000031010",
                f"App: VISA CREDIT",
                f"TVR: 0000000000",
                f"TSI: E800",
                f"Entry: {entry}",
                f"AC: {ac}",
                f"RRN: {rrn}",
                f"STAN: {stan}",
                f"TransID: {trans_id}",
                f"TID: {term_id}",
                f"MID: {mid}",
            ])
                
        # Wrap all lines to width
        wrapped = []
        for ln in preview:
            if len(ln) <= receipt_width:
                wrapped.append(ln)
            else:
                i = 0
                while i < len(ln):
                    wrapped.append(ln[i:i+receipt_width])
                    i += receipt_width

        # Render HTML with image + preformatted text for alignment
        # Handle barcode markup by converting to visual representation
        escaped_lines = []
        for line in wrapped:
            # Check for barcode markup: >BARCODE TYPE DATA>
            if line.strip().startswith('>BARCODE '):
                # Parse barcode using shared pattern
                match = re.match(BARCODE_MARKUP_PATTERN, line.strip())
                if match:
                    bc_type = match.group(1)
                    bc_data = match.group(2)
                    remaining = match.group(3)
                    # Create visual barcode representation for preview
                    # Use a simple ASCII art representation
                    barcode_visual = f"[BARCODE {bc_type}: {bc_data}]"
                    barcode_visual = barcode_visual.center(receipt_width)
                    # Add visual bars with limited width
                    # Limit bar count to avoid excessive width (max 20 bars)
                    bar_count = min(len(bc_data), 20)
                    bars = '|' + '| ' * bar_count + '|'
                    bars = bars.center(receipt_width)
                    escaped_lines.append(bars)
                    escaped_lines.append(barcode_visual)
                    if remaining:
                        escaped_lines.append(remaining.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
                    continue
            
            # Regular line - escape HTML
            escaped_lines.append(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
        
        escaped = '\n'.join(escaped_lines)
        html = img_html + f"<pre style=\"font-family:'Courier New',monospace; font-size:12px; white-space: pre;\">{escaped}</pre>"
        self.preview_text.setHtml(html)

    def save_preview(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        path, _ = QFileDialog.getSaveFileName(self, 'Save preview', '', 'Text Files (*.txt);;All Files (*)')
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.preview_text.toPlainText())
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save: {e}')

    def load_preview(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        path, _ = QFileDialog.getOpenFileName(self, 'Load preview', '', 'Text Files (*.txt);;All Files (*)')
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.preview_text.setPlainText(f.read())
            # enter edit mode so we don't auto-overwrite
            self.edit_toggle.setChecked(True)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load: {e}')
        
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
            
        # If user is editing preview, print exactly what's shown
        if hasattr(self, 'edit_toggle') and self.edit_toggle.isChecked():
            # Get HTML to preserve formatting (bold, italic, font size)
            html_content = self.preview_text.toHtml()
            
            # Print using rich HTML method which preserves formatting
            ok = self.printer.print_rich_html(html_content)
            
            if ok:
                QMessageBox.information(self, self.translator.translate('success'),
                                      self.translator.translate('print_success'))
            else:
                QMessageBox.warning(self, self.translator.translate('error'),
                                  self.translator.translate('print_error'))
            return

        # Otherwise generate from current form
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

        width = self.settings.get('receipt_width', 48)
        if self.printer.print_receipt(receipt_data, width=width):
            QMessageBox.information(self, self.translator.translate('success'),
                                  self.translator.translate('print_success'))
        else:
            QMessageBox.warning(self, self.translator.translate('error'),
                              self.translator.translate('print_error'))
