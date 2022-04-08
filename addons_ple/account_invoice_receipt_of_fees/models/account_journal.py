from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

import logging
_logger=logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_receipt_of_fees = fields.Boolean(string=" Es Recibo por Honorario?", default=False)

