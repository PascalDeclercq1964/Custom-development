from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
_inherit = 'account.move'


reinvoice_sale_id = fields.Many2one('account.move', string='Reinvoice Sale', readonly=True, copy=False)


def action_reinvoice_selected(self):
active_ids = self.env.context.get('active_ids') or []
bills = self.env['account.move'].browse(active_ids)
return self._reinvoice_moves(bills)


def _reinvoice_moves(self, bills):
Sale = self.env['account.move']
Param = self.env['ir.config_parameter']


partner_id = int(Param.sudo().get_param('purchase_to_sale_reinvoice.reinvoice_partner_id') or 0)
if not partner_id:
raise UserError(_('Please configure the Reinvoice Customer in Settings > Accounting > Reinvoice Customer.'))


created = []
for bill in bills.filtered(lambda m: m.move_type in ('in_invoice', 'in_refund')):
if bill.reinvoice_sale_id:
continue


sale_vals = {
'move_type': 'out_invoice',
'partner_id': partner_id,
'invoice_date': bill.invoice_date,
'invoice_origin': bill.name or bill.ref or bill.invoice_number,
'company_id': bill.company_id.id,
'invoice_line_ids': [],
}
sale = Sale.create(sale_vals)


for line in bill.invoice_line_ids:
mapped_account = getattr(line, 'mapped_account_id', False)
mapped_tax = getattr(line, 'mapped_tax_id', False)


account_id = mapped_account.id if mapped_account else line.account_id.id
taxes = [(6, 0, [mapped_tax.id])] if mapped_tax else [(6, 0, line.tax_ids.ids)]


price_unit = line.price_unit if bill.move_type == 'in_invoice' else -line.price_unit


sale_line_vals = {
'name': line.name,
'quantity': line.quantity,
'price_unit': price_unit,
'account_id': account_id,
'tax_ids': taxes,
}
sale.write({'invoice_line_ids': [(0, 0, sale_line_vals)]})


bill.reinvoice_sale_id = sale.id
created.append(sale)


return {
'type': 'ir.actions.client',
'tag': 'reload',
'created_count': len(created),
}