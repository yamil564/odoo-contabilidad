from odoo import fields, models,api

class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    is_national_bank_detraction = fields.Boolean("Banco de la Nación para Detracciones")
