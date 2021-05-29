# -*- coding: utf-8 -*-
from odoo import api, models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    sunat_user = fields.Char("USUARIO SOL")
    sunat_pass = fields.Char("CLAVE SOL")
    tipo_envio = fields.Selection(selection=[(
        "0", "0 - Pruebas"), ("1", "1 - Producción")], default=0)

    cert_id = fields.Many2one(
        "cert.sunat", string="Certificados digitales")

    # validez_comprobantes_client_id = fields.Char("Cliente Id")
    # validez_comprobantes_client_secret = fields.Char("Cliente Secret")
    # url_consulta_comprobante = fields.Char("Consulta Comprobante URL")
    # mensaje_representacion_impresa = fields.Html(
    #     "Mensaje de Representación Impresa")
