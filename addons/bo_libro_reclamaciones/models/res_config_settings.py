# -*- coding: utf-8 -*-
from odoo import fields,models

class ResCompany(models.Model):
    _inherit = "res.company"

    default_claim_sequence_id = fields.Many2one("ir.sequence",string="Secuencia de reclamo")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    claim_sequence_id = fields.Many2one("ir.sequence",related="company_id.default_claim_sequence_id",readonly=False)