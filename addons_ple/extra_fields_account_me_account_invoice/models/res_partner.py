from odoo import models, fields, api, _

class ResPartner(models.Model):
	_inherit = "res.partner"

	property_account_receivable_me_id=fields.Many2one('account.account' ,
		string="Cuenta a cobrar ME", company_dependent=True, 
		domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
		help="This account will be used instead of the default one as the receivable account for the current partner",
		required=True
		)

	property_account_payable_me_id=fields.Many2one('account.account',
		company_dependent=True, string="Cuenta a pagar ME",
		domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
		help="This account will be used instead of the default one as the payable account for the current partner",
		required=True)

	#massive_update = fields.Boolean(string="Sujeto a actualización Masiva", default=True)

	@api.model
	def _commercial_fields(self):
		return super(ResPartner, self)._commercial_fields() + \
			['property_account_receivable_me_id', 'property_account_payable_me_id']