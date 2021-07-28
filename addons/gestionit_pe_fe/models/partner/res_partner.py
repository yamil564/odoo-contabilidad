# -*- coding: utf-8 -*-
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError
from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    def create_address_contact(self):
        
        self.create({
            'parent_id': self.id,
            'name': self.name+' - Entrega',
            'type': 'other',
            'street': self.street,
            'company_type': 'person',
            'ubigeo': self.ubigeo
        })

#     def write():
#         return super(resPartner, self).write(values)
