# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.profiler import profile

import logging
log = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # tipo_sistema_calculo_isc = fields.Many2one("einvoice.catalog.08")
    tipo_afectacion_igv_type = fields.Char("Tipo Afectación IGV - Tipo")
    tipo_afectacion_igv_code = fields.Char("Tipo Afectación IGV - Código")
    tipo_afectacion_igv_name = fields.Char("Tipo Afectación IGV - Nombre")
    no_onerosa = fields.Boolean("No onerosa", compute="_compute_price")
    price_subtotal2 = fields.Float("Precio Total", compute="_compute_price")
    descuento_unitario = fields.Float("Descuento Unitario")

    @api.onchange('discount')
    def _onchange_discount(self):
        for record in self:
            if record.discount >= 100:
                record.discount = 0

    @api.onchange('name')
    def _onchange_name(self):
        for record in self:
            if record.name:
                record.name = record.name.strip()
                record.name = record.name.replace("\n", " ")

    # @profile
    # @api.one
    @api.depends(
        'price_unit', 'discount', 'tax_ids', 'quantity',
        'product_id', 'move_id.partner_id', 'move_id.currency_id',
        'move_id.company_id', 'move_id.date'
    )
    def _compute_price(self):
        # self.ensure_one()
        for line in self:
            currency = line.move_id and line.move_id.currency_id or None
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = False
            if line.tax_ids:
                taxes = line.tax_ids.compute_all(
                    price, currency, line.quantity, product=line.product_id, partner=line.move_id.partner_id)

            if len([1 for tax in line.tax_ids if tax.tax_group_id.codigo in ["31", "32", "33", "34", "35", "36"]]) == 0:
                line.price_subtotal = price_subtotal_signed = taxes[
                    'total_excluded'] if taxes else line.quantity * price
                line.price_total = taxes['total_included'] if taxes else line.price_subtotal
            else:
                line.price_subtotal = price_subtotal_signed = 0
                line.price_total = 0

            # if line.move_id.currency_id and line.move_id.currency_id != line.move_id.company_id.currency_id:
            #     price_subtotal_signed = line.move_id.currency_id.with_context(date=line.move_id._get_currency_rate_date(
            #     )).compute(price_subtotal_signed, line.move_id.company_id.currency_id)
            sign = line.move_id.type in ['in_refund', 'out_refund'] and -1 or 1
            line.price_subtotal_signed = price_subtotal_signed * sign
            line.price_subtotal2 = line.quantity * \
                (line.price_unit*(1 - ((line.discount or 0.0) / 100.0)) -
                 line.descuento_unitario)
            line.no_onerosa = line.tax_ids[0].tax_group_id.no_onerosa if len(
                line.tax_ids) > 0 else False

    # @profile
    @api.onchange("tax_ids")
    def _afectacion_igv(self):
        self.tipo_afectacion_igv_type = self.tax_ids[0].tax_group_id.tipo_afectacion if self.tax_ids else False
        self.tipo_afectacion_igv_code = self.tax_ids[0].tax_group_id.codigo if self.tax_ids else False
        self.tipo_afectacion_igv_name = self.tax_ids[0].tax_group_id.descripcion if self.tax_ids else False

        log.info("tipo_afectacion line")
        log.info(self.tax_ids)
