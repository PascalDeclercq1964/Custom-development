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
        'security/ir.model.access.csv', # Wordt later toegevoegd voor rechten
        'wizards/purchase_resell_wizard_views.xml', # Wordt later toegevoegd
        'views/account_move_views.xml', # Wordt later toegevoegd
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}