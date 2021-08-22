# -*- coding: utf-8 -*-
from odoo import api, models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    sunat_user = fields.Char("USUARIO SUNAT",help="Nombre del usuario secundario con permiso para emisión de comprobantes electrónicos.")
    sunat_pass = fields.Char("CLAVE SUNAT",help="Password del usuario secundario con permiso para emisión de comprobantes electrónicos.")
    tipo_envio = fields.Selection(selection=[("0", "0 - Pruebas"), ("1", "1 - Producción")], default="0")

    cert_id = fields.Many2one("cert.sunat", string="Certificados digitales")

    website_invoice_search = fields.Char("Web de consulta de comprobante")
    default_national_bank_account_id = fields.Many2one("res.partner.bank",string="Cuenta de detracciones del Banco de la Nación",domain=[("is_national_bank_detraction","=",True)])
    default_product_global_discount_id = fields.Many2one("product.product",domain=[('is_charge_or_discount','=',True),('type_charge_or_discount_id','in',['02'])])

    def get_username_sunat(self):
        return "{}{}".format(self.vat,self.sunat_user)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    product_global_discount_id = fields.Many2one(related="company_id.default_product_global_discount_id",readonly=False)