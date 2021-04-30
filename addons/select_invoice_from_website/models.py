from odoo import models,fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_type_code = fields.Selection(selection=[("01","Factura Electrónica"),("03","Boleta Electrónica")])

