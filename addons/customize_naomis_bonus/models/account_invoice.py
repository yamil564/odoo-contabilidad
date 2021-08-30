from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class accountInvoice(models.Model):
    _inherit = "account.invoice"

    observacion = fields.Text(string="Observaciones")
