# -*- coding: utf-8 -*-
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError
from odoo import fields, models, api, _
import logging
import re
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains('vat','l10n_latam_identification_type_id')
    def _check_limitation_partners(self):
        for record in self:
            company = self.env['res.company'].browse(self.env.company.id)
            if company.limit_change_contacts:
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
            'ubigeo': self.ubigeo
        })
