from odoo import fields, models

class AccountTax(models.Model):
    _inherit = 'account.tax'

    # Veld om de Verkoop BTW Code voor doorfacturatie direct vast te leggen
    x_resell_sale_tax_id = fields.Many2one(
        'account.tax',
        string='Doorgefactureerde Verkoop BTW',
        domain=[('type_tax_use', '=', 'sale')], # Zorg dat het een verkoop BTW code is
        help="De verkoop BTW code die gebruikt moet worden bij doorfacturatie van aankoopfacturen die deze BTW code gebruiken."
    )