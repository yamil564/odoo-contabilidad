from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import re

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_property_account_receivable_fees_id(self):
        default=self.env['res.company']._company_default_get().property_account_receivable_fees_id.id
        return default

    @api.model
    def get_property_account_payable_fees_id(self):
        default=self.env['res.company']._company_default_get().property_account_payable_fees_id.id
        return default


    @api.model
    def get_property_account_receivable_me_id(self):
        default=self.env['res.company']._company_default_get().property_account_receivable_me_id.id
        return default

    @api.model
    def get_property_account_payable_me_id(self):
        default=self.env['res.company']._company_default_get().property_account_payable_me_id.id
        return default


    @api.model
    def get_property_account_receivable_me_fees_id(self):
        default=self.env['res.company']._company_default_get().property_account_receivable_me_fees_id.id
        return default

    @api.model
    def get_property_account_payable_me_fees_id(self):
        default=self.env['res.company']._company_default_get().property_account_payable_me_fees_id.id
        return default
    

    massive_update_account_fees = fields.Boolean(string="Sujeto a actualización Masiva de cuentas de Recibo Honorario", default=True)

    property_account_receivable_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios a Cobrar",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        default=get_property_account_receivable_fees_id
        )

    property_account_payable_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios a Pagar",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        default=get_property_account_payable_fees_id
        )

    ######################################################
    massive_update_account_me = fields.Boolean(string="Sujeto a actualización Masiva de cuentas en ME", default=True)
    
    property_account_receivable_me_id=fields.Many2one('account.account',
        string="Cuenta a cobrar ME",
        implied_group='base.group_multi_currency',
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        default=get_property_account_receivable_me_id)

    property_account_payable_me_id=fields.Many2one('account.account',
        string="Cuenta a pagar ME",
        implied_group='base.group_multi_currency',
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        default=get_property_account_payable_me_id
        )


    massive_update_account_fees_me = fields.Boolean(string="Sujeto a actualización Masiva de cuentas de Recibo Honorario en ME", default=True)

    property_account_receivable_me_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios a Cobrar ME",
        implied_group='base.group_multi_currency',readonly=False,
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        default=get_property_account_receivable_me_fees_id)

    property_account_payable_me_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios a Pagar ME",
        implied_group='base.group_multi_currency',readonly=False,
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        default=get_property_account_payable_me_fees_id)


    @api.model
    def _commercial_fields(self):
        return super(ResPartner, self)._commercial_fields() + \
            ['property_account_receivable_me_id', 'property_account_payable_me_id',
                'property_account_receivable_fees_id', 'property_account_payable_fees_id',
                'property_account_receivable_me_fees_id', 'property_account_payable_me_fees_id']
