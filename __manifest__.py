{
    'name': 'Purchase to Sale Reinvoice',
    'version': '18.0.1.0.0',
    'summary': 'Mass-reinvoice vendor bills to one fixed customer',
    'author': 'Generated for user',
    'license': 'AGPL-3',
    'category': 'Accounting',
    'depends': ['base', 'purchase', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/reinvoice_views.xml',
    ],
    'installable': True,
    'application': False,
}