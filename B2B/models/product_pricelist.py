from odoo import fields, models

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    # Veld om aan te geven of de prijslijst B2B is
    x_is_b2b_pricelist = fields.Boolean(
        string='Is B2B Prijslijst',
        default=False,
        help="Vink dit aan als deze prijslijst bedoeld is voor Business-to-Business klanten."
    )