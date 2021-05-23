from odoo import fields,models

class PosOrder(models.Model):
    _inherit = "pos.order"
    
    invoice_journal_id = fields.Many2one("account.journal")


    def _prepare_invoice_vals(self):
        vals = super(PosOrder, self)._prepare_invoice_vals()

        if self.invoice_journal_id:
            raise UserError("La creación del comprobante requiere de la selección de una Serie.")

        vals.update({
            "journal_id":self.invoice_journal_id
        })

        return vals
    
