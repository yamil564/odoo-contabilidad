from odoo import fields,models,api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"
    
    invoice_journal_id = fields.Many2one("account.journal")


    def _prepare_invoice_vals(self):
        vals = super(PosOrder, self)._prepare_invoice_vals()

        if not self.invoice_journal_id:
            raise ValidationError("La creación del comprobante requiere de la selección de una Serie de facturación.")

        vals.update({
            "journal_id":self.invoice_journal_id.id,
            "invoice_type_code":self.invoice_journal_id.invoice_type_code_id
        })

        return vals

    def _order_fields(self,ui_order):
        vals = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get("invoice_journal_id",False):
            vals.update({'invoice_journal_id':ui_order.get("invoice_journal_id")})
        return vals

    def get_current_invoice(self):
        res = {"digest_value":"*"}
        for order in self:
            invoice = order.account_move
            if invoice:
                res.update({"digest_value":invoice.digest_value if invoice.digest_value else "*",
                            "name":invoice.name if invoice.digest_value else "*",
                            "invoice_portal_url":invoice.get_portal_url(report_type="pdf",download=True)})
            
            return res

    
    def get_invoice_name(self):
        self.ensure_one()
        invoice_type_names = {"01":"Factura Electrónica","03":"Boleta Electrónica","07":"Nota de Crédito"}
        invoice = self.account_move
        if invoice:
            invoice_type_name = invoice_type_names.get(invoice.invoice_type_code) or ""
            name = invoice.name
            return "{} {}".format(invoice_type_name, name)
        return ""


class l10nLatamIdentificationType(models.Model):
    _inherit = "l10n_latam.identification.type"

    available_in_pos = fields.Boolean("Disponible en POS",default=False)
