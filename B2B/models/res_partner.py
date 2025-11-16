from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_is_b2b_blocked = fields.Boolean(
        string='Geblokkeerd voor B2B',
        default=False,
        help="Vink aan om deze partner te blokkeren als B2B klant."
    )