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
