from odoo import fields,models
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"
    
    invoice_journal_id = fields.Many2one("account.journal")


    def _prepare_invoice_vals(self):
        vals = super(PosOrder, self)._prepare_invoice_vals()

        if not self.invoice_journal_id:
            raise ValidationError("La creación del comprobante requiere de la selección de una Serie.")

        vals.update({
            "journal_id":self.invoice_journal_id.id
        })

        return vals

    def _order_fields(self,ui_order):
        vals = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get("invoice_journal_id",False):
            vals.update({'invoice_journal_id':ui_order.get("invoice_journal_id")})

        _logger.info(vals)
        return vals


class l10nLatamIdentificationType(models.Model):
    _inherit = "l10n_latam.identification.type"

    available_in_pos = fields.Boolean("Disponible en POS",default=False)
