# -*- coding: utf-8 -*-
from openerp import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
import json
from io import StringIO, BytesIO
import os
import logging
import re
_logger = logging.getLogger(__name__)

patron_ruc = re.compile("[12]\d{10}$")
patron_dni = re.compile("\d{8}$")


class ResPartner(models.Model):
    _inherit = "res.partner"

    registration_name = fields.Char('Name', size=128, index=True)
    estado_contribuyente = fields.Char(string='Estado del Contribuyente')
    msg_error = fields.Char(readonly=True)

    l10n_latam_identification_type_id = fields.Many2one('l10n_latam.identification.type',
                                                        string="Tipo de documento de identificación", index=True, auto_join=True,
                                                        default=lambda self: self.env.ref('gestionit_pe_consulta_ruc_dni.it_RUC', raise_if_not_found=False),
                                                        help="Tipo de documento de identificación")
    
    street_invoice_ids = fields.One2many("res.partner","parent_id",string="Facturación",domain=[("type","=","invoice")])
    street_delivery_ids = fields.One2many("res.partner","parent_id",string="Direcciones",domain=[("type","in",["delivery","other","private"])])

    @api.model
    def default_get(self,field_list):
        res = super(ResPartner, self).default_get(field_list)
        if self.env.context.get("no_doc"):
            res.update({"l10n_latam_identification_type_id": self.env.ref("l10n_pe.it_NDTD").id,"vat":"0"})
        return res

    def _get_name(self):
        partner = self
        name = partner.name or ''
        name = super(ResPartner, self)._get_name()
        if self._context.get("show_vat_first") and partner.vat:
            name = "%s ‒ %s" % (partner.vat, name)
        return name

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        return super(ResPartner, self).with_context(show_vat=True).onchange_partner_id()


    @api.model
    def _commercial_fields(self):
        return []
        
    @api.constrains('vat','l10n_latam_identification_type_id')
    def _check_valid_numero_documento(self):
        vat_str = (self.vat or "").strip()
        if self.l10n_latam_identification_type_id and self.type in ["contact","invoice"]:
            if self.l10n_latam_identification_type_id.l10n_pe_vat_code == "6":
                if patron_ruc.match(vat_str):
                    vat_arr = [int(c) for c in vat_str]
                    arr = [5,4,3,2,7,6,5,4,3,2]
                    s = sum([vat_arr[r]*arr[r] for r in range(0,10)])
                    num_ver = (11-s%11)%10
                    if vat_arr[10] != num_ver:
                        raise UserError("El número de RUC ingresado es inválido.")
                else:
                    raise UserError("El número de RUC ingresado es inválido.")

            if self.l10n_latam_identification_type_id.l10n_pe_vat_code == "1":
                if not patron_dni.match(vat_str):
                    raise UserError("El número de DNI ingresado es inválido")

    @api.onchange("street","type")
    def get_name_street(self):
        if self.type == "delivery" and not self.name:
            self.name = self.street or "-"


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

    def _esrucvalido(self, vat_str):
        if patron_ruc.match(vat_str):
            vat_arr = [int(c) for c in vat_str]
            arr = [5,4,3,2,7,6,5,4,3,2]
            s = sum([vat_arr[r]*arr[r] for r in range(0,10)])
            num_ver = (11-s%11)%10
            if vat_arr[10] != num_ver:
                return False
            return True
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
