# mijn_b2b_aanpassingen/__manifest__.py

{
    'name': 'Mijn B2B E-commerce Aanpassingen',
    'summary': 'Implementeert B2B-specifieke logica zoals minimum bestelhoeveelheden en prijsverberging.',
    'version': '18.0.1.0.0',
    'category': 'Website/E-commerce',
    'license': 'LGPL-3',
    'depends': [
        'base', 
        'website_sale', # Essentieel, omdat we de templates van deze module overschrijven
        'sale', 
    ],
    'data': [
        # Laad de XML-bestanden die de QWeb overrides bevatten
        'views/templates.xml'
    ],
    'assets': {
        # Registreer het JavaScript bestand dat de knoppen-logica overschrijft
        'web.assets_frontend': [
            # Zorg ervoor dat dit na de originele website_sale.js laadt
            'mijn_b2b_aanpassingen/static/src/js/b2b_sale_qty.js',
        ],
    },
    'installable': True,
    'application': False,
}