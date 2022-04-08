# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_account_ME = fields.Boolean("Cuentas por Cobrar y por Pagar en Divisa",  implied_group='base.group_multi_currency', default=False)#,
    property_account_receivable_me_id=fields.Many2one('account.account',
        string="Cuenta a cobrar ME",
        related='company_id.property_account_receivable_me_id',
        implied_group='base.group_multi_currency',
        readonly=False)

    property_account_payable_me_id=fields.Many2one('account.account',
        string="Cuenta a pagar ME",
        related='company_id.property_account_payable_me_id',
        implied_group='base.group_multi_currency',
        readonly=False)

    
    @api.multi   
    def sync_account_partners(self):
        env = api.Environment(self._cr, SUPERUSER_ID, {})
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
                _logger.info('\n\n %r \n\n', [account,value])
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