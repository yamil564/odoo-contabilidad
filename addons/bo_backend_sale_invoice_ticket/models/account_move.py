from re import S
from datetime import datetime, timedelta
import re
from odoo import models, fields, api, _
from odoo.http import request
# import pandas as pd
# import numpy as np
import logging
from odoo.addons.bo_backend_sale_invoice_ticket.models.number_to_letter import to_word
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    @api.model
    def check_user_group(self):
        uid = request.session.uid
        # user = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)
        # if user.has_group('bo_denuncia_ec.group_denuncia_resp'):
        #     return True
        # else:
        #     return False
        return True

    def btn_ticket(self):
        return {
            'name': 'Invoice Ticket',
            'tag': 'invoice_ticket',
            'type': 'ir.actions.client',
            'params': {
                'ticket_id': self.id,
                'model_id': 'account.move'
            }
        }

    @api.model
    def invoice_data(self, ticket_id):
        _logger.info("----- invoice_data -----")
        move_env = self.browse(ticket_id)

        if move_env:
            company_env = self.env['res.company'].browse(
                move_env.company_id.id)
            fields_company = {'currency_id', 'email', 'website', 'company_registry', 'vat', 'name', 'phone',
                              'partner_id', 'country_id', 'state_id', 'city',
                              'tax_calculation_rounding_method', 'street', 'website_invoice_search'}
            company = company_env.read(fields_company)[0]

            fields_move = {'name', 'invoice_type_code', 'invoice_date', 'partner_id', 'total_venta_gravado',
                           'amount_igv', 'total_venta_inafecto', 'total_venta_exonerada', 'total_venta_gratuito',
                           'total_descuento_global', 'total_descuentos', 'amount_total', 'invoice_user_id',
                           'invoice_payment_term_id', 'journal_id', 'digest_value', 'invoice_origin'}
            move = move_env.read(fields_move)[0]

            journal_env = self.env['account.journal'].browse(
                move_env.journal_id.id)
            fields_journal = {'code', 'invoice_type_code_id'}
            journal = journal_env.read(fields_journal)[0]

            partner_env = self.env['res.partner'].browse(
                move_env.partner_id.id)
            fields_partner = {'name', 'vat', 'street',
                              'phone', 'l10n_latam_identification_type_id'}
            partner = partner_env.read(fields_partner)[0]

            l10n_latam_env = self.env['l10n_latam.identification.type'].browse(
                partner_env.l10n_latam_identification_type_id.id)
            fields_l10n_latam = {'name', 'l10n_pe_vat_code'}
            l10n_latam = l10n_latam_env.read(fields_l10n_latam)[0]

            lines_env_ids = self.env['account.move.line'].search(
                [('move_id', '=', move_env.id), ('product_id', '!=', False)])
            fields_line = {'product_id', 'quantity',
                           'price_unit', 'price_subtotal'}
            lines_ids = lines_env_ids.read(fields_line)

            _logger.info("lines_ids: %s" % str(lines_ids))

            json_lines = []
            for line in lines_ids:
                _logger.info("line: %s" % str(line))
                line.update({'product_name': line['product_id'][1]})
                json_lines.append(line)

            # _logger.info("company_env: %s" % str(company_env.read(fields_company)))

            _logger.info("move: %s" % str(move))
            # _logger.info("move_env-read: %s" % str(move.read()))

            # _logger.info("company: %s" % company)

            data = {
                'name': move['name'],
                'origin': move['invoice_origin'],
                'invoice_date': move['invoice_date'],
                'payment_id': move['invoice_payment_term_id'][1] if move['invoice_payment_term_id'] else "Contado",
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
                'digest_value': move['digest_value'],
                'son': to_word(move['amount_total']).upper() + " SOLES",
                'partner': {
                    'name': partner['name'],
                    'vat_label': l10n_latam['name'],
                    'vat': partner['vat'],
                    'street': partner['street'],
                    'phone': partner['phone'],
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
                    'state_id': company['state_id'],
                    'city': company['city'],
                    'country_id': company['country_id'][1],
                    'phone': company['phone'],
                    'logo':  '/web/binary/company_logo'
                }
            }
            # Generar QR
            qr_string = (
                data['company']['vat'],
                data['name'].split("-")[0],
                data['name'].split("-")[1],
                str(data['amount_igv']),
                str(data['amount_total']),
                l10n_latam['l10n_pe_vat_code'],
                move['digest_value'] if move['digest_value'] else "" + "*"
            )
            _logger.info("qr_string: %s" % str(qr_string))
            data.update({
                'qr_string': "|".join(qr_string)
            })
            _logger.info("data: %s" % str(data))
            return data
        else:
            return {}
