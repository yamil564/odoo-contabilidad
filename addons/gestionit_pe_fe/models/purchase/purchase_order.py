from odoo import models,api,fields
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_view_invoice(self):
        res = super(PurchaseOrder, self).action_view_invoice()
        res["context"].update({"default_invoice_type_code":"01","default_journal_type":"purchase"})
        # _logger.info(res)
        return res