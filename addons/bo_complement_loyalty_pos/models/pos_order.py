from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
import pytz
import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    desc_global = fields.Float(string="Descuento global", default=0)

    def _prepare_invoice_line(self, order_line):
        if order_line.price_unit*order_line.qty > 0:
            return {
                'product_id': order_line.product_id.id,
                'quantity': order_line.qty if self.amount_total >= 0 else -order_line.qty,
                'discount': order_line.discount,
                'price_unit': order_line.price_unit,
                'name': order_line.product_id.display_name,
                'tax_ids': [(6, 0, order_line.tax_ids_after_fiscal_position.ids)],
                'product_uom_id': order_line.product_uom_id.id,
                'lot_name': ",".join(order_line.pack_lot_ids.mapped('lot_name'))
            }
        else:
            self.desc_global += abs(order_line.qty*order_line.price_unit)

    # def _prepare_invoice_vals(self):
    #     vals = super(PosOrder, self)._prepare_invoice_vals()

    #     desc_percent = (abs(self.desc_global)*100) / \
    #         (abs(self.desc_global)+self.amount_total)

    #     vals.update({
    #         'invoice_line_ids': [(0, None, self._prepare_invoice_line(line)) for line in self.lines if line.price_unit*line.qty > 0],
    #         "apply_global_discount": True if abs(desc_percent) > 0 else False,
    #         "descuento_global": abs(desc_percent)
    #     })

    # def _prepare_invoice_vals(self):
    #     self.ensure_one()
    #     timezone = pytz.timezone(self._context.get(
    #         'tz') or self.env.user.tz or 'UTC')
    #     desc_percent = (abs(self.desc_global)*100) / \
    #         (abs(self.desc_global)+self.amount_total)
    #     vals = {
    #         'invoice_payment_ref': self.name,
    #         'invoice_origin': self.name,
    #         'journal_id': self.session_id.config_id.invoice_journal_id.id,
    #         'type': 'out_invoice' if self.amount_total >= 0 else 'out_refund',
    #         'ref': self.name,
    #         'partner_id': self.partner_id.id,
    #         'narration': self.note or '',
    #         # considering partner's sale pricelist's currency
    #         'currency_id': self.pricelist_id.currency_id.id,
    #         'invoice_user_id': self.user_id.id,
    #         'invoice_date': self.date_order.astimezone(timezone).date(),
    #         'fiscal_position_id': self.fiscal_position_id.id,
    #         'invoice_line_ids': [(0, None, self._prepare_invoice_line(line)) for line in self.lines if line.price_unit*line.qty > 0], "apply_global_discount": True if abs(desc_percent) > 0 else False,
    #         "descuento_global": abs(desc_percent)
    #     }
    #     return vals
