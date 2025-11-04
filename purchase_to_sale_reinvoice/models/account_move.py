from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.config import config # Nodig om de systeem parameters op te halen

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Veld om de link naar de aangemaakte verkoopfactuur vast te leggen (uit eerdere stappen)
    x_doorfactureer_move_id = fields.Many2one(
        'account.move', 
        string='Doorgefactureerd aan Verkoopfactuur', 
        readonly=True, 
        copy=False,
        help="Verwijzing naar de verkoopfactuur die is aangemaakt voor deze aankoopfactuur."
    )

    def action_resell_selected_invoices_with_config(self):
        """
        Maakt één verkoopfactuur aan uit de geselecteerde aankoopfacturen.
        Gebruikt de klant uit de Algemene Instellingen en de 1:1 mappings
        gedefinieerd op de bron Grootboekrekeningen en BTW Codes.
        """
        # We hoeven self.ensure_one() niet te gebruiken, omdat deze methode is ontworpen om
        # op een recordset (de geselecteerde facturen) te draaien via de Server Actie.

        # 1. HAAL CONFIGURATIE EN VALIDATIE OP
        
        # Haal de vaste klant ID op uit de Systeem Parameters
        config_partner_id = self.env['ir.config_parameter'].sudo().get_param(
            'purchase_to_sale_reinvoice.resell_partner_id'
        )
        if not config_partner_id:
            raise UserError("De 'Vaste Doorgefactureerde Klant' is niet ingesteld in de Instellingen. Gelieve deze in te vullen.")
            
        try:
            klant = self.env['res.partner'].browse(int(config_partner_id))
            if not klant.exists():
                raise ValueError("Klant niet gevonden")
        except (ValueError, TypeError):
            raise UserError("Ongeldige Klant ID ingesteld in de Algemene Instellingen.")
        
        # Filter alleen geldige aankoopfacturen (type 'in_invoice' en nog niet doorgefactureerd)
        invoices_to_resell = self.filtered(lambda m: m.move_type == 'in_invoice' and not m.x_doorfactureer_move_id)
        
        if not invoices_to_resell:
            # Kan gebeuren als men de actie aanklikt zonder geselecteerde facturen
            return {
                'warning': {
                    'title': "Geen Facturen Geselecteerd",
                    'message': "Geen geldige aankoopfacturen geselecteerd voor doorfacturatie, of alle geselecteerde facturen zijn al doorgefactureerd."
                }
            }


        # 2. CREËER DE VERKOOPFACTUUR HEADER
        
        # We nemen de valuta van de eerste geselecteerde factuur. Let op: dit veronderstelt 
        # dat alle door te factureren facturen dezelfde valuta hebben.
        currency_id = invoices_to_resell[0].currency_id.id
        
        new_sale_invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': klant.id,
            'invoice_date': fields.Date.today(),
            'currency_id': currency_id,
        })
        
        # 3. LOOP EN MAAK LIJNEN MET MAPPING
        
        new_invoice_lines = []
        for invoice in invoices_to_resell:
            for line in invoice.invoice_line_ids:
                
                purchase_account = line.account_id
                
                # A) ACCOUNT MAPPING GEBRUIKEN
                sale_account = purchase_account.x_resell_sale_account_id
                if not sale_account:
                    raise UserError(f"Fout in doorfacturatie: De Aankooprekening '{purchase_account.display_name}' ({purchase_account.code}) heeft GEEN Doorgefactureerde Verkooprekening ingesteld.")
                
                # B) BTW MAPPING GEBRUIKEN
                sale_taxes = self.env['account.tax']
                
                if line.tax_ids:
                    # Neem de eerste BTW code (vereenvoudiging)
                    purchase_tax = line.tax_ids[0] 
                    sale_tax = purchase_tax.x_resell_sale_tax_id
                    
                    if not sale_tax:
                        raise UserError(f"Fout in doorfacturatie: De Aankoop BTW Code '{purchase_tax.name}' heeft GEEN Doorgefactureerde Verkoop BTW Code ingesteld.")
                        
                    sale_taxes += sale_tax

                # Creëer de lijn data voor de nieuwe factuur
                new_invoice_lines.append((0, 0, {
                    'name': f"Doorgefactureerd: {invoice.name} - {line.name}",
                    'account_id': sale_account.id,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit, 
                    'tax_ids': [(6, 0, sale_taxes.ids)], 
                    'move_id': new_sale_invoice.id,
                    # We gebruiken price_unit en quantity; Odoo berekent price_subtotal
                }))
                
        # 4. VOEG DE LIJNEN TOE EN BOEK DE FACTUUR
        if new_invoice_lines:
            # We voegen de lijnen toe door de write methode op de verkoopfactuur aan te roepen
            new_sale_invoice.write({'invoice_line_ids': new_invoice_lines})
            
            # Valideren/Boeken van de factuur (optioneel, maar efficiënt voor doorfacturatie)
            new_sale_invoice.action_post()
            
            # Vul het referentieveld in op de oorspronkelijke aankoopfacturen (de vlag)
            invoices_to_resell.write({'x_doorfactureer_move_id': new_sale_invoice.id})
        
        # 5. RETURN ACTIE: Ga naar de zojuist aangemaakte verkoopfactuur
        return {
            'name': 'Aangemaakte Verkoopfactuur',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': new_sale_invoice.id,
            'type': 'ir.actions.act_window',
            'target': 'current', # Opent in het huidige venster
        }
