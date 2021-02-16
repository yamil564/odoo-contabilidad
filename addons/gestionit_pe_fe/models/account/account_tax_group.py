# -*- coding: utf-8 -*-
from odoo import fields,models,api

class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    code = fields.Char("Código")
    description = fields.Char("Descripción")
    name_code = fields.Char("Nombre del Código")
