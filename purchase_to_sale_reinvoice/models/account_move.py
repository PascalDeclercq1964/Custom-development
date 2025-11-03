from odoo import fields, models, api
from odoo.exceptions import UserError
from collections import defaultdict

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

    def action_resell_selected_invoices_hardcoded(self):
        # 1. HARDGECODEERDE CONSTANTEN DEFINIËREN
        # Zoek ID's op basis van hun XML ID of handmatig (moet u zelf aanpassen!)

        # Vaste Klant (Vervang 'external_id_klant' door de werkelijke XML ID of zoek handmatig)
        # Beter is het om de klant op te zoeken op naam of ID:
        klant = self.env['res.partner'].search([('name', '=', 'Vaste Klant Naam')], limit=1)
        if not klant:
            raise UserError("Vaste klant 'Vaste Klant Naam' niet gevonden. Pas de hardgecodeerde naam aan.")

        # Hardgecodeerde Mappings voor Accounts (Vervang 'aank_rekening_id' en 'verk_rekening_id' door de werkelijke ID's)
        # We maken een dictionary aan om snel te kunnen mappen:
        # Sleutel is de ID van de Aankooprekening, Waarde is de ID van de Verkooprekening
        ACCOUNT_MAPPING = {
            # Voorbeeld: Zorg dat u de werkelijke ID's hier invult!
            # 600000: 700000, 
            # 610000: 710000, 
        }

        # Hardgecodeerde Mappings voor BTW Codes (Sleutel: Aankoop BTW ID, Waarde: Verkoop BTW ID)
        TAX_MAPPING = {
            # Voorbeeld: 
            # 'Tax 21% Purchase ID': 'Tax 21% Sale ID', 
        }

        # 2. VALIDATIE
        invoices_to_resell = self.filtered(lambda m: m.move_type == 'in_invoice' and not m.x_doorfactureer_move_id)
        
        if not invoices_to_resell:
            raise UserError("Er zijn geen (geldige) aankoopfacturen geselecteerd voor doorfacturatie.")

        # 3. CREËER DE VERKOOPFACTUUR HEADER
        new_sale_invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': klant.id,
            'invoice_date': fields.Date.today(),
            # Optioneel: Stel de betalingstermijn in, valuta, etc.
        })
        
        # 4. LOOP EN MAAK LIJNEN
        
        new_invoice_lines = []
        for invoice in invoices_to_resell:
            for line in invoice.invoice_line_ids:
                # Zoek de nieuwe account ID op in de mapping
                purchase_acc_id = line.account_id.id
                sale_acc_id = ACCOUNT_MAPPING.get(purchase_acc_id)
                
                if not sale_acc_id:
                    raise UserError(f"Geen Verkooprekening gevonden voor Aankooprekening ID {purchase_acc_id}.")
                
                # Bepaal de nieuwe BTW ID
                # Voor eenvoud nemen we de eerste BTW ID als de enige, u kunt dit aanpassen indien nodig
                purchase_tax_id = line.tax_ids[:1].id if line.tax_ids else False
                sale_tax_id = TAX_MAPPING.get(purchase_tax_id) if purchase_tax_id else False

                if purchase_tax_id and not sale_tax_id:
                    raise UserError(f"Geen Verkoop BTW ID gevonden voor Aankoop BTW ID {purchase_tax_id}.")
                
                # Creëer de lijn voor de nieuwe factuur
                new_invoice_lines.append((0, 0, {
                    'name': f"Doorgefactureerd: {invoice.name} - {line.name}",
                    'account_id': sale_acc_id,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'tax_ids': [(6, 0, [sale_tax_id])] if sale_tax_id else False,
                    # De verkoopfactuurlijn neemt de bedragen en hoeveelheid over van de aankoopfactuurlijn
                    # Optioneel: Voeg hier een marge of prijsberekening toe
                }))

        # 5. VOEG DE LIJNEN TOE EN UPDATE DE REFERENTIES
        if new_invoice_lines:
            new_sale_invoice.write({'invoice_line_ids': new_invoice_lines})
            
            # Vul het referentieveld in op de oorspronkelijke aankoopfacturen
            invoices_to_resell.write({'x_doorfactureer_move_id': new_sale_invoice.id})
            
            # Optioneel: Zet de factuur op 'Geboekt'
            new_sale_invoice.action_post()
        
        # 6. RETURN ACTIE: Ga naar de zojuist aangemaakte verkoopfactuur
        return {
            'name': 'Aangemaakte Verkoopfactuur',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': new_sale_invoice.id,
            'type': 'ir.actions.act_window',
        }