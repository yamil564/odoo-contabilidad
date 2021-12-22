from odoo import models, api, fields
import re
from odoo.exceptions import UserError, ValidationError

patron_dni = re.compile("\d{8}$")
patron_ruc = re.compile("[12]\d{10}$")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def emitir_factura(self):
        self.ensure_one()
        if not(self.partner_invoice_id.l10n_latam_identification_type_id.l10n_pe_vat_code == "6" and patron_ruc.match(self.partner_invoice_id.vat or "")):
            raise UserError(
                "Para emitir una Factura entonces la dirección de Facturación debe tener el tipo de documento como RUC y su valor debe ser válido")

        if len(self.invoice_ids) == 0:
            self.tipo_documento = "01"
            # self.action_invoice_create(final=True)
            move = self._create_invoices(final=True)
            move._onchange_invoice_line_ids()

        return self.action_view_invoice()

    def emitir_boleta(self):
        self.ensure_one()
        if not(self.partner_invoice_id.l10n_latam_identification_type_id.l10n_pe_vat_code in ["0", "1", "4"]):
            raise UserError(
                "Para Emitir una Boleta la dirección de Facturación debe tener alguno de estos tipo de documentos 'DNI', 'DOC.TRIB.NO.DOM.SIN.RUC', 'Carnet de Extranjería' y su valor debe ser válido.")

        if self.partner_invoice_id.l10n_latam_identification_type_id.l10n_pe_vat_code == "0":
            if not patron_dni.match(self.partner_invoice_id.vat or ""):
                raise UserError("El número de dni del cliente es erróneo")

        if len(self.invoice_ids) == 0:
            self.tipo_documento = "03"
            move = self._create_invoices(final=True)
            move._onchange_invoice_line_ids()
        return self.action_view_invoice()
