from re import S
from datetime import datetime, timedelta
import re
from odoo import models, fields, api, _
from odoo.http import request
import pandas as pd
import numpy as np
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'
    
    @api.model
    def check_user_group(self):
        uid = request.session.uid
        user = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        # if user.has_group('bo_denuncia_ec.group_denuncia_resp'):
        #     return True
        # else:
        #     return False
        return True

    def btn_invoice_ticket(self):
        return {
            'name': 'Invoice Ticket',
            'tag': 'invoice_ticket',
            'type': 'ir.actions.client',
            'params': {
                'invoice_id': self.id
                }
            }

    @api.model
    def invoice_data(self, invoice_id):
        _logger.info("----- invoice_data -----")
        move_env = self.browse(invoice_id)
        
        if move_env:
            company_env = self.env['res.company'].browse(move_env.company_id.id)
            fields_company = {'currency_id', 'email', 'website', 'company_registry', 'vat', 'name', 'phone', 
                'partner_id' , 'country_id', 'state_id', 'city',
                'tax_calculation_rounding_method','street', 'website_invoice_search'}
            company = company_env.read(fields_company)[0]

            fields_move = {'name','invoice_type_code','invoice_date','partner_id','total_venta_gravado',
                'amount_igv','total_venta_inafecto','total_venta_exonerada','total_venta_gratuito',
                'total_descuento_global','total_descuentos','amount_total','invoice_user_id'}
            move = move_env.read(fields_move)[0]

            partner_env = self.env['res.partner'].browse(move_env.partner_id.id)
            fields_partner = {'name', 'vat','street', 'l10n_latam_identification_type_id'}
            partner = partner_env.read(fields_partner)[0]

            lines_env_ids = self.env['account.move.line'].search([('move_id','=',move_env.id),('product_id','!=',False)])
            fields_line = {'product_id', 'quantity','price_unit', 'price_subtotal'}
            lines_ids = lines_env_ids.read(fields_line)

            _logger.info("lines_ids: %s" % str(lines_ids))

            json_lines = []
            for line in lines_ids:
                _logger.info("line: %s" % str(line))
                line.update({'product_name': line['product_id'][1]})
                json_lines.append(line)

            # _logger.info("company_env: %s" % str(company_env.read(fields_company)))

            # _logger.info("move: %s" % str(move))
            # _logger.info("move_env-read: %s" % str(move.read()))
            
            # _logger.info("company: %s" % company)

            data = {
                'name': move['name'],
                'invoice_date': move['invoice_date'],
                'cashier': move['invoice_user_id'][1],
                'invoice_type_code': move['invoice_type_code'],
                'total_venta_gravado': move['total_venta_gravado'],
                'amount_igv': move['amount_igv'],
                'total_venta_inafecto': move['total_venta_inafecto'],
                'total_venta_exonerada': move['total_venta_exonerada'],
                'total_venta_gratuito': move['total_venta_gratuito'],
                'total_descuento_global': move['total_descuento_global'],
                'total_descuentos': move['total_descuentos'],
                'amount_total': move['amount_total'],
                'partner': {
                    'name': partner['name'],
                    'vat': partner['vat'],
                    'street': partner['street'],
                    'identification_type_id': partner['l10n_latam_identification_type_id'][0]
                },
                'orderlines': json_lines,
                'precision': {
                    'price': 2,
                    'money': 2,
                    'quantity': 3
                },
                'company': {
                    'email': company['email'],
                    'website': company['website'],
                    'website_invoice_search': company['website_invoice_search'],
                    'company_registry': company['company_registry'],
                    'contact_address': company['partner_id'][1],
                    'vat': company['vat'],
                    'vat_label': "RUC",
                    'name': company['name'],
                    'street': company['street'],
                    'state_id': company['state_id'][1],
                    'city': company['city'],
                    'country_id': company['country_id'][1],
                    'phone': company['phone'],
                    'logo':  ''
                }
            }
            _logger.info("data: %s" % str(data))
            return {
                'receipt': data
            }
        else:
            return { 'receipt' : {}}