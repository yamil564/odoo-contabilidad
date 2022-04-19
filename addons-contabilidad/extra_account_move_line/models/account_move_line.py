# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError
import logging
_logger=logging.getLogger(__name__)

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	prefix_code=fields.Char(string="N°Serie")
	invoice_number=fields.Char(string="Número Documento")
	type_document_id = fields.Many2one('sunat.catalog.10', string="Tipo de Documento")
	date_emission = fields.Date(string="Fecha de Emisión")