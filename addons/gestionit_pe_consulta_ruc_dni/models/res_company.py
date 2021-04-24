# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = ['res.company']

    api_migo_endpoint = fields.Char(string="API Migo - Endpoint")
    api_migo_token = fields.Char(string="API Migo - Token")
