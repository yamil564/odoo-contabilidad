from odoo import models,api,fields

class SunatCatalog(models.Model):
    _name = "sunat.catalog.54"
    _description = "Códigos de bienes y servicios sujetos a detracciones"

    active = fields.Boolean("Activo",default=True)
    name = fields.Char("Descripción")
    code = fields.Char("Código")
    rate = fields.Float("Tasa %")


