from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning

class ResCompany(models.Model):
    _inherit = "res.company"

    property_account_receivable_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios a Cobrar",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]")

    property_account_payable_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios a Pagar",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]")

    ###############################################################
    property_account_receivable_me_id=fields.Many2one('account.account',
        string="Cuenta a cobrar ME",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        implied_group='base.group_multi_currency')

    property_account_payable_me_id=fields.Many2one('account.account',
        string="Cuenta a pagar ME",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        implied_group='base.group_multi_currency')

    property_account_receivable_me_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios a Cobrar ME",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        implied_group='base.group_multi_currency')

    property_account_payable_me_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios a Pagar ME",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        implied_group='base.group_multi_currency')