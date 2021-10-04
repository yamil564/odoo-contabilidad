from odoo import models,fields,api
from odoo.exceptions import UserError

class PaymenttermLine(models.Model):
    _name = "paymentterm.line"
    _order = "date_due ASC"
    
    currency_id = fields.Many2one("res.currency",related="move_id.currency_id")
    move_id = fields.Many2one("account.move","Account Move")
    date_due = fields.Date("Fecha de vencimiento")
    amount = fields.Float("Monto")

    @api.constrains("move_id")
    def check_move_id(self):
        for record in self:
            if record.move_id:
                if record.move_id.invoice_payment_term_id:
                    if record.move_id.invoice_payment_term_id.type != "Credito":
                        raise UserError("Si la factura tiene líneas de plazos de pago, entonces su término de pago debe ser uno de tipo Crédito.")
                else:
                    raise UserError("Si la factura tiene líneas de plazos de pago, entonces su término de pago debe ser uno de tipo Crédito.")

    


