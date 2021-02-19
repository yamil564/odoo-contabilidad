# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = ['res.company']

    api_ruc_endpoint = fields.Char("end-point")
    api_ruc_username = fields.Char("API RUC USERNAME")
    api_ruc_password = fields.Char("API RUC PASSWORD")
