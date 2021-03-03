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

    registration_name = fields.Char('Name', size=128, index=True)
    ubigeo = fields.Char('Ubigeo')
    estado_contribuyente = fields.Selection(selection=[(
        'activo', 'Activo'), ('noactivo', 'No Activo')], string='Estado del Contribuyente')
    msg_error = fields.Char(readonly=True)

    @api.onchange('l10n_latam_identification_type_id', 'vat')
    def vat_change(self):
        self.update_document()

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

    def _esrucvalido(self, dato):
        largo_dato = len(dato)
        if dato is not None and dato != "" and dato.isdigit() and (largo_dato == 11 or largo_dato == 8):
            valor = int(dato)
            if largo_dato == 8:
                suma = 0
                for i in range(largo_dato - 1):
                    digito = int(dato[i]) - 0
                    if i == 0:
                        suma = suma + digito * 2
                    else:
                        suma = suma + digito * (largo_dato - 1)
                    resto = suma % 11
                    if resto == 1:
                        resto = 11
                    if (resto + int(dato[largo_dato - 1]) - 0) == 11:
                        return True
            elif largo_dato == 11:
                suma = 0
                x = 6
                for i in range(largo_dato - 1):
                    if i == 4:
                        x = 8
                    digito = int(dato[i]) - 0
                    x = x - 1
                    if x == 0:
                        suma = suma + digito * x
                    else:
                        suma = suma + digito * x
                resto = suma % 11
                resto = 11 - resto
                if resto >= 10:
                    resto = resto - 10
                if resto == int(dato[largo_dato - 1]) - 0:
                    return True

            return False
        else:
            return False

    # @api.one
    def update_document(self):
        self.ensure_one()
        if not self.vat:
            return False
        if self.l10n_latam_identification_type_id.l10n_pe_vat_code == '1':
            # Valida DNI
            if self.vat:
                self.vat = self.vat.strip()
            if self.vat and len(self.vat) != 8:
                self.msg_error = 'El DNI debe tener 8 caracteres'
            if not self._esrucvalido(self.vat):
                self.msg_error = "El DNI no es Válido"
            else:
                nombre_entidad = self.get_person_name_v3(self.vat)
                if nombre_entidad:
                    self.name = nombre_entidad
                    self.registration_name = nombre_entidad
                    # self.district_id = ""
                    # self.province_id = ""
                    # self.state_id = ""
                    # self.country_id = ""
                    # self.zip = ""
                    # self.street = ""
                else:
                    self.name = " - "
                    self.registration_name = " - "
                    # self.district_id = ""
                    # self.province_id = ""
                    # self.state_id = ""
                    # self.country_id = ""
                    # self.zip = ""
                    # self.street = ""

        elif self.l10n_latam_identification_type_id.l10n_pe_vat_code == '6':
            # Valida RUC
            if self.vat and len(self.vat) != 11:
                self.msg_error = "El RUC debe tener 11 carácteres"
            if not self._esrucvalido(self.vat):
                self.msg_error = "El RUC no es Válido"
            else:
                d = self.consulta_ruc_api(self.vat)
                if not d:
                    self.name = " - "
                    return True
                if not d["success"]:
                    self.name = " - "
                    return True
                #d = d['data']
                # ~ Busca el distrito
                # _logger.info(d)
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
                # tstate = d['condicion_de_domicilio']
                # if tstate == 'HABIDO':
                #     tstate = 'habido'
                # else:
                #     tstate = 'nhabido'

                tstate_contribuyente = d['estado_del_contribuyente']

                # if tstate_contribuyente == "ACTIVO":
                #     self.estado_contribuyente = "activo"
                # else:
                #     self.estado_contribuyente = "noactivo"

                # self.state = tstate
                self.name = d['nombre']
                self.registration_name = d['nombre']
                self.ubigeo = d["ubigeo"]
                self.street = d['direccion_completa']
                # self.vat_subjected = True
                self.is_company = True
                self.company_type = "company"
        else:
            True

    def _onchange_country(self):
        return
