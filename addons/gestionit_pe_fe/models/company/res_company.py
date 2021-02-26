# -*- coding: utf-8 -*-
from odoo import api, models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    # type_endpoint = fields.Selection(
    #     selection=[
    #         ("production", "Producción"),
    #         ("devlopment", "Desarrollo")
    #     ],
    #     string="Tipo de Endpoint"
    # )
    # endpoint = fields.Char("Endpoint")
    sunat_user = fields.Char("USUARIO SOL")
    sunat_pass = fields.Char("CLAVE SOL")
    key_public = fields.Text("Cert. PUBLIC")
    key_private = fields.Text("Cert. PRIVATE")
    tipo_envio = fields.Selection(selection=[(
        "0", "0 - Pruebas"), ("1", "1 - Homologación"), ("2", "2 - Producción")])

    # url_consulta_comprobante = fields.Char("Consulta Comprobante URL")
    # mensaje_representacion_impresa = fields.Html(
    #     "Mensaje de Representación Impresa")
