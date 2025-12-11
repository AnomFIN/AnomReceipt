"""
Template management system for receipt generation
Supports JSON and YAML formats
"""

import json
import yaml
import os
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReceiptTemplate:
    """Represents a receipt template"""
    
    # Default VAT rate (24% for Finland, configurable per template)
    DEFAULT_VAT_RATE = 0.24
    
    def __init__(self, name, company_info, payment_methods, logo=None, vat_rate=None, logo_image=None):
        self.name = name
        self.company_info = company_info
        self.payment_methods = payment_methods
        self.logo = logo or ""
        self.logo_image = logo_image  # file path to PNG/JPEG
        self.vat_rate = vat_rate if vat_rate is not None else self.DEFAULT_VAT_RATE
        
    def generate_receipt(self, items, payment_method, language='EN', customer_info=None):
        """
        Generate receipt data from template and transaction data
        
        Args:
            items: List of items with name, price, qty
            payment_method: Payment method used (cash, card, mobilepay, bank)
            language: Language code (FI/EN)
            customer_info: Optional customer information
            
        Returns:
            Dictionary with receipt data ready for printing
        """
        receipt = {
            'logo': self.logo,
            'logo_image': self.logo_image,
            'header': [],
            'items': [],
            'footer': [],
            'cut': True
        }
        
        # Company header
        receipt['header'].append(self.company_info.get('name', ''))
        if self.company_info.get('address'):
            receipt['header'].append(self.company_info['address'])
        if self.company_info.get('city'):
            receipt['header'].append(self.company_info['city'])
        if self.company_info.get('vat_id'):
            vat_label = 'Y-tunnus:' if language == 'FI' else 'VAT ID:'
            receipt['header'].append(f"{vat_label} {self.company_info['vat_id']}")
        if self.company_info.get('phone'):
            phone_label = 'Puh:' if language == 'FI' else 'Phone:'
            receipt['header'].append(f"{phone_label} {self.company_info['phone']}")
        # Opening hours if available
        oh = self.company_info.get('opening_hours')
        if oh:
            receipt['header'].append('')
            hours_title = 'Aukioloajat' if language == 'FI' else 'Opening hours'
            receipt['header'].append(hours_title)
            if isinstance(oh, list):
                for line in oh[:7]:
                    receipt['header'].append(line)
            elif isinstance(oh, str):
                for line in oh.splitlines()[:7]:
                    receipt['header'].append(line)
            
        receipt['header'].append('')
        receipt['header'].append(datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
        receipt['header'].append('')
        
        # Items section
        receipt['items'] = items
        
        # Calculate totals
        total = sum(float(item.get('price', '0').replace('€', '').strip()) for item in items)
        subtotal = total / (1 + self.vat_rate)
        vat = total - subtotal
        
        # Footer with totals
        receipt['footer'].append('')
        
        vat_percent = int(self.vat_rate * 100)
        subtotal_label = 'Veroton yhteensä:' if language == 'FI' else 'Subtotal:'
        vat_label = f'ALV {vat_percent}%:' if language == 'FI' else f'VAT {vat_percent}%:'
        total_label = 'YHTEENSÄ:' if language == 'FI' else 'TOTAL:'
        payment_label = 'Maksutapa:' if language == 'FI' else 'Payment:'
        
        receipt['footer'].append(f"{subtotal_label:<30} {subtotal:>6.2f}€")
        receipt['footer'].append(f"{vat_label:<30} {vat:>6.2f}€")
        receipt['footer'].append(f"{total_label:<30} {total:>6.2f}€")
        receipt['footer'].append('')
        
        # Payment method
        payment_text = self.payment_methods.get(payment_method, {}).get(language, payment_method)
        receipt['footer'].append(f"{payment_label} {payment_text}")
        receipt['footer'].append('')
        
        # Thank you messages
        if language == 'FI':
            receipt['footer'].append('Kiitos käynnistä!')
            receipt['footer'].append('Tervetuloa uudelleen!')
        else:
            receipt['footer'].append('Thank you for your visit!')
            receipt['footer'].append('Welcome again!')
            
        return receipt


class TemplateManager:
    """Manages receipt templates"""
    
    def __init__(self, templates_dir='templates/companies'):
        self.templates_dir = Path(templates_dir)
        self.templates = {}
        self.template_files = {}
        self.load_templates()
        
    def load_templates(self):
        """Load all templates from the templates directory"""
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return
            
        for file_path in self.templates_dir.glob('*'):
            if file_path.suffix in ['.json', '.yaml', '.yml']:
                try:
                    template = self.load_template_file(file_path)
                    if template:
                        self.templates[template.name] = template
                        self.template_files[template.name] = file_path
                        logger.info(f"Loaded template: {template.name}")
                except Exception as e:
                    logger.error(f"Error loading template {file_path}: {e}")
                    
    def load_template_file(self, file_path):
        """Load a single template file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix == '.json':
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)
                    
            # Load logo if specified (.txt as ASCII or .png/.jpg as image path)
            logo = ""
            logo_image = None
            if data.get('logo_file'):
                logo_path = Path('templates/logos') / data['logo_file']
                if logo_path.exists():
                    if logo_path.suffix.lower() == '.txt':
                        with open(logo_path, 'r', encoding='utf-8') as lf:
                            logo = lf.read()
                    elif logo_path.suffix.lower() in ('.png', '.jpg', '.jpeg'):
                        logo_image = str(logo_path)
                        
            return ReceiptTemplate(
                name=data.get('name', file_path.stem),
                company_info=data.get('company_info', {}),
                payment_methods=data.get('payment_methods', {}),
                logo=logo,
                vat_rate=data.get('vat_rate'),  # Optional VAT rate override
                logo_image=logo_image,
            )
        except Exception as e:
            logger.error(f"Error loading template file {file_path}: {e}")
            return None
            
    def get_template(self, name):
        """Get a template by name"""
        return self.templates.get(name)
        
    def list_templates(self):
        """List all available template names"""
        return list(self.templates.keys())
        
    def save_template(self, template, file_format='yaml'):
        """Save a template to file"""
        filename = f"{template.name}.{file_format}"
        file_path = self.templates_dir / filename
        
        data = {
            'name': template.name,
            'company_info': template.company_info,
            'payment_methods': template.payment_methods
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_format == 'json':
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                    
            self.templates[template.name] = template
            logger.info(f"Saved template: {template.name}")
            return True
        except Exception as e:
            logger.error(f"Error saving template: {e}")
            return False

    def save_company_info(self, name: str, company_info: dict) -> bool:
        """Persist updated company_info back to its template file."""
        file_path = self.template_files.get(name)
        if not file_path:
            logger.error(f"Template file not found for {name}")
            return False

    def save_logo_file(self, name: str, logo_filename: str) -> bool:
        """Persist logo_file (PNG/TXT) at template top-level and update in-memory logo/image."""
        file_path = self.template_files.get(name)
        if not file_path:
            logger.error(f"Template file not found for {name}")
            return False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f) if file_path.suffix == '.json' else yaml.safe_load(f)
            data['logo_file'] = logo_filename
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.suffix == '.json':
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            # Update in-memory template
            tpl = self.templates.get(name)
            if tpl:
                from pathlib import Path as _P
                p = _P('templates/logos') / logo_filename
                tpl.logo = ''
                tpl.logo_image = str(p) if p.exists() else None
            return True
        except Exception as e:
            logger.error(f"Error saving logo_file to template {file_path}: {e}")
            return False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f) if file_path.suffix == '.json' else yaml.safe_load(f)
            if 'company_info' not in data:
                data['company_info'] = {}
            data['company_info'].update({k: v for k, v in company_info.items() if v})
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.suffix == '.json':
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            # Update in-memory too
            tpl = self.templates.get(name)
            if tpl:
                tpl.company_info.update({k: v for k, v in company_info.items() if v})
            return True
        except Exception as e:
            logger.error(f"Error saving company info to template {file_path}: {e}")
            return False
