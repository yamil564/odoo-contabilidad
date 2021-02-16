# -*- coding: utf-8 -*-
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError
from odoo import fields, models, api, _
from odoo.tools.profiler import profile
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from itertools import groupby
from datetime import datetime, timedelta
from werkzeug.urls import url_encode
from odoo.addons.gestionit_pe_fe.models.parameters.catalogs import tdi

import json
import time
import uuid
import os


class Partner(models.Model):
    _inherit = "res.partner"

    tipo_documento_identidad = fields.Selection(selection="_selection_tipo_documento_identidad")
    documento_identidad = fields.Char(string="Numero de documento")

    def _selection_tipo_documento_identidad(self):
        return tdi
    
    @api.onchange("company_type")
    def _onchange_company_type(self):
        if self.company_type == "company":
            self.tipo_documento_identidad = "6"
        else:
            self.tipo_documento_identidad = "1"