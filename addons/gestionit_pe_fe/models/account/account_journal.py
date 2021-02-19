# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from odoo.exceptions import UserError,ValidationError
from odoo.addons.gestionit_pe_fe.models.parameters.catalogs import tdc


class AccountJournal(models.Model):
    _inherit = "account.journal"
    codigo_documento = fields.Char("Codigo de tipo de Documento")
    tipo_envio = fields.Selection(selection=[("0","0 - Pruebas"),("2","2 - Producción")])
    
    resumen = fields.Boolean("Resumen Diario de Boleta",default=False)
    formato_comprobante = fields.Selection(selection=[("fisico","Físico"),("electronico","Electrónico")],default="electronico")

    invoice_type_code_id=fields.Selection(
        string="Tipo de Documento",
        selection="_selection_invoice_type")

    def _selection_invoice_type(self):
        return tdc
    
    tipo_comprobante_a_rectificar = fields.Selection(selection=[("00","Otros"),("01","Factura"),("03","Boleta")])

    # @api.constrains("code")
    # def constrains_code(self):
    #     for record in self:
    #         if record.formato_comprobante == "electronico":
    #             if record.code and record.invoice_type_code_id in ["07","08"]:
    #                 if record.code[0] == "B" and record.tipo_comprobante_a_rectificar == "03":
    #                     return 
    #                 if record.code[0] == "F" and record.tipo_comprobante_a_rectificar == "01" :
    #                     return 
    #                 raise ValidationError("Error: El campo 'código corto' o 'Comprobante a rectificar' son Erróneos")
        

    # @api.model
    # def _get_sequence_prefix(self, code, refund=False):
    #     prefix = code.upper()
    #     if refund and (self.formato_comprobante == 'electronico'):
    #         prefix=prefix[0]+'R'+prefix[2:]
    #     elif refund:
    #         prefix="R"+prefix
    #     return prefix + '-'

    # @api.model
    # def create(self, vals):
    #     if ("invoice_type_code_id" in vals) and (vals.get("formato_comprobante","") == 'electronico'):
    #         if vals["invoice_type_code_id"] in ['01','03']:
    #             if "code" in vals:
    #                 if len(vals["code"])!=4:
    #                     raise UserError("La serie debe contener 4 carácteres. Si es Factura inicia con 'F' y si es boleta inicia con 'B'")
    #                 if vals["invoice_type_code_id"]=='01':
    #                     if vals["code"][0] != 'F':
    #                         raise UserError("La serie de una factura debe iniciar con 'F'")
    #                 elif vals["invoice_type_code_id"]=='03':                    
    #                     if vals["code"][0] != 'B':
    #                         raise UserError("La serie de una factura debe iniciar con 'B'")

    #     return super(AccountJournal,self).create(vals)
    
    # @api.multi
    # def write(self, vals):
    #     if ("invoice_type_code_id" in vals) and (vals.get("formato_comprobante","") == 'electronico'):
    #         if vals["invoice_type_code_id"] in ['01','03','07','08']:
    #             if "code" in vals:
    #                 if len(vals["code"])!=4:
    #                     raise UserError("La serie debe contener 4 carácteres. Si es Factura inicia con 'F' y si es boleta inicia con 'B'")

    #                 if vals["invoice_type_code_id"]=='01':
    #                     if vals["code"][0] != 'F':
    #                         raise UserError("La serie de una factura debe iniciar con 'F'")
                            
    #                 elif vals["invoice_type_code_id"]=='03':                    
    #                     if vals["code"][0] != 'B':
    #                         raise UserError("La serie de una factura debe iniciar con 'B'")

    #     return super(AccountJournal,self).write(vals)
    
    # @api.constrains("code")
    # def _constrains_serie(self):
    #     if self.formato_comprobante == 'electronico':
            
    #         if self.invoice_type_code_id=='01':
    #             if self.code[0] != 'F':
    #                 raise UserError("La serie de una factura debe iniciar con 'F'")
    #             else:
    #                 if len(self.code)!=4:
    #                     raise UserError("La serie debe contener 4 carácteres. Si es Factura inicia con 'F' y si es boleta inicia con 'B'")

                    
    #         elif self.invoice_type_code_id=='03':                    
    #             if self.code[0] != 'B':
    #                 raise UserError("La serie de una factura debe iniciar con 'B'")
    #             else:
    #                 if len(self.code)!=4:
    #                     raise UserError("La serie debe contener 4 carácteres. Si es Factura inicia con 'F' y si es boleta inicia con 'B'")

                    
    # @api.model
    # def _create_sequence(self, vals, refund=False):
    #     """ Create new no_gap entry sequence for every new Journal"""
    #     prefix = self._get_sequence_prefix(vals['code'], refund)
    #     seq = {
    #         'name': refund and vals['name'] + _(': Refund') or vals['name'],
    #         'implementation': 'no_gap',
    #         'prefix': prefix,
    #         'padding': 8,
    #         'number_increment': 1,
    #         'use_date_range': False,
    #         'invoice_type_code_id':'08'
    #     }
    #     if 'company_id' in vals:
    #         seq['company_id'] = vals['company_id']
    #     return self.env['ir.sequence'].create(seq)
