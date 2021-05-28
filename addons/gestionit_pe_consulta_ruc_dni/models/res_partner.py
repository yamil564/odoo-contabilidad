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
    estado_contribuyente = fields.Char(string='Estado del Contribuyente')
    msg_error = fields.Char(readonly=True)

    l10n_latam_identification_type_id = fields.Many2one('l10n_latam.identification.type',
                                                        string="Tipo de documento de identificación", index=True, auto_join=True,
                                                        default=lambda self: self.env.ref(
                                                            'l10n_pe.it_RUC', raise_if_not_found=False),
                                                        help="Tipo de documento de identificación")
    
    @api.onchange('l10n_latam_identification_type_id', 'vat')
    def vat_change(self):
        self.update_document()

    @api.model
    def request_migo_dni(self, dni):
        user_id = self.env.context.get('uid', False)
        if user_id:
            user = self.env["res.users"].sudo().browse(user_id)
            url = user.company_id.api_migo_endpoint + "dni"
            token = user.company_id.api_migo_token
        try:
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
    def request_migo_ruc(self, ruc):
        user_id = self.env.context.get('uid', False)
        errors = []

        if user_id:
            user = self.env["res.users"].sudo().browse(user_id)

            if not user.company_id.api_migo_endpoint:
                errors.append("Debe configurar el end-point del API")
            if not user.company_id.api_migo_token:
                errors.append("Debe configurar el token del API")
            if len(errors) > 0:
                raise UserError("\n".join(errors))
            else:
                url = user.company_id.api_migo_endpoint + "ruc"
                token = user.company_id.api_migo_token

                try:
                    headers = {
                        'Content-Type': 'application/json'
                    }
                    data = {
                        "token": token,
                        "ruc": ruc
                    }
                    res = requests.request(
                        "POST", url, headers=headers, data=json.dumps(data))
                    res = res.json()

                    if res.get("success", False):
                        return res
                    return None
                except Exception as e:
                    return None

        return None

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
            # if not self._esrucvalido(self.vat):
            #     self.msg_error = "El DNI no es Válido"
            else:
                nombre_entidad = self.request_migo_dni(self.vat)
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
                d = self.request_migo_ruc(self.vat)
                _logger.info(d)           
                if not d:
                    self.name = " - "
                    return True
                if not d["success"]:
                    self.name = " - "
                    return True

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

                
                self.estado_contribuyente = d['estado_del_contribuyente']

                self.name = d['nombre_o_razon_social']
                self.registration_name = d['nombre_o_razon_social']
                self.ubigeo = d["ubigeo"]
                self.street = d['direccion']
                self.is_company = True
                self.company_type = "company"
        else:
            True

    def _onchange_country(self):
        return
