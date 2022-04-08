from odoo import models, fields, api, _

class ResCompany(models.Model):
	_inherit = "res.company"

	property_account_receivable_me_id=fields.Many2one('account.account' ,
		string="Cuenta a cobrar ME",
		implied_group='base.group_multi_currency')

	property_account_payable_me_id=fields.Many2one('account.account',
		string="Cuenta a pagar ME",
		implied_group='base.group_multi_currency')