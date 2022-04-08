# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	@api.onchange('partner_id', 'company_id')
	def _onchange_partner_id(self):
		res = super(AccountInvoice, self)._onchange_partner_id()
		company = self.company_id
		if self.currency_id and self.currency_id != company.currency_id:
			p = self.partner_id if not company else self.partner_id.with_context(force_company=company.id)
			type = self.type or self.env.context.get('type', 'out_invoice')
			account_id = False
			currency = self.currency_id
			if p:
				rec_account = p.property_account_receivable_me_id
				pay_account = p.property_account_payable_me_id
				if not rec_account and not pay_account:
					action = self.env.ref('account.action_account_config')
					msg = _('Cannot find a chart of accounts ME for this company, You should configure it. \nPlease go to Account Configuration.')
					raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
				if type in ('in_invoice', 'in_refund'):
					account_id = pay_account.id
				else:
					account_id = rec_account.id
			self.account_id = account_id
		return res

	@api.onchange('currency_id')
	def _onchange_currency_id(self):
		self._onchange_partner_id()