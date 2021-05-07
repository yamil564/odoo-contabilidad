# -*- coding: utf-8 -*-
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError
from odoo import fields, models, api, _
from odoo.tools.profiler import profile
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from itertools import groupby
from datetime import datetime, timedelta
from werkzeug.urls import url_encode
from odoo.addons.gestionit_pe_fe.models.parameters.catalogs import tdi

import json
import time
import uuid
import os


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tipo_documento_identidad = fields.Selection(
        selection="_selection_tipo_documento_identidad")

    def _selection_tipo_documento_identidad(self):
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

    # Create invoice
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        # ensure a correct context for the _get_default_journal method and company-dependent fields
        self = self.with_context(
            default_company_id=self.company_id.id, force_company=self.company_id.id)
        journal = self.env['account.move'].with_context(
            default_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (
                self.company_id.name, self.company_id.id))

        warehouse_id = self.picking_ids[0].picking_type_id.warehouse_id

        for whj in warehouse_id.journal_ids:
            if whj.invoice_type_code_id == self.tipo_documento:
                journal = whj
                break

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'invoice_partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_payment_ref': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'invoice_type_code': self.tipo_documento,
            'warehouse_id': warehouse_id,
        }
        return invoice_vals

    total_venta_gravado = fields.Monetary(
        string="Gravado",
        default=0.0,
        compute="_amount_all",
        currency_field='currency_id')
    total_venta_inafecto = fields.Monetary(
        string="Inafecto",
        default=0.0,
        compute="_amount_all")
    total_venta_exonerada = fields.Monetary(
        string="Exonerado",
        default=0.0,
        compute="_amount_all",
        currency_field='currency_id')
    total_venta_gratuito = fields.Monetary(
        string="Gratuita",
        default=0.0,
        compute="_amount_all",
        currency_field='currency_id')
    total_descuentos = fields.Monetary(
        string="Total Descuentos",
        default=0.0,
        compute="_amount_all",
        currency_field='currency_id')
    # amount_igv = fields.Monetary(
    #     string="IGV",
    #     default=0.0,
    #     compute="_amount_all")
    descuento_global = fields.Float(
        string="Descuento Global (%)",
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=0.0)
    total_descuento_global = fields.Monetary(
        string="Total Descuentos Global",
        default=0.0,
        compute="_amount_all",
        currency_field='currency_id')

    @api.depends('order_line', 'order_line.product_id', 'order_line.price_unit', 'order_line.product_uom_qty', 'order_line.tax_id', 'order_line.discount', 'descuento_global')
    def _amount_all(self):
        for order in self:
            total_descuento_global = sum(
                [
                    line.price_subtotal
                    for line in order.order_line
                    if len([line.price_subtotal for line_tax in line.tax_id
                            if line_tax.tax_group_id.tipo_afectacion not in ["31", "32", "33", "34", "35", "36"]])
                ])*order.descuento_global/100.0

            total_venta_gravado = sum(
                [
                    line.price_subtotal
                    for line in order.order_line
                    if len([line.price_subtotal for line_tax in line.tax_id if line_tax.tax_group_id.tipo_afectacion in ["10"]]) or len(line.tax_id) == 0

                ])*(1-order.descuento_global/100.0)

            total_venta_inafecto = sum(
                [
                    line.price_subtotal
                    for line in order.order_line
                    if len(
                        [line.price_subtotal for line_tax in line.tax_id
                         if line_tax.tax_group_id.tipo_afectacion in ["40", "30"]])
                ])*(1-order.descuento_global/100.0)

            total_venta_exonerada = sum(
                [
                    line.price_subtotal
                    for line in order.order_line
                    if len(
                        [line.price_subtotal for line_tax in line.tax_id
                         if line_tax.tax_group_id.tipo_afectacion in ["20"]])
                ])*(1-order.descuento_global/100.0)

            total_venta_gratuito = sum(
                [
                    line.price_unit*line.product_uom_qty
                    for line in order.order_line
                    if len([line.price_subtotal for line_tax in line.tax_id
                            if line_tax.tax_group_id.tipo_afectacion in ["31", "32", "33", "34", "35", "36"]])
                ])

            total_descuentos = sum(
                [
                    ((line.price_subtotal / (1-(line.discount/100.0)))
                     * line.discount/100.0)
                    for line in order.order_line
                    if line.discount <= 100
                ]) + total_descuento_global

            amount_tax = (sum(
                [line.price_tax for line in order.order_line])+total_venta_gratuito)*(1-order.descuento_global/100)

            order.update({
                'total_descuento_global': total_descuento_global,
                'total_venta_gravado': total_venta_gravado,
                'total_venta_inafecto': total_venta_inafecto,
                'total_venta_exonerada': total_venta_exonerada,
                'total_venta_gratuito': total_venta_gratuito,
                'total_descuentos': total_descuentos,
                'amount_tax': amount_tax,
                'amount_total': total_venta_gravado + total_venta_exonerada + total_venta_inafecto + amount_tax
            })

    guia_remision_ids = fields.Many2many("gestionit.guia_remision")

    def so_action_context_default_guia_remision(self):
        return {
            "default_documento_asociado": "orden_venta",
            "default_fecha_emision": fields.Date.today(),
            "default_fecha_inicio_traslado": fields.Date.today(),
            # "default_modalidad_transporte":"01",
            "default_motivo_traslado": "01",
            "default_sale_order_ids": [(6, 0, [self.id])],
            "default_destinatario_partner_id": self.partner_id.id,
            "default_company_partner_id": self.partner_id.id
        }

    def so_action_open_guia_remision(self):
        guia_remision_ids = self.guia_remision_ids + \
            self.invoice_ids.mapped("guia_remision_ids")
        if len(guia_remision_ids) > 1:
            action = {
                "type": "ir.actions.act_window",
                "res_model": "gestionit.guia_remision",
                "domain": [("id", "in", guia_remision_ids.mapped("id"))],
                "target": "self",
                "view_mode": "tree"
            }
        else:
            action = {
                "type": "ir.actions.act_window",
                "res_model": "gestionit.guia_remision",
                "context": self.so_action_context_default_guia_remision(),
                "target": "self",
                "view_mode": "form"
            }
        return action
