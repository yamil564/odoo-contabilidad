from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

import logging
_logger=logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    fees_account_payable_id = fields.Many2one('account.account',string="Cuenta Honorarios a Pagar")
    fees_account_payable_me_id = fields.Many2one('account.account',string="Cuenta Honorarios a Pagar en ME")

