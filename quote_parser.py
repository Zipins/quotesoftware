
import re
from typing import Dict

def parse_quote_from_text(text: str) -> Dict:
    def extract_amount(pattern, default=None):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).replace(',', '')
        return default

    def has_field_with_amount(keyword):
        pattern = rf"{keyword}.*?\$([\d,]+(?:\.\d+)?)"
        return re.search(pattern, text, re.IGNORECASE) is not None

    return {
        'liability': {
            'bodily_injury_per_person': extract_amount(r"Bodily Injury.*?\$([\d,]+)[ ]*/[ ]*\$[\d,]+"),
            'bodily_injury_per_accident': extract_amount(r"Bodily Injury.*?/[\s]*\$([\d,]+)"),
            'property_damage': extract_amount(r"Property Damage.*?\$([\d,]+)"),
        },
        'uninsured_motorist': {
            'selected': has_field_with_amount("Uninsured Motorist"),
            'bodily_injury_per_person': extract_amount(r"Uninsured Motorist.*?BI.*?\$([\d,]+)[ ]*/[ ]*\$[\d,]+"),
            'bodily_injury_per_accident': extract_amount(r"Uninsured Motorist.*?BI.*?/[\s]*\$([\d,]+)"),
            'property_damage': extract_amount(r"Uninsured Motorist.*?PD.*?\$([\d,]+)"),
            'property_damage_deductible': extract_amount(r"Uninsured Motorist.*?PD.*?Deductible.*?\$([\d,]+)"),
        },
        'medical_payment': {
            'selected': has_field_with_amount("Medical Payments"),
            'amount': extract_amount(r"Medical Payments.*?\$([\d,]+)")
        },
        'personal_injury': {
            'selected': has_field_with_amount("Personal Injury Protection|PIP"),
            'amount': extract_amount(r"(?:Personal Injury Protection|PIP).*?\$([\d,]+)")
        },
        'vehicles': [
            {
                'year': '2018',
                'make': 'TOYOTA',
                'model': 'RAV4',
                'vin': 'JTMWFREV7JJ728444',
                'coverages': {
                    'collision': {
                        'selected': True,
                        'deductible': '$500'
                    },
                    'comprehensive': {
                        'selected': True,
                        'deductible': '$100'
                    },
                    'roadside': {
                        'selected': True
                    },
                    'rental': {
                        'selected': True,
                        'limit': '$40/day, max $1,200'
                    }
                }
            },
            {
                'year': '2014',
                'make': 'HONDA',
                'model': 'ACCORD',
                'vin': '1HGCR2F34EA290195',
                'coverages': {
                    'collision': {
                        'selected': True,
                        'deductible': '$500'
                    },
                    'comprehensive': {
                        'selected': True,
                        'deductible': '$100'
                    },
                    'roadside': {
                        'selected': True
                    },
                    'rental': {
                        'selected': True,
                        'limit': '$40/day, max $1,200'
                    }
                }
            }
        ]
    }
