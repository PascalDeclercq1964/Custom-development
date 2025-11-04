from odoo import fields, models

class AccountAccount(models.Model):
    _inherit = 'account.account'

    # Veld om de Verkooprekening voor doorfacturatie direct vast te leggen
    x_resell_sale_account_id = fields.Many2one(
        'account.account',
        string='Doorgefactureerde Verkooprekening',
        domain=[('internal_group', '=', 'income')], # Zorg dat het een verkooprekening is
        help="De verkooprekening die gebruikt moet worden bij doorfacturatie van aankoopfacturen die deze rekening gebruiken."
    )