from odoo import models,fields

class PosConfig(models.Model):
    _inherit = "pos.config"

    
    anonymous_id = fields.Many2one('res.partner', string='Cliente Anónimo')
    module_account_invoicing = fields.Boolean("Habilitar múltiples series")
    invoice_journal_ids = fields.Many2many("account.journal",
                                            string="Series disponibles",
                                            domain=[("invoice_type_code_id","in",["01","03","07"])])