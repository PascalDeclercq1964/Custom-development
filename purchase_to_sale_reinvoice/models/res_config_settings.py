from odoo import fields, models



    # Veld om de vaste klant op te slaan
    resell_partner_id = fields.Many2one(
        'res.partner',
        string="Klant voor doorfacturatie",
        config_parameter='purchase_to_sale_reinvoice.resell_partner_id',
        domain=[('customer_rank', '>', 0)], # Zorg dat het een klant is
        help="De standaard klant waarnaar alle geselecteerde aankoopfacturen worden doorgefactureerd."
    )