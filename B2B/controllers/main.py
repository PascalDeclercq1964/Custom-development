from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleB2B(WebsiteSale):

    def _set_b2b_pricelist_context(self):
        """ Hulpfunctie om de B2B-prijslijst in de context te injecteren. """
        
        # Controleer of we op de B2B-website (ID 2) zijn
        if request.website.id == 2 and request.env.user:
            user = request.env.user
            partner = user.partner_id
            
            # Gebruik de gefixeerde logica om de partner prijslijst te krijgen,
            # door de pricelist uit de context te negeren.
            pricelist = partner.with_context(pricelist=False).property_product_pricelist
            
            # Aanname: is_b2b_pricelist is het veld op product.pricelist
            if pricelist and pricelist.x_is_b2b_pricelist and not partner.x_is_b2b_blocked:
                
                # Forceer de pricelist ID in de context van de request
                # Hierdoor gebruiken alle ORM-berekeningen (zoals product.price) deze pricelist.
                request.update_context(pricelist=pricelist.id)
                _logger.info("B2B CONTEXT: Pricelist ID %s van partner %s toegepast op request context.", pricelist.id, partner.name)
            elif user.id != request.env.ref('base.public_user').id:
                # Als de gebruiker is ingelogd maar geen B2B-prijslijst heeft,
                # zorgen we dat de website's standaardprijslijst wordt gebruikt 
                # (maar de QWeb verbergt de prijs, zie stap 3).
                _logger.info("B2B CONTEXT: Ingelogde gebruiker zonder B2B-prijslijst. Standaard website pricelist gebruikt.")


    # Override voor Categorie/Shop overzichtspagina's
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, **post):
        self._set_b2b_pricelist_context()
        return super(WebsiteSaleB2B, self).shop(**post)

    # Override voor Product Detailpagina's
    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        self._set_b2b_pricelist_context()
        return super(WebsiteSaleB2B, self).product(product, category=category, search=search, **kwargs)