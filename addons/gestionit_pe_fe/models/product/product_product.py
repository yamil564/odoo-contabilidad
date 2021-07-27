from odoo import fields,models,api

class ProductProduct(models.Model):
    _inherit = "product.product"
    
    is_charge_or_discount = fields.Boolean(related="product_tmpl_id.is_charge_or_discount")
    type_charge_or_discount_id = fields.Many2one("sunat.catalog.53",related="product_tmpl_id.type_charge_or_discount_id",readonly=False)

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    is_charge_or_discount = fields.Boolean("Es un cargo, descuento u otra deducción?",default=False)
    type_charge_or_discount_id = fields.Many2one("sunat.catalog.53",string="Código de Cargo, Descuento u Otra Deducción",readonly=False)
    

