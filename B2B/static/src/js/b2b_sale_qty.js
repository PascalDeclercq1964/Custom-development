/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/widget";
import WebsiteSale from "@website_sale/js/website_sale"; // Importeer de originele widget

// Overschrijf de WebsiteSale widget
publicWidget.registry.WebsiteSale.include({

    /**
     * Override de functie die de hoeveelheid update bij een klik op '+' of '-'.
     */
    _onChangeCartQuantity: function (ev) {
        // Zorg ervoor dat de oorspronkelijke functie wordt uitgevoerd
        this._super.apply(this, arguments);

        // EXTRA LOGICA OM data-step TE RESPECTEREN
        // Deze logica is essentieel als Odoo's standaard implementatie data-step negeert

        var $input = $(ev.currentTarget).closest('.css_quantity').find("input[name='add_qty']");
        var $link = $(ev.currentTarget);

        // 1. Haal de dynamische stapgrootte op (gezet in QWeb)
        var step = parseFloat($input.data('step') || 1); 
        var quantity = parseFloat($input.val());

        if (step > 1) { // Voer alleen de logic uit als we B2B-specifieke stappen hebben
            
            // 2. Pas de hoeveelheid aan
            if ($link.hasClass('js_add_cart_json')) {
                if ($link.find('.fa-plus').length) {
                    // Als er op plus geklikt is, zorg dan dat het een veelvoud van 'step' is
                    quantity = Math.ceil(quantity / step) * step;
                } else if ($link.find('.fa-minus').length) {
                    // Als er op min geklikt is
                    quantity = Math.floor(quantity / step) * step;
                }
            }
            
            // 3. Zorg voor het minimum (data-min)
            var min_qty = parseFloat($input.data('min') || 1);
            if (quantity < min_qty) {
                quantity = min_qty;
            }

            // Werk de inputwaarde bij VOOR het verzenden naar de server
            $input.val(quantity);
            
            // Trigger een herberekening in de originele widget om de server te updaten
            $input.trigger('change');
        }
    },
});