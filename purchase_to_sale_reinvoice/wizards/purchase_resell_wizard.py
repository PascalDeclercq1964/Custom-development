from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class PurchaseResellWizard(models.TransientModel):
    _name = 'purchase.resell.wizard'
    _description = 'Wizard to Resell Purchase Invoices'

    # Velden om de wizard te configureren
    partner_id = fields.Many2one(
        'res.partner',
        string='Vaste Klant',
        required=True,
        domain=[('customer_rank', '>', 0)], # Zorg dat het een klant is
        help="De vaste klant waarnaar de aankoopfacturen worden doorgefactureerd."
    )

    move_ids = fields.Many2many(
        'account.move',
        string='Geselecteerde Aankoopfacturen',
        readonly=True,
        help="De aankoopfacturen die zijn geselecteerd voor doorfacturatie."
    )

    # Mappings voor Grootboekrekeningen (een-op-veel relatie)
    account_map_ids = fields.One2many(
        'purchase.resell.account.map',
        'wizard_id',
        string='Grootboekrekening Mappings',
        help="Definieer hoe aankoop grootboekrekeningen worden gemapt naar verkooprekeningen."
    )

    # Mappings voor BTW Codes (een-op-veel relatie)
    tax_map_ids = fields.One2many(
        'purchase.resell.tax.map',
        'wizard_id',
        string='BTW Code Mappings',
        help="Definieer hoe aankoop BTW codes worden gemapt naar verkoop BTW codes."
    )

    # Wanneer de wizard wordt geladen, vullen we automatisch de mappings in
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            purchase_moves = self.env['account.move'].browse(active_ids)
            res['move_ids'] = [(6, 0, active_ids)] # Koppel de geselecteerde facturen aan de wizard

            # Verzamel unieke aankooprekeningen en btw-codes van de geselecteerde facturen
            unique_purchase_accounts = purchase_moves.invoice_line_ids.account_id.filtered(lambda a: a.internal_group == 'expense').ids
            unique_purchase_taxes = purchase_moves.invoice_line_ids.tax_ids.ids

            # Creëer standaard mappinglijnen voor grootboekrekeningen
            account_maps = []
            for acc_id in unique_purchase_accounts:
                account_maps.append((0, 0, {
                    'purchase_account_id': acc_id,
                    'sale_account_id': False, # Moet nog gekozen worden
                }))
            res['account_map_ids'] = account_maps

            # Creëer standaard mappinglijnen voor btw-codes
            tax_maps = []
            for tax_id in unique_purchase_taxes:
                tax_maps.append((0, 0, {
                    'purchase_tax_id': tax_id,
                    'sale_tax_id': False, # Moet nog gekozen worden
                }))
            res['tax_map_ids'] = tax_maps
        return res

    # Actie om de wizard te openen (wordt aangeroepen vanuit de server actie)
    def action_open_wizard(self):
        # Zorgt ervoor dat de wizard wordt geopend
        return {
            'name': 'Factureer Door Aankoopfacturen',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.resell.wizard',
            'views': [(False, 'form')],
            'target': 'new', # Opent in een pop-up
            'res_id': self.id,
        }

    # Validatie voor mappings
    @api.constrains('account_map_ids', 'tax_map_ids')
    def _check_mappings(self):
        for record in self:
            for acc_map in record.account_map_ids:
                if not acc_map.sale_account_id:
                    raise ValidationError("Alle aankoop grootboekrekeningen moeten gemapt worden naar een verkooprekening.")
            for tax_map in record.tax_map_ids:
                if not tax_map.sale_tax_id:
                    raise ValidationError("Alle aankoop BTW codes moeten gemapt worden naar een verkoop BTW code.")

    # Hoofdlogica voor het doorfactureren - wordt later geïmplementeerd
    def action_resell_invoices(self):
        self._check_mappings() # Valideer mappings voordat we verder gaan
        # De implementatie van het creëren van verkoopfacturen komt hier
        # Voor nu, return een actie om de wizard te sluiten en een notificatie te geven
        raise UserError("Doorfacturatie logica is nog niet geïmplementeerd. Mappings gevalideerd!")
        return {'type': 'ir.actions.act_window_close'}


class PurchaseResellAccountMap(models.TransientModel):
    _name = 'purchase.resell.account.map'
    _description = 'Mapping for Purchase to Sale Accounts in Resell Wizard'

    wizard_id = fields.Many2one('purchase.resell.wizard', string='Wizard', required=True, ondelete='cascade')
    purchase_account_id = fields.Many2one('account.account', string='Aankooprekening', readonly=True, required=True, domain=[('internal_group', '=', 'expense')])
    sale_account_id = fields.Many2one('account.account', string='Verkooprekening', required=True, domain=[('internal_group', '=', 'income')])

class PurchaseResellTaxMap(models.TransientModel):
    _name = 'purchase.resell.tax.map'
    _description = 'Mapping for Purchase to Sale Taxes in Resell Wizard'

    wizard_id = fields.Many2one('purchase.resell.wizard', string='Wizard', required=True, ondelete='cascade')
    purchase_tax_id = fields.Many2one('account.tax', string='Aankoop BTW Code', readonly=True, required=True, domain=[('type_tax_use', '=', 'purchase')])
    sale_tax_id = fields.Many2one('account.tax', string='Verkoop BTW Code', required=True, domain=[('type_tax_use', '=', 'sale')])