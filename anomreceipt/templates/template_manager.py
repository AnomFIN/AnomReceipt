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
    
    def __init__(self, name, company_info, payment_methods, logo=None):
        self.name = name
        self.company_info = company_info
        self.payment_methods = payment_methods
        self.logo = logo or ""
        
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
            
        receipt['header'].append('')
        receipt['header'].append(datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
        receipt['header'].append('')
        
        # Items section
        receipt['items'] = items
        
        # Calculate totals
        total = sum(float(item.get('price', '0').replace('€', '').strip()) for item in items)
        subtotal = total / 1.24  # Assuming 24% VAT
        vat = total - subtotal
        
        # Footer with totals
        receipt['footer'].append('')
        
        subtotal_label = 'Veroton yhteensä:' if language == 'FI' else 'Subtotal:'
        vat_label = 'ALV 24%:' if language == 'FI' else 'VAT 24%:'
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
        
        # Thank you message
        if language == 'FI':
            receipt['footer'].append('Kiitos!')
        else:
            receipt['footer'].append('Thank you!')
            
        return receipt


class TemplateManager:
    """Manages receipt templates"""
    
    def __init__(self, templates_dir='templates/companies'):
        self.templates_dir = Path(templates_dir)
        self.templates = {}
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
                    
            # Load logo if specified
            logo = ""
            if data.get('logo_file'):
                logo_path = Path('templates/logos') / data['logo_file']
                if logo_path.exists():
                    with open(logo_path, 'r', encoding='utf-8') as lf:
                        logo = lf.read()
                        
            return ReceiptTemplate(
                name=data.get('name', file_path.stem),
                company_info=data.get('company_info', {}),
                payment_methods=data.get('payment_methods', {}),
                logo=logo
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
