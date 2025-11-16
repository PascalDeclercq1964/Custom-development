from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_is_b2b_blocked = fields.Boolean(
        string='B2B Prijzen Geblokkeerd',
        default=False,
        help="Vink aan om deze partner te blokkeren voor B2B-prijzen, ongeacht de toegewezen prijslijst."
    )