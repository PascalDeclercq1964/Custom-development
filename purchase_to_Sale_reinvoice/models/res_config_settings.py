from odoo import models, fields


class ResConfigSettings(models.TransientModel):
_inherit = 'res.config.settings'


reinvoice_partner_id = fields.Many2one(
'res.partner',
string='Reinvoice Customer',
config_parameter='purchase_to_sale_reinvoice.reinvoice_partner_id'
)