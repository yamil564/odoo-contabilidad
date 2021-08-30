from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_combo = fields.Boolean('Combo Product', default=False)
