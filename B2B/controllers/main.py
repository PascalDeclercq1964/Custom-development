# controllers/main.py (Gewijzigde _set_b2b_pricelist_context)

def _set_b2b_pricelist_context(self):
    """ Hulpfunctie om de B2B-prijslijst in de context te injecteren. 
        Leest partnergegevens met sudo om ACL-fouten te voorkomen, 
        maar gebruikt de ID van de aangemelde gebruiker.
    """
    if request.website.id == 2 and request.env.user:
        user = request.env.user
        
        # 1. We halen de ID van de partner van de aangemelde gebruiker op (veilige stap)
        partner_id = user.partner_id.id
        
        # 2. We halen de Partner record op, maar nu met Superuser rechten (sudo())
        # Dit omzeilt de ACL-check voor de leesoperatie (die de write-fout veroorzaakt).
        PartnerSudo = request.env['res.partner'].sudo()
        partner_record = PartnerSudo.browse(partner_id)
        
        # Controleer of de partner bestaat en of deze niet geblokkeerd is
        if not partner_record or partner_record.x_is_b2b_blocked:
            return

        # 3. Haal de prijslijst op met de geforceerde context (pricelist=False)
        # We gebruiken de partner_record met sudo rechten, zodat de berekening slaagt.
        pricelist = partner_record.with_context(pricelist=False).property_product_pricelist
        
        # 4. Controleer of de prijslijst B2B is
        if pricelist and pricelist.x_is_b2b_pricelist:
            
            # Injecteer de prijslijst ID in de request context
            request.update_context(pricelist=pricelist.id)
            
            _logger.info("B2B CONTEXT: Pricelist ID %s van partner %s toegepast op request context (FIXED).", pricelist.id, partner_record.name)
        else:
             _logger.info("B2B CONTEXT: Partner %s heeft geen B2B-prijslijst. Standaard website pricelist gebruikt.", partner_record.name)