import logging
from odoo import api, models, _, fields
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)

class LibroReclamaciones(models.Model):
    _name = "libro.reclamaciones"
    _description = "Libro de reclamaciones"
    _inherit = ['mail.thread']

    state = fields.Selection(string="Estado",selection=[('new','Nuevo'),
                                                        ('in_process','En proceso'),
                                                        ('cancel','Cancelado'),
                                                        ('resolved','Resuelto')],default="new")

    # IDENTIFICACIÓN DEL CONSUMIDOR RECLAMANTE
    consumer_type = fields.Selection(selection=[('individual','Persona Natural'),('company','Empresa')],string="Tipo de consumidor",default="individual")
    consumer_company_name = fields.Char(string="Razón Social")
    consumer_company_document = fields.Char(string="N° R.U.C.")

    consumer_name = fields.Char(string="Nombres")
    consumer_lastname = fields.Char(string="Apellidos")
    consumer_email = fields.Char(string="E-mail")
    consumer_document_type = fields.Selection(string="Tipo de documento de Identidad",selection=[('1','DNI'),('4','CE'),('7','Pasaporte')],default="1")
    consumer_document = fields.Char(string="Número de documento")
    consumer_phone = fields.Char(string="Teléfono")
    consumer_address = fields.Char(string="Dirección")
    
    consumer_country_id = fields.Many2one("res.country",default=lambda r:r.env.ref("base.pe",raise_if_not_found=False))
    consumer_state_id = fields.Many2one("res.country.state",string="Departamento")
    consumer_province_id = fields.Many2one("res.country.state",string="Provincia")
    consumer_district_id = fields.Many2one("res.country.state",string="Distrito")

    # DATOS DEL PADRE, MADRE O TUTOR
    consumer_younger = fields.Boolean(string="Es menor de edad?",default=False)
    consumer_younger_name = fields.Char(string="Nombres")
    consumer_younger_lastname = fields.Char(string="Apellidos")
    consumer_younger_document = fields.Char(string="DNI/CE")

    # IDENTIFICACIÓN DEL BIEN CONTRATADO
    product_type = fields.Selection(string="Tipo de producto",selection=[('product','Producto'),('service','Servicio')],default="product")
    product_code = fields.Char(string="Código de producto")
    order_name = fields.Char(string="Número de órden de venta")
    date_order = fields.Date(string="Fecha de venta")
    product_name = fields.Char(string="Nombre de producto")

    # DETALLE DE RECLAMO O QUEJA
    claim_type = fields.Selection(string="Tipo de reclamación",selection=[('reclamo','Reclamo'),('queja','Queja')],default="reclamo")
    claim_amount = fields.Float(string="Monto reclamado")
    claim_detail = fields.Text(string="Detalle de reclamo")
    claim_request = fields.Text(string="Solicitud de reclamo")
    company_id = fields.Many2one("res.company",default=lambda self:self.env.company)

    name = fields.Char("Número de Reclamo")
    
    @api.model
    def create(self,vals):
        result = super(LibroReclamaciones, self).create(vals)
        if not self.env.company.default_claim_sequence_id:
            raise UserError("La secuencia del reclamo no se encuentra configurada, comuníquese con su administrador.")
        name = self.env.company.default_claim_sequence_id.next_by_id()
        result.update({"name":name})
        return result
