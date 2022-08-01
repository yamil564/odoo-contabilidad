from odoo import fields,models,api
import logging
_logger = logging.getLogger(__name__)

class AccountBankStatement(models.Model):
	_inherit = "account.bank.statement"

	fecha_fin = fields.Date(string="Fecha Fin")

	def action_generate_bank_statement(self):
		move_line = self.env['account.move.line']
		journals = self.env['account.journal'].search([('type','in',['bank','cash'])])
		accounts = self.env['account.account'].browse()
		for j in journals:
			accounts += j.default_credit_account_id + j.default_debit_account_id
		move_lines_obj = move_line.search([('statement_extract_line_id','=',False),
			('account_id','in',accounts.ids),('move_id.state','=','posted')]).mapped('move_id')

		move = list(set(move_lines_obj.ids))
		move_obj = self.env['account.move'].browse(move)
		move_obj._create_bank_reconcile()

	

	@api.onchange('balance_start')
	def _onchange_balance_end_real(self):
		for rec in self:
			rec._onchange_balance_end_real_real= rec.balance_start + sum([i.amount for i in rec.line_ids])