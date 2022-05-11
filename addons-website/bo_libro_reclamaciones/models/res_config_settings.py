# -*- coding: utf-8 -*-
from odoo import fields,models

class ResCompany(models.Model):
    _inherit = "res.company"

    default_claim_sequence_id = fields.Many2one("ir.sequence",string="Secuencia de reclamo")
    default_claim_user_id = fields.Many2one("res.users",string="Responsable de Reclamos y Quejas")

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    claim_sequence_id = fields.Many2one("ir.sequence",related="company_id.default_claim_sequence_id",readonly=False)
    claim_user_id = fields.Many2one("res.users",related="company_id.default_claim_user_id",readonly=False)