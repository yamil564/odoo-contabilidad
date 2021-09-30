from odoo import models,fields,api

class PaymenttermLine(models.Model):
    _name = "paymentterm.line"
    _order = "date_due ASC"
    
    move_id = fields.Many2one("account.move","Account Move")
    date_due = fields.Date("Fecha de vencimiento")
    amount = fields.Float("Monto")
    


