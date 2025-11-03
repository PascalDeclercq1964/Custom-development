from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Veld om de gelinkte verkoopfactuur op te slaan
    # Dit is een Many2one relatie naar een andere account.move (de verkoopfactuur)
    x_resell_move_id = fields.Many2one(
        'account.move',
        string='Doorgefactureerde Verkoopfactuur',
        copy=False, # Zorg ervoor dat dit veld niet wordt gekopieerd bij duplicatie
        readonly=True, # Dit veld wordt automatisch ingevuld door de wizard
        help="De verkoopfactuur die is gegenereerd uit deze aankoopfactuur."
    )

    # Veld om aan te geven of de aankoopfactuur is doorgefactureerd
    x_is_reselled = fields.Boolean(
        string='Is Doorgefactureerd',
        compute='_compute_is_reselled',
        store=True, # Opslaan in de database voor sneller zoeken/filteren
        help="Geeft aan of deze aankoopfactuur al is doorgefactureerd."
    )

    @api.depends('x_resell_move_id')
    def _compute_is_reselled(self):
        for record in self:
            record.x_is_reselled = bool(record.x_resell_move_id)