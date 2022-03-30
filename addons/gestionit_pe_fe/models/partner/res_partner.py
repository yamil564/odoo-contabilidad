# -*- coding: utf-8 -*-
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError
from odoo import fields, models, api, _
import logging
import re
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains('vat','l10n_latam_identification_type_id', 'name', 'registration_name', 'estado_contribuyente')
    def _check_limitation_partners(self):
        for record in self:
            check_flag = self.env.context.get('check_flag', False)
            group_change_partner = self.env.ref('gestionit_pe_fe.res_groups_change_partners')
            if check_flag is False:
                if self.env.uid in group_change_partner.users.ids:
                    if record.total_invoiced:
                        raise UserError("No puede modificar datos de un contacto que ya ha completado alguna factura.")

    @api.model
    def default_get(self,field_list):
        res = super(ResPartner, self).default_get(field_list)
        if self.env.context.get("parent_id"):
            res.update({"parent_id": self.env.context.get("parent_id")})
        return res

    def create_address_contact(self):

        self.create({
            'parent_id': self.id,
            'name': self.name+' - Entrega',
            'type': 'other',
            'street': self.street,
            'company_type': 'person',
            'ubigeo': self.ubigeo,
            'district_id': self.district_id.id,
            'province_id':self.province_id.id,
            'state_id':self.state_id.id,
            'country_id':self.country_id.id
        })
