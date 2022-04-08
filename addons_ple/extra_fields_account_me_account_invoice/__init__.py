from . import models
from . import wizard
from odoo import api, SUPERUSER_ID, _, tools


def _configure_account_me(cr, registry):
	env = api.Environment(cr, SUPERUSER_ID, {})

	company_ids = env['res.company'].search([('chart_template_id','!=',False)])
	# Property Stock Accounts
	for company_id in company_ids:
		todo_list = [
			('property_account_receivable_me_id', 'res.partner', 'account.account'),
			('property_account_payable_me_id', 'res.partner', 'account.account'),
		]
		for record in todo_list:
			account = getattr(company_id, record[0])
			value = account and 'account.account,' + str(account.id) or False
			if value:
				field = env['ir.model.fields'].search([
					('name', '=', record[0]), 
					('model', '=', record[1]), 
					('relation', '=', record[2])
				], limit=1)

				vals = {
					'name': record[0],
					'company_id': company_id.id,
					'fields_id': field.id,
					'value': value,
				}
				properties = env['ir.property'].search([
					('name', '=', record[0]),
					('company_id', '=', company_id.id)
				])
				if properties:
					#the property exist: modify it
					properties.write(vals)
				else:
					#create the property
					env['ir.property'].create(vals)

# def post_install_hook(cr, registry):
# 	env = Environment(cr, SUPERUSER_ID, {})
# 	partner_ids=env['res.partner'].search([])
# 	for line in partner_ids:
# 		line.write({'property_account_receivable_me_id':line.company_id.property_account_receivable_me_id.id})
# 		line.write({'property_account_payable_me_id':line.company_id.property_account_payable_me_id.id})
