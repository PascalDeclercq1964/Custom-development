# models/res_users.py
from odoo import models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def user_can_see_b2b_price(self):
        """ Controleert of de huidige gebruiker de prijs mag zien op basis van B2B-criteria. """
        user = self.env.user
        
        # 1. Anonieme gebruiker mag GEEN prijs zien
        # Een publieke gebruiker heeft de 'base.group_public' groep, maar niet 'base.group_portal'
        if user.has_group('base.group_public') and not user.has_group('base.group_portal'):
             return False 
        
        # Partner van de ingelogde gebruiker
        partner = user.partner_id
        
        # 2. Check of de klant B2B geblokkeerd is
        if partner.x_is_b2b_blocked:
            return False 
        
        # 3. Check de actieve prijslijst
        # We halen de actieve prijslijst op die de website momenteel gebruikt
        pricelist = self.env['product.pricelist'].browse(self.env.context.get('pricelist'))
        
        # 4. Check of de actieve prijslijst is gemarkeerd als B2B
        if pricelist and pricelist.x_is_b2b_pricelist:
            return True
        
        # Voldoet niet aan alle criteria (ingelogd, niet geblokkeerd, én B2B-prijslijst)
        return False