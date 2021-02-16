# -*- coding: utf-8 -*-
from odoo import fields,models,api
from odoo.tools.profiler import profile

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    tipo_sistema_calculo_isc = fields.Many2one("einvoice.catalog.08")
    tipo_afectacion_igv_type = fields.Char("Tipo Afectación IGV - Tipo")
    tipo_afectacion_igv_code = fields.Char("Tipo Afectación IGV - Código")
    tipo_afectacion_igv_name = fields.Char("Tipo Afectación IGV - Nomre")
    no_onerosa  = fields.Boolean("No onerosa",compute="_compute_price")
    price_subtotal2 = fields.Float("Precio Total",compute="_compute_price")
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
                record.name = record.name.replace("\n"," ")

    @profile
    @api.one
    @api.depends(
        'price_unit', 'discount', 'invoice_line_tax_ids','quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 
        'invoice_id.company_id','invoice_id.date_invoice'
        )
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)

        if len([1 for tax in self.invoice_line_tax_ids if tax.tipo_afectacion_igv.code in ["31","32","33","34","35","36"]]) == 0:
            self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
            self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        else:
            self.price_subtotal = price_subtotal_signed =  0
            self.price_total = 0

        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id._get_currency_rate_date()).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
        self.price_subtotal2 = self.quantity*(self.price_unit*(1 - ((self.discount or 0.0) / 100.0))- self.descuento_unitario)
        self.no_onerosa = self.invoice_line_tax_ids[0].tipo_afectacion_igv.no_onerosa if  len(self.invoice_line_tax_ids)>0 else False
        
    @profile
    @api.onchange("invoice_line_tax_ids")
    def _afectacion_igv(self):
        self.tipo_afectacion_igv_type = self.invoice_line_tax_ids[0].tipo_afectacion_igv.type if  len(self.invoice_line_tax_ids)>0 else False
        self.tipo_afectacion_igv_code = self.invoice_line_tax_ids[0].tipo_afectacion_igv.code if  len(self.invoice_line_tax_ids)>0 else False
        self.tipo_afectacion_igv_name = self.invoice_line_tax_ids[0].tipo_afectacion_igv.name if  len(self.invoice_line_tax_ids)>0 else False
        
    
