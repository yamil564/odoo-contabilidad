from odoo import fields, api, models, _

class SaleOrder(models.Model):
	_inherit = "sale.order"

	def _finalize_invoices(self, invoices, references):
		for invoice in invoices.values():
			invoice._onchange_currency_id()
		super(SaleOrder, self)._finalize_invoices(invoices, references)