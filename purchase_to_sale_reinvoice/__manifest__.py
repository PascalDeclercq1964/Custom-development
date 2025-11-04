{
    'name': 'Purchase Invoice Resell',
    'version': '1.0',
    'summary': 'Module to resell purchase invoices to a fixed customer.',
    'description': """
        This module adds functionality to resell selected purchase invoices
        to a predefined customer. It includes account and tax mapping,
        and a link to the generated sales invoice.
    """,
    'author': 'Pascal Declercq', 
    'category': 'Accounting/Purchase',
    'depends': [
        'account', # Essentieel voor facturatie
        'purchase', # Essentieel voor aankoop
    ],
    'data': [
        'data/server_action.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}