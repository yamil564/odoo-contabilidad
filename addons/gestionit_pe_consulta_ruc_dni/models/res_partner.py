# -*- coding: utf-8 -*-
from openerp import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
import json
from io import StringIO, BytesIO
import os
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # registration_name = fields.Char('Name', size=128, index=True)
    # catalog_06_id = fields.Many2one('einvoice.catalog.06', 'Tipo Doc.', index=True)
    # tipo_documento = fields.Selection(selection="_list_tipo_documento",string="Tipo Doc.Ident.")

    # def _list_tipo_documento(self):
    #     tipo_documento_objs = self.env["einvoice.catalog.06"].sudo().search([])
    #     tipo_documento_list = [(td.code,td.name) for td in tipo_documento_objs]
    #     return tipo_documento_list

    # state = fields.Selection([('habido', 'Habido'), ('nhabido', 'No Habido'),('no_existe','No Existe')], 'Estado')
    # estado_contribuyente = fields.Selection([('activo', 'Activo'), ('noactivo', 'No Activo')], 'Estado del Contribuyente')
    # msg_error = fields.Char(readonly=True)

    def get_person_name_v3(self, dni):
        try:
            url = "https://api.migo.pe/api/v1/dni"
            token = "YFWhSoBB9PrZLXtPp2N5YrNDXsfhFGLOH0WHVOa7JoqyV4RbgxUZL8jYn5Zt"
            headers = {
                'Content-Type': 'application/json'
            }
            data = {
                "token": token,
                "dni": dni
            }
            res = requests.request(
                "POST", url, headers=headers, data=json.dumps(data))
            res = res.json()

            if res.get("success", False):
                return res.get("nombre", False)
            return None
        except Exception as e:
            return None

    @api.model
    def consulta_ruc_api(self, vat):
        user_id = self.env.context.get('uid', False)
        if user_id:
            user = self.env["res.users"].sudo().browse(user_id)
            api_ruc_endpoint = user.company_id.api_ruc_endpoint
        errors = []
        if not api_ruc_endpoint:
            errors.append("Debe configurar el end-point del API RUC")
        if len(errors) > 0:
            raise UserError("\n".join(errors))

        url = api_ruc_endpoint
        data = {"ruc": vat.strip()}
        response = requests.post(url, json=data).json()
        if "success" not in response:
            raise UserError(response['msg'])
        return response

    @api.one
    def update_document(self):
        if not self.vat:
            return False
        if self.tipo_documento == '1':
            # Valida DNI
            if self.vat:
                self.vat = self.vat.strip()
            _logger.info(self.vat)
            _logger.info(self.tipo_documento)
            if self.vat and len(self.vat) != 8:
                self.msg_error = 'El DNI debe tener 8 caracteres'
            else:
                nombre_entidad = self.get_person_name_v3(self.vat)
                if nombre_entidad:
                    self.registration_name = nombre_entidad
                    self.name = nombre_entidad
                    self.estado_contribuyente = "activo"
                else:
                    self.registration_name = " - "
                    self.name = " - "
                    self.estado_contribuyente = "noactivo"
                
        elif self.tipo_documento == '6':
            # Valida RUC
            if self.vat and len(self.vat) != 11:
                self.msg_error = "El RUC debe tener 11 carácteres"
                #raise UserError('El Ruc debe tener 11 caracteres')
            if not self._esrucvalido(self.vat):
                #raise UserError('El Ruc no es valido')
                self.msg_error = "El RUC no es Válido"
            else:
                d = self.consulta_ruc_api(self.vat)
                #d = get_data_doc(1, self.vat)
                # os.system("echo '%s'"%(json.dumps(d)))
                if not d:
                    self.name =" - "
                    return True
                if not d["success"]:
                    self.name =" - "
                    return True
                #d = d['data']
                # ~ Busca el distrito
                ditrict_obj = self.env['res.country.state']
                prov_ids = ditrict_obj.search([('name', '=', d['provincia']),
                                               ('province_id', '=', False),
                                               ('state_id', '!=', False)])
                dist_id = ditrict_obj.search([('name', '=', d['distrito']),
                                              ('province_id', '!=', False),
                                              ('state_id', '!=', False),
                                              ('province_id', 'in', [x.id for x in prov_ids])], limit=1)
                if dist_id:
                    self.district_id = dist_id.id
                    self.province_id = dist_id.province_id.id
                    self.state_id = dist_id.state_id.id
                    self.country_id = dist_id.country_id.id

                # Si es HABIDO, caso contrario es NO HABIDO
                tstate = d['condicion_de_domicilio']
                if tstate == 'HABIDO':
                    tstate = 'habido'
                else:
                    tstate = 'nhabido'
                tstate_contribuyente = d['estado_del_contribuyente']

                if tstate_contribuyente=="ACTIVO":
                    self.estado_contribuyente = "activo"
                else:
                    self.estado_contribuyente = "noactivo"

                self.state = tstate
                self.name = d['nombre']
                self.registration_name = d['nombre']
                self.zip = d["ubigeo"]
                self.street = d['direccion_completa']
                self.vat_subjected = True
                self.is_company = True
        else:
            True