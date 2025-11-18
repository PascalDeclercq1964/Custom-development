
# models/res_users.py
from odoo import models, api
import logging
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def user_can_see_b2b_price(self):
        user = self.env.user
        partner = user.partner_id
        
        # 1. Check: Anonieme gebruiker
        # Een publieke gebruiker is in de 'base.group_public' maar niet in 'base.group_portal'
        is_public_user = user.has_group('base.group_public') and not user.has_group('base.group_portal')
        _logger.info("B2B Debug: Huidige gebruiker: %s (ID: %s)", user.name, user.id)
        _logger.info("B2B Debug: Is Publieke Gebruiker (Anoniem): %s", is_public_user)

        if is_public_user:
             return False 
        
        # 2. Check: B2B Geblokkeerd op Contact
        _logger.info("B2B Debug: Partner B2B geblokkeerd: %s", partner.x_is_b2b_blocked)
        if partner.is_b2b_blocked:
            return False 
        
        # 3. Check: Prijslijst is B2B
        # Belangrijk: De prijslijst is de ACTIEVE prijslijst in de context
        pricelist_id = self.env.context.get('pricelist')
        pricelist = self.env['product.pricelist'].browse(pricelist_id) if pricelist_id else self.env['product.pricelist']
        
        _logger.info("B2B Debug: Actieve Prijslijst ID: %s", pricelist.id)
        
        # Zorg dat 'is_b2b_pricelist' is gedefinieerd in product.pricelist (uit Stap 1)
        is_b2b_pricelist = pricelist and pricelist.x_is_b2b_pricelist
        _logger.info("B2B Debug: Prijslijst gemarkeerd als B2B: %s", is_b2b_pricelist)

        if is_b2b_pricelist:
            _logger.info("B2B Debug: CONCLUSIE: TOON PRIJS (True)")
            return True
        
        _logger.info("B2B Debug: CONCLUSIE: VERBERG PRIJS (False)")
        return False