"""
Sample company profiles for the receipt printing application.
"""
from models import CompanyProfile


# Company 1: Heavy Machinery
HARJUN_RASKASKONE = CompanyProfile(
    name="Harjun Raskaskone Oy",
    address="Teollisuustie 42",
    postal_code="33100",
    city="Tampere",
    country="Finland",
    vat_id="FI12345678",
    phone="+358 3 1234 5678",
    email="info@harjunraskaskone.fi",
    website="www.harjunraskaskone.fi",
    default_language="FI",
    default_currency="EUR",
    default_footer_fi="Takuu 12kk - Huolto ja varaosat",
    default_footer_en="12 months warranty - Service and spare parts",
    logo_file="harjun_raskaskone.txt"
)


# Company 2: E-Bike Service
HELSINKI_EBIKE = CompanyProfile(
    name="Helsinki eBike Service Oy",
    address="Pyöräkatu 15",
    postal_code="00100",
    city="Helsinki",
    country="Finland",
    vat_id="FI23456789",
    phone="+358 9 8765 4321",
    email="service@helsinkiebike.fi",
    website="www.helsinkiebike.fi",
    default_language="FI",
    default_currency="EUR",
    default_footer_fi="Sähköpyörien asiantuntija - Tervetuloa uudelleen!",
    default_footer_en="E-Bike specialist - Welcome back!",
    logo_file="helsinki_ebike.txt"
)


# Company 3: IT/Cyber
JUGISYSTEMS = CompanyProfile(
    name="JugiSystems",
    address="Kyberpolku 7",
    postal_code="02150",
    city="Espoo",
    country="Finland",
    vat_id="FI34567890",
    phone="+358 50 123 4567",
    email="info@jugisystems.fi",
    website="www.jugisystems.fi",
    default_language="EN",
    default_currency="EUR",
    default_footer_fi="IT-ratkaisut yrityksille - 24/7 tuki",
    default_footer_en="IT solutions for businesses - 24/7 support",
    logo_file="jugisystems.txt"
)


# Company 4: Generic Retail Store 1
RETAIL_STORE_1 = CompanyProfile(
    name="Lähikauppa Mäkelä",
    address="Kauppatie 3",
    postal_code="00200",
    city="Helsinki",
    country="Finland",
    vat_id="FI45678901",
    phone="+358 9 1111 2222",
    email="makela@lahikauppa.fi",
    default_language="FI",
    default_currency="EUR",
    default_footer_fi="Kiitos ostoksista! Tervetuloa uudelleen!",
    default_footer_en="Thank you for shopping! Welcome back!",
    logo_file=None
)


# Company 5: Generic Retail Store 2
RETAIL_STORE_2 = CompanyProfile(
    name="Oulu Marketplace",
    address="Markettikatu 21",
    postal_code="90100",
    city="Oulu",
    country="Finland",
    vat_id="FI56789012",
    phone="+358 8 3333 4444",
    email="info@oulumarketplace.fi",
    default_language="FI",
    default_currency="EUR",
    default_footer_fi="Avoinna ma-pe 8-20, la 10-18",
    default_footer_en="Open Mon-Fri 8-20, Sat 10-18",
    logo_file=None
)


# Dictionary of all companies
COMPANIES = {
    "Harjun Raskaskone Oy": HARJUN_RASKASKONE,
    "Helsinki eBike Service Oy": HELSINKI_EBIKE,
    "JugiSystems": JUGISYSTEMS,
    "Lähikauppa Mäkelä": RETAIL_STORE_1,
    "Oulu Marketplace": RETAIL_STORE_2,
}


def get_company(name: str) -> CompanyProfile:
    """Get company profile by name."""
    return COMPANIES.get(name)


def get_company_names() -> list:
    """Get list of all company names."""
    return list(COMPANIES.keys())
