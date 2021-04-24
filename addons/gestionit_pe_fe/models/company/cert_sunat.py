# -*- coding: utf-8 -*-
from odoo import api, models, fields


class certSunat(models.Model):
    _name = "cert.sunat"

    key_public = fields.Text("Cert. PUBLIC")
    key_private = fields.Text("Cert. PRIVATE")
    expiration_date = fields.Date(string='Fecha de expiración')
    issue_date = fields.Date(string='Fecha de emisión')
    active = fields.Boolean(string="Activo", default=True)
