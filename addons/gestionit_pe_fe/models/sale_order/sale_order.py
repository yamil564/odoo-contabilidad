# -*- coding: utf-8 -*-
from odoo.addons import decimal_precision as dp

from odoo.exceptions import UserError, AccessError

from odoo import fields, models, api, _

import json
import time

import os

from odoo.tools.profiler import profile
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang


import uuid

from itertools import groupby

from datetime import datetime, timedelta

from werkzeug.urls import url_encode


from odoo.addons.gestionit_pe_fe.models.parameters.catalogs import tdi


# class SaleOrderLine(models.Model):
#     _inherit = "sale.order.line"

#     @api.onchange('discount', 'tax_id')
#     def _onchange_discount(self):
#         for line in self:
#             if round(line.discount) >= 100 or round(line.discount) < 0:
#                 line.discount = 0

#             if len([1 for tax in line.tax_id if tax.tipo_afectacion_igv.code in ["31", "32", "33", "34", "35", "36"]]) > 0 and line.discount > 0:
#                 line.discount = 0

#     @api.depends('product_id', 'purchase_price', 'product_uom_qty', 'price_unit', 'price_subtotal')
#     def _product_margin(self):
#         for line in self:
#             currency = line.order_id.pricelist_id.currency_id
#             price = line.purchase_price
#             if len([1 for tax in line.tax_id if tax.tipo_afectacion_igv.code in ["31", "32", "33", "34", "35", "36"]]) == 0:
#                 line.margin = currency.round(
#                     line.price_subtotal - (price * line.product_uom_qty))

# @api.depends('product_id', 'product_uom_qty', 'discount', 'price_unit', 'tax_id')
# def _compute_amount(self):
#     """
#     Compute the amounts of the SO line.
#     """
#     for line in self:
#         if len([1 for tax in line.tax_id if tax.tipo_afectacion_igv.code in ["31", "32", "33", "34", "35", "36"]]) == 0:
#             price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
#             taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
#                                             product=line.product_id, partner=line.order_id.partner_shipping_id)
#             line.update({
#                 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
#                 'price_total': taxes['total_included'],
#                 'price_subtotal': taxes['total_excluded'],
#             })
#         else:
#             line.update({
#                 'price_tax': 0,
#                 'price_total': 0,
#                 'price_subtotal': 0,
#             })


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tipo_documento_identidad = fields.Selection(
        selection="_selection_tipo_documento_identidad")

    def _selection_tipo_documento_identidad(self):
        # hola mundo
        # asfasdf
        asdassd
        return tdi

    tipo_documento = fields.Selection(
        string="Tipo de Documento",
        selection=[('01', 'Factura'), ('03', 'Boleta')],
        default="01",
        required=True)

    @api.onchange("tipo_documento_identidad")
    def _onchange_tipo_documento_identidad(self):
        if self.tipo_documento_identidad == "6":
            self.tipo_documento = "01"
        else:
            self.tipo_documento = "03"

    # # @api.multi
    # def _prepare_invoice(self):
    #     self.ensure_one()
    #     for record in self:
    #         invoice_type_code = record.tipo_documento
    #         journal_ids = record.env["account.journal"].search(
    #             [
    #                 ["invoice_type_code_id", "=", record.tipo_documento]
    #             ]
    #         )

    #         if len(journal_ids) > 0 and record.tipo_documento:
    #             journal_id = journal_ids[0].id
    #         else:
    #             raise UserError("No se pudo generar el comprobante")
    #         if not journal_id:
    #             raise UserError(
    #                 _('Please define an accounting sales journal for this company.'))
    #         invoice_vals = {
    #             'name': record.client_order_ref or '',
    #             'origin': record.name,
    #             'type': 'out_invoice',
    #             'account_id': record.partner_invoice_id.property_account_receivable_id.id,
    #             'partner_id': record.partner_invoice_id.id,
    #             'partner_shipping_id': record.partner_shipping_id.id,
    #             'currency_id': record.pricelist_id.currency_id.id,
    #             'comment': record.note,
    #             'payment_term_id': record.payment_term_id.id,
    #             'fiscal_position_id': record.fiscal_position_id.id or record.partner_invoice_id.property_account_position_id.id,
    #             'company_id': record.company_id.id,
    #             'user_id': record.user_id and record.user_id.id,
    #             'team_id': record.team_id.id,
    #             "invoice_type_code": invoice_type_code,
    #             "journal_id": journal_id,
    #             "descuento_global": record.descuento_global
    #         }
    #         return invoice_vals

    # total_venta_gravado = fields.Monetary(
    #     string="Gravado",
    #     default=0.0,
    #     compute="_amount_all",
    #     currency_field='currency_id')
    # total_venta_inafecto = fields.Monetary(
    #     string="Inafecto",
    #     default=0.0,
    #     compute="_amount_all")
    # total_venta_exonerada = fields.Monetary(
    #     string="Exonerado",
    #     default=0.0,
    #     compute="_amount_all",
    #     currency_field='currency_id')
    # total_venta_gratuito = fields.Monetary(
    #     string="Gratuita",
    #     default=0.0,
    #     compute="_amount_all",
    #     currency_field='currency_id')
    # total_descuentos = fields.Monetary(
    #     string="Total Descuentos",
    #     default=0.0,
    #     compute="_amount_all",
    #     currency_field='currency_id')

    # descuento_global = fields.Float(
    #     string="Descuento Global (%)",
    #     readonly=True,
    #     states={'draft': [('readonly', False)]},
    #     default=0.0)

    # total_descuento_global = fields.Monetary(
    #     string="Total Descuentos Global",
    #     default=0.0,
    #     compute="_amount_all",
    #     currency_field='currency_id')

    # @api.depends('order_line', 'order_line.product_id', 'order_line.price_unit', 'order_line.product_uom_qty', 'order_line.tax_id', 'order_line.discount', 'descuento_global')
    # def _amount_all(self):
    #     for order in self:
    #         total_descuento_global = sum(
    #             [
    #                 line.price_subtotal
    #                 for line in order.order_line
    #                 if len([line.price_subtotal for line_tax in line.tax_id
    #                         if line_tax.tipo_afectacion_igv.code not in ["31", "32", "33", "34", "35", "36"]])
    #             ])*order.descuento_global/100.0

    #         total_venta_gravado = sum(
    #             [
    #                 line.price_subtotal
    #                 for line in order.order_line
    #                 if len([line.price_subtotal for line_tax in line.tax_id if line_tax.tipo_afectacion_igv.code in ["10"]]) or len(line.tax_id) == 0

    #             ])*(1-order.descuento_global/100.0)

    #         total_venta_inafecto = sum(
    #             [
    #                 line.price_subtotal
    #                 for line in order.order_line
    #                 if len(
    #                     [line.price_subtotal for line_tax in line.tax_id
    #                      if line_tax.tipo_afectacion_igv.code in ["40", "30"]])
    #             ])*(1-order.descuento_global/100.0)

    #         total_venta_exonerada = sum(
    #             [
    #                 line.price_subtotal
    #                 for line in order.order_line
    #                 if len(
    #                     [line.price_subtotal for line_tax in line.tax_id
    #                      if line_tax.tipo_afectacion_igv.code in ["20"]])
    #             ])*(1-order.descuento_global/100.0)

    #         total_venta_gratuito = sum(
    #             [
    #                 line.price_unit*line.product_uom_qty
    #                 for line in order.order_line
    #                 if len([line.price_subtotal for line_tax in line.tax_id
    #                         if line_tax.tipo_afectacion_igv.code in ["31", "32", "33", "34", "35", "36"]])
    #             ])

    #         total_descuentos = sum(
    #             [
    #                 ((line.price_subtotal / (1-(line.discount/100.0)))
    #                  * line.discount/100.0)
    #                 for line in order.order_line
    #                 if line.discount <= 100
    #             ]) + total_descuento_global

    #         amount_tax = sum(
    #             [line.price_tax for line in order.order_line])*(1-order.descuento_global/100)

    #         order.update({
    #             'total_descuento_global': total_descuento_global,
    #             'total_venta_gravado': total_venta_gravado,
    #             'total_venta_inafecto': total_venta_inafecto,
    #             'total_venta_exonerada': total_venta_exonerada,
    #             'total_venta_gratuito': total_venta_gratuito,
    #             'total_descuentos': total_descuentos,
    #             'amount_tax': amount_tax,
    #             'amount_total': total_venta_gravado + total_venta_exonerada + total_venta_inafecto + amount_tax
    #         })

    # guia_remision_ids = fields.Many2many("efact.guia_remision")

    # def so_action_context_default_guia_remision(self):
    #     return {
    #         "default_documento_asociado": "orden_venta",
    #         "default_fecha_emision": fields.Date.today(),
    #         "default_fecha_inicio_traslado": fields.Date.today(),
    #         # "default_modalidad_transporte":"01",
    #         "default_motivo_traslado": "01",
    #         "default_sale_order_ids": [(6, 0, [self.id])],
    #         "default_destinatario_partner_id": self.partner_id.id,
    #         "default_company_partner_id": self.partner_id.id
    #     }

    # def so_action_open_guia_remision(self):
    #     guia_remision_ids = self.guia_remision_ids + \
    #         self.invoice_ids.mapped("guia_remision_ids")
    #     if len(guia_remision_ids) > 1:
    #         action = {
    #             "type": "ir.actions.act_window",
    #             "res_model": "efact.guia_remision",
    #             "domain": [("id", "in", guia_remision_ids.mapped("id"))],
    #             "target": "self",
    #             "view_mode": "tree"
    #         }
    #     else:
    #         action = {
    #             "type": "ir.actions.act_window",
    #             "res_model": "efact.guia_remision",
    #             "context": self.so_action_context_default_guia_remision(),
    #             "target": "self",
    #             "view_mode": "form"
    #         }
    #     return action


# class SaleAdvancePayment(models.TransientModel):
#     _inherit = "sale.advance.payment.inv"

#     def _create_invoice(self, order, so_line, amount):
#         # os.system("echo '{} '".format("_create_invoices"))
#         inv_obj = self.env['account.invoice']
#         ir_property_obj = self.env['ir.property']
#         ##############################
#         invoice_type_code = order.tipo_documento
#         journal_ids = self.env["account.journal"].search(
#             [
#                 ["invoice_type_code_id", "=", order.tipo_documento]
#             ]
#         )

#         if len(journal_ids) > 0 and order.tipo_documento:
#             journal_id = journal_ids[0].id
#         else:
#             raise UserError("No se pudo generar el comprobante")
#         # os.system("echo '{} {}'".format(journal_id,invoice_type_code))

#         ##############################

#         account_id = False
#         if self.product_id.id:
#             account_id = order.fiscal_position_id.map_account(
#                 self.product_id.property_account_income_id or self.product_id.categ_id.property_account_income_categ_id).id
#         if not account_id:
#             inc_acc = ir_property_obj.get(
#                 'property_account_income_categ_id', 'product.category')
#             account_id = order.fiscal_position_id.map_account(
#                 inc_acc).id if inc_acc else False
#         if not account_id:
#             raise UserError(
#                 _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
#                 (self.product_id.name,))

#         if self.amount <= 0.00:
#             raise UserError(
#                 _('The value of the down payment amount must be positive.'))
#         context = {'lang': order.partner_id.lang}
#         if self.advance_payment_method == 'percentage':
#             amount = order.amount_untaxed * self.amount / 100
#             name = _("Down payment of %s%%") % (self.amount,)
#         else:
#             amount = self.amount
#             name = _('Down Payment')
#         del context
#         taxes = self.product_id.taxes_id.filtered(
#             lambda r: not order.company_id or r.company_id == order.company_id)
#         if order.fiscal_position_id and taxes:
#             tax_ids = order.fiscal_position_id.map_tax(taxes).ids
#         else:
#             tax_ids = taxes.ids

#         invoice = inv_obj.create({
#             'name': order.client_order_ref or order.name,
#             'origin': order.name,
#             'type': 'out_invoice',
#             'reference': False,
#             'account_id': order.partner_id.property_account_receivable_id.id,
#             'partner_id': order.partner_invoice_id.id,
#             'partner_shipping_id': order.partner_shipping_id.id,
#             "invoice_type_code": invoice_type_code,
#             "journal_id": journal_id,
#             'invoice_line_ids': [(0, 0, {
#                 'name': name,
#                 'origin': order.name,
#                 'account_id': account_id,
#                 'price_unit': amount,
#                 'quantity': 1.0,
#                 'discount': 0.0,
#                 'uom_id': self.product_id.uom_id.id,
#                 'product_id': self.product_id.id,
#                 'sale_line_ids': [(6, 0, [so_line.id])],
#                 'invoice_line_tax_ids': [(6, 0, tax_ids)],
#                 'account_analytic_id': order.analytic_account_id.id or False,
#             })],
#             'currency_id': order.pricelist_id.currency_id.id,
#             'payment_term_id': order.payment_term_id.id,
#             'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
#             'team_id': order.team_id.id,
#             'user_id': order.user_id.id,
#             'comment': order.note,
#         })
#         invoice.compute_taxes()

#         return invoice
