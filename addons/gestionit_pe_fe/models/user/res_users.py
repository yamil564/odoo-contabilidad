# -*- coding: utf-8 -*-
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError
from odoo import fields, models, api, _


class Users(models.Model):
    _inherit = "res.users"

    warehouse_ids = fields.Many2many('stock.warehouse', string='Almacenes')
