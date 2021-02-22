# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.tools import float_is_zero, float_compare
from odoo.http import request
from ..auth import oauth
from ..auth.oauth import consulta_estado_comprobante, consulta_comprobante, consultar_validez_comprobante
import os
import site
import json
import ast
import base64
import io
import re
from datetime import datetime
from ..utils.number_to_letter import to_word
from odoo.tools.profiler import profile
import logging

_logger = logging.getLogger(__name__)
patron_dni = re.compile("\d{8}$")
patron_ruc = re.compile("[12]\d{10}$")

codigos_tipo_afectacion_igv = [
    "10", "11", "12", "13", "14", "15", "16", "20", "30", "31", "34", "35", "36", "40"
]

codigo_unidades_de_medida = [
    "DZN",
    "DAY",
    "HUR",
    "LTR",
    "NIU",
    "CMT",
    "GLL",
    "OZI",
    "GRM",
    "GLL",
    "KGM",
    "LBR",
    "MTR",
    "LBR",
    "SMI",
    "ONZ",
    "FOT",
    "INH",
    "LTN",
    "BX"
]

TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}
estado_comprobante_electronico = {
    "0": "0_NO_EXISTE",
    "1": "1_ACEPTADO",
    "2": "2_ANULADO",
    "3": "3_AUTORIZADO",
    "4": "4_NO_AUTORIZADO"
}
estado_contribuyente_ruc = {
    "00": "00_ACTIVO",
    "01": "01_BAJA_PROVISIONAL",
    "02": "02_BAJA_PROV_POR_OFICIO",
    "03": "03_SUSPENSION_TEMPORAL",
    "10": "10_BAJA_DEFINITIVA",
    "11": "11_BAJA_DE_OFICIO",
    "22": "22_INHABILITADO-VENT.UNICA"
}

condicion_domicilio_contribuyente = {
    "00": "00_HABIDO",
    "09": "09_PENDIENTE",
    "11": "11_POR_VERIFICAR",
    "12": "12_NO_HABIDO",
    "20": "20_NO_HALLADO"
}


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    account_log_status_ids = fields.One2many(
        "account.log.status", "account_invoice_id", string="Registro de Envíos", copy=False)

    estado_comprobante_electronico = fields.Selection(selection=[("0_NO_EXISTE", "NO EXISTE"),
                                                                 ("1_ACEPTADO",
                                                                  "ACEPTADO"),
                                                                 ("2_ANULADO",
                                                                  "ANULADO"),
                                                                 ("3_AUTORIZADO",
                                                                  "AUTORIZADO"),
                                                                 ("4_NO_AUTORIZADO",
                                                                  "NO AUTORIZADO"),
                                                                 ("-", "-")], default="-")

    estado_contribuyente_ruc = fields.Selection(selection=[("00_ACTIVO", "ACTIVO"),
                                                           ("01_BAJA_PROVISIONAL",
                                                            "BAJA PROVISIONAL"),
                                                           ("02_BAJA_PROV_POR_OFICIO",
                                                            "BAJA PROV. POR OFICIO"),
                                                           ("03_SUSPENSION_TEMPORAL",
                                                            "SUSPENSION TEMPORAL"),
                                                           ("10_BAJA_DEFINITIVA",
                                                            "BAJA DEFINITIVA"),
                                                           ("11_BAJA_DE_OFICIO",
                                                            "BAJA DE OFICIO"),
                                                           ("22_INHABILITADO-VENT.UNICA",
                                                            "INHABILITADO-VENT.UNICA"),
                                                           ("-", "-")], default="-")

    condicion_domicilio_contribuyente = fields.Selection(selection=[("00_HABIDO", "HABIDO"),
                                                                    ("09_PENDIENTE",
                                                                     "PENDIENTE"),
                                                                    ("11_POR_VERIFICAR",
                                                                     "POR VERIFICAR"),
                                                                    ("12_NO_HABIDO",
                                                                     "NO HABIDO"),
                                                                    ("20_NO_HALLADO",
                                                                     "NO HALLADO"),
                                                                    ("-", "-")], default="-")

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        change_default=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='always')

    json_comprobante = fields.Text(string="JSON Comprobante", copy=False)
    json_respuesta = fields.Text(string="JSON Respuesta", copy=False)
    digest_value = fields.Char(string="Digest Value", copy=False, default="*")
    status_envio = fields.Boolean(
        string="Estado del envio del documento",
        default=False,
        copy=False
    )
    status_baja = fields.Boolean(
        string="Estado de la baja del documento",
        default=False,
        copy=False
    )
    # variables para notas de venta
    sustento_nota = fields.Text(
        string="Sustento de nota",
        readonly=True,
        states={
            'draft': [
                ('readonly', False)
            ]
        },
        copy=False)

    def action_invoice_cancel(self):
        res = super(AccountInvoice, self).action_invoice_cancel()
        if self.estado_comprobante_electronico not in ["0_NO_EXISTE", "-", False] or self.estado_emision in ["A"]:
            raise UserError(
                "Sólo puedes cancelar comprobantes que aún no han sido Aceptados por SUNAT")
        return res

    @api.depends("amount_total")
    def _compute_monto_en_letras(self):
        for record in self:
            record.monto_en_letras = to_word(
                record.amount_total, record.currency_id.name)

    monto_en_letras = fields.Char(
        "Monto en letras", compute=_compute_monto_en_letras)
    tiene_guia_remision = fields.Boolean(
        "Tienes guía de Remisión", default=False, copy=False)
    invoice_picking_id = fields.Many2one(
        "stock.picking", string="Documento de Envío", copy=False)
    stock_picking_id = fields.Many2one(
        "stock.picking", string="Documento de Envío", copy=False)
    numero_guia = fields.Char(
        "Número de Guía", related="invoice_picking_id.numero_guia", copy=False)
    numero_guia_remision = fields.Char(
        "Número de Guía de Remisión", copy=False)

    guia_remision_ids = fields.Many2many(
        "efact.guia_remision", string="Guía de Remisión")
    guia_remision_count = fields.Integer(
        "Cantidad de GRE", compute="_compute_guia_remision_count")

    @api.multi
    def _compute_guia_remision_count(self):
        for record in self:
            record.guia_remision_count = len(record.guia_remision_ids)

    tipo_comprobante_elect_ref = fields.Selection(
        related="refund_invoice_id.invoice_type_code")

    tipo_comprobante_ref = fields.Selection(
        selection=[("01", "Factura"), ("03", "Boleta")], default="01")
    formato_comprobante_ref = fields.Selection(selection=[(
        "fisico", "Físico"), ("electronico", "Electrónico")], default="electronico")
    comprobante_fisico_ref = fields.Char("Comprobante Físico Ref.")
    fecha_emision_comprobante_fisico_ref = fields.Date(
        "Fecha emisión de Comprobante Físico")

    tipo_operacion = fields.Selection(selection=[(
        "01", "Venta Interna"), ("02", "Exportación")], default="01", required=True, copy=False)
    #("04","Venta Interna - Anticipos"),("05","Venta Itinerante")

    nota_id = fields.Many2one("efact.invoice_nota", string="Nota", states={
                              'draft': [('readonly', False)]})

    @api.multi
    def name_get(self):
        TYPES = {
            'out_invoice': _('Invoice'),
            'in_invoice': _('Vendor Bill'),
            'out_refund': _('Credit Note'),
            'in_refund': _('Vendor Credit note'),
        }
        result = []
        for inv in self:
            name = TYPES[inv.type]
            if inv.type == "out_invoice" and inv.invoice_type_code == "03":
                name = "Boleta"
            elif inv.type == "out_invoice" and inv.invoice_type_code == "01":
                name = "Factura"

            result.append((inv.id, "%s %s" %
                           (inv.number or name, inv.name or '')))
        return result

    @api.onchange("tiene_guia_remision")
    def _set_default_tiene_guia_remision(self):
        for record in self:
            if not record.tiene_guia_remision:
                record.invoice_picking_id = False
                record.numero_guia = False

    # tipo_nota
    reference_id = fields.Many2one(
        'account.invoice',
        string='Documento de Referencia',
        change_default=True,
        readonly=True,
        states={
            'draft': [
                ('readonly', False)
            ]},
        track_visibility='always')
    tipo_nota_credito = fields.Many2one(
        'einvoice.catalog.09',
        string='Tipo de Nota de Credito',
        readonly=True,
        states={
            'draft': [
                ('readonly', False)
            ]})
    tipo_nota_dedito = fields.Many2one(
        'einvoice.catalog.10',
        string='Tipo de Nota de Debito',
        readonly=True,
        states={
            'draft': [
                ('readonly', False)
            ]})
    documento_baja_id = fields.Many2one(
        "efact.account_comunicacion_baja", copy=False)
    documento_baja_state = fields.Selection(
        string="Estado del Documento de Baja", related="documento_baja_id.state", copy=False)

    resumen_anulacion_id = fields.Many2one("account.summary", copy=False)
    resumen_anulacion_state = fields.Selection(
        related="resumen_anulacion_id.estado_emision", copy=False)

    anulacion_comprobante = fields.Char(
        "Anulación de Comprobante", compute="_compute_obtener_estado_anulacion_comprobante")

    @api.multi
    def _compute_obtener_estado_anulacion_comprobante(self):
        for record in self:
            if record.documento_baja_id:
                record.anulacion_comprobante = record.documento_baja_state
            elif record.resumen_anulacion_id:
                record.anulacion_comprobante = record.resumen_anulacion_state
            else:
                record.anulacion_comprobante = "-"

    # baja_id = fields.Many2one('facturactiva.baja_documento', string='Documento de baja perteneciente',
    #   ondelete='cascade', index=True)
    tipo_cambio_fecha_factura = fields.Float(
        string="Tipo de cambio a la fecha de factura",
        default=1.0)
    descuento_global = fields.Float(
        string="Descuento Global (%)",
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=0.0)
    date_invoice = fields.Date(string='Invoice Date',
                               readonly=True,
                               index=True,
                               help="Keep empty to use the current date",
                               default=fields.Date.context_today)

    @api.multi
    def actualizar_datos_cliente(self):
        for record in self:
            if record.partner_id:
                record.partner_id.update_document()
            else:
                raise UserError("No hay cliente asociado a la factura")

    @api.model
    def default_get(self, fields_list):
        res = super(AccountInvoice, self).default_get(fields_list)
        refund_id = self._context.get("default_refund_invoice_id", False)
        domain = []
        if refund_id:
            refund_obj = self.env["account.invoice"].browse(refund_id)
            domain += [['tipo_comprobante_a_rectificar',
                        'in', [refund_obj.invoice_type_code]]]
        domain += [['invoice_type_code_id', '=',
                    self._context.get("default_invoice_type_code")], ["type", "=", "sale"]]
        journal_id = self.env['account.journal'].search(domain, limit=1)
        res["journal_id"] = journal_id.id
        return res

    invoice_type_code = fields.Selection(selection=[('00', 'Otros'),
                                                    ('01', 'Factura'),
                                                    ('03', 'Boleta'),
                                                    ('07', 'Nota de crédito'),
                                                    ('08', 'Nota de débito')],
                                         string="Tipo de Comprobante", related="journal_id.invoice_type_code_id",
                                         readonly=True
                                         )

    invoice_type_code_str = fields.Char(
        "Tipo de Comrpobante*", compute="_compute_tipo_comprobante", store=True)

    def _compute_tipo_comprobante(self):
        for record in self:
            if record.invoice_type_code == "01":
                record.invoice_type_code_str = "Factura Electrónica"
            elif record.invoice_type_code == "03":
                record.invoice_type_code_str = "Boleta de Venta Electrónica"
            elif record.invoice_type_code == "07":
                record.invoice_type_code_str = "Nota de crédito Electrónica"
            elif record.invoice_type_code == "08":
                record.invoice_type_code_str = "Nota de débito Electrónica"

    @api.one
    @api.depends('invoice_line_ids.price_unit', 'invoice_line_ids.quantity', 'invoice_line_ids.price_subtotal', 'tax_line_ids.amount',
                 'tax_line_ids.amount_rounding', "descuento_global", 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        self.total_descuento_global = sum(
            [
                line.price_subtotal
                for line in self.invoice_line_ids
                if len([line.price_subtotal for line_tax in line.invoice_line_tax_ids
                        if line_tax.tipo_afectacion_igv.code not in ["31", "32", "33", "34", "35", "36"]])
            ])*self.descuento_global/100.0

        self.total_venta_gravado = sum(
            [
                line.price_subtotal
                for line in self.invoice_line_ids
                if len([line.price_subtotal for line_tax in line.invoice_line_tax_ids
                        if line_tax.tipo_afectacion_igv.code in ["10"]])
            ])*(1-self.descuento_global/100.0)

        self.total_venta_inafecto = sum(
            [
                line.price_subtotal
                for line in self.invoice_line_ids
                if len(
                    [line.price_subtotal for line_tax in line.invoice_line_tax_ids
                     if line_tax.tipo_afectacion_igv.code in ["40", "30"]])
            ])*(1-self.descuento_global/100.0)

        self.total_venta_exonerada = sum(
            [
                line.price_subtotal
                for line in self.invoice_line_ids
                if len(
                    [line.price_subtotal for line_tax in line.invoice_line_tax_ids
                     if line_tax.tipo_afectacion_igv.code in ["20"]])
            ])*(1-self.descuento_global/100.0)

        self.total_venta_gratuito = sum(
            [
                line.price_unit*line.quantity
                for line in self.invoice_line_ids
                if len([1 for line_tax in line.invoice_line_tax_ids
                        if line_tax.tipo_afectacion_igv.code in ["31", "32", "33", "34", "35", "36"]])
            ])

        self.total_descuentos = sum(
            [
                ((line.price_subtotal / (1-line.discount/100.0))
                 * line.discount/100.0) + line.descuento_unitario
                for line in self.invoice_line_ids
                if line.discount < 100
            ])+self.total_descuento_global

        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal
                                  for line in self.invoice_line_ids
                                  if len([line.price_subtotal for line_tax in line.invoice_line_tax_ids
                                          if line_tax.tipo_afectacion_igv.code not in ["31", "32", "33", "34", "35", "36"]]))-self.total_descuento_global

        self.amount_tax = sum(round_curr(line.amount_total)
                              for line in self.tax_line_ids)*(1-self.descuento_global/100.0)
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(
                self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(
                self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    total_tax_discount = fields.Monetary(
        string="Total Descuento Impuesto",
        default=0.0,
        compute="_compute_amount",
        currency_field='company_currency_id')
    total_venta_gravado = fields.Monetary(
        string="Gravado",
        default=0.0,
        compute="_compute_amount",
        currency_field='company_currency_id')
    total_venta_inafecto = fields.Monetary(
        string="Inafecto",
        default=0.0,
        compute="_compute_amount")
    total_venta_exonerada = fields.Monetary(
        string="Exonerado",
        default=0.0,
        compute="_compute_amount",
        currency_field='company_currency_id')
    total_venta_gratuito = fields.Monetary(
        string="Gratuita",
        default=0.0,
        compute="_compute_amount",
        currency_field='company_currency_id')
    total_descuentos = fields.Monetary(
        string="Total Descuentos",
        default=0.0,
        compute="_compute_amount",
        currency_field='company_currency_id')
    total_descuento_global = fields.Monetary(
        string="Total Descuentos Global",
        default=0.0,
        compute="_compute_amount",
        currency_field='company_currency_id')

    estado_emision = fields.Selection(
        selection=[
            ('A', 'Aceptado'),
            ('E', 'Enviado a SUNAT'),
            ('N', 'Envio Erróneo'),
            ('O', 'Aceptado con Observación'),
            ('R', 'Rechazado'),
            ('P', 'Pendiente de envió a SUNAT'),
        ],
        string="Estado Emisión a SUNAT",
        copy=False
    )

    @api.model
    def _default_new_invoice(self):
        return self._context.get('default_new_invoice', True)

    new_invoice = fields.Boolean(
        string="Indica si es nuevo o proviene de un documento anterior",
        default=_default_new_invoice)

    @api.multi
    def envio_documento_batch(self):
        documets = self.env['account.invoice'].search(
            [['status_envio', '=', False]])
        nro_exitos = 0
        nro_errores = 0
        for document in documets:
            result, msg = oauth.enviar_doc(
                document, document.company_id.endpoint)
            if result:
                nro_exitos = nro_exitos + 1
            else:
                nro_errores = nro_errores + 1

    @api.multi
    def generar_nota_credito(self):
        if not self.number:
            self.action_invoice_open()
        ref = request.env.ref("account.invoice_form")
        inv_lines2 = []
        for il1 in self.invoice_line_ids:
            obj = il1.copy(default={
                "invoice_id": ""
            })
            inv_lines2.append(obj.id)
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.invoice",
            "target": "self",
            "view_id": ref.id,
            "view_mode": "form",
            "context": {
                'default_partner_id': self.partner_id.id,
                'default_refund_invoice_id': self.id,
                'default_date_invoice': datetime.now().strftime("%Y-%m-%d"),
                'default_payment_term_id': self.payment_term_id.id,
                'default_invoice_line_ids': inv_lines2,
                'default_new_invoice': False,
                'default_type': 'out_refund',
                'journal_type': 'sale',
                'default_invoice_type_code': '07',
                'default_number': 'Nota de Crédito 123'},
            "domain": [('type', 'in', ('out_invoice', 'out_refund')), ('invoice_type_code', '=', '07')]
        }

    @api.multi
    def generar_nota_debito(self):
        if not self.number:
            self.action_invoice_open()
        ref = request.env.ref("account.invoice_form")
        inv_lines2 = []
        for il1 in self.invoice_line_ids:
            obj = il1.copy(default={
                "invoice_id": ""
            })
            inv_lines2.append(obj.id)
        #print( str(self.number[0:4]) + " - " + str(int(self.number[5:len(self.number)])))
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.invoice",
            "target": "self",
            "view_id": ref.id,
            "view_mode": "form",
            "context": {
                'default_partner_id': self.partner_id.id,
                'default_refund_invoice_id': self.id,
                'default_date_invoice': datetime.now().strftime("%Y-%m-%d"),
                'default_payment_term_id': self.payment_term_id.id,
                'default_invoice_line_ids': inv_lines2,
                'default_new_invoice': False,
                'default_type': 'out_invoice',
                'journal_type': 'sale',
                'default_invoice_type_code': '08',
                'default_number': 'Nota de Débito 123'},
            "domain": [('type', 'in', ('out_invoice', 'out_refund')), ('invoice_type_code', '=', '08')]
        }

    def btn_comunicacion_baja(self):
        ref = self.env.ref("efact.view_comunicacion_baja_form")
        # if self.estado_comprobante_electronico in ["-",False,"0_NO_EXISTE"]:
        # self.btn_consulta_validez_comprobante()

        _logger.info(True if self.documento_baja_id else False)

        if self.estado_comprobante_electronico == "2_ANULADO":
            raise UserError("Este comprobante ha sido Anulado.")

        elif re.match("^F\w{3}-\d{1,8}$", self.move_name):
            if self.documento_baja_id:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "efact.account_comunicacion_baja",
                    "target": "self",
                    "res_id": self.documento_baja_id.id,
                    "view_mode": "form",
                    "view_id": ref.id,
                }
            else:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "efact.account_comunicacion_baja",
                    "target": "self",
                    "view_id": ref.id,
                    "view_mode": "form",
                    "context": {
                        'default_invoice_ids': [self.id],
                        'default_invoice_type_code_id': self.invoice_type_code,
                        'default_date_invoice': self.date_invoice,
                        'default_issue_date': datetime.now().strftime("%Y-%m-%d")
                    }
                }
        elif re.match("^B\w{3}-\d{1,8}$", self.move_name):
            if self.resumen_anulacion_id:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "account.summary",
                    "name": "Anulación de comprobante",
                    "view_mode": "form",
                    "target": "self",
                    "res_id": self.resumen_anulacion_id.id
                }
            else:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "account.summary.anulacion",
                    "name": "Anulación de Comprobante",
                    "view_id": self.env.ref("efact.view_popup_account_summary_anulacion").id,
                    "view_mode": "form",
                    "target": "new",
                    "context": {
                            "default_account_invoice_id": self.id
                    }
                }
        # elif self.estado_comprobante_electronico != "1_ACEPTADO":
        #     raise UserError("Para que un documento pueda ser Anulado, debe tener estado ACEPTADO.")

        # "domain": [('type', 'in', ('out_invoice', 'out_refund')), ('journal_id.invoice_type_code_id', '=', '07')]

    def validacion_factura(self):
        errors = []
        # if self.partner_id.company_type != "company":
        #     errors.append('''* El cliente seleccionado debe ser de tipo Compañía para las facturas
        #                     Recuerda: que para un cliente de tipo compañía, los campos de tipo de documento,
        #                     Documento y Razón Social son Obligatorios. Además el tipo de Documento debe ser RUC.''')
        if self.partner_id.tipo_documento != "6":
            errors.append(
                "* El cliente seleccionado debe tener como tipo de documento el RUC, esto es necesario para facturas.")
        if not self.partner_id.vat:
            errors.append(
                "* El cliente selecionado no tiene RUC, esto es necesario para facturas")
        elif len(self.partner_id.vat) != 11:
            errors.append(
                "* El RUC del cliente selecionado debe tener 11 dígitos")
        if not self.partner_id.zip:
            errors.append(
                "* El cliente selecionado no tiene configurado el Ubigeo.")
        """
        if not self.partner_id.email:
            errors.append("* El cliente selecionado no tiene email.")
        """
        for line in self.invoice_line_ids:
            if len(line.invoice_line_tax_ids) == 0:
                errors.append(
                    "* El Producto debe tener al menos un tipo de impuesto Asociado")
            for tax in line.invoice_line_tax_ids:
                if not tax.tipo_afectacion_igv:
                    errors.append(
                        "* El Tipo de Afectacion al IGV no esta configurado para el Impuesto %s del item %s" % (tax.name, line.name))
            # Falta Validar los tipos de Afectación al IGV
            if not line.uom_id.code:
                errors.append(
                    "* La Unidad de Medida seleccionada para el item %s no tiene código" % (line.name))

        return errors

    def validacion_boleta(self):
        errors = []
        """
        if not self.partner_id.email:
            errors.append("* El cliente selecionado no tiene email.")
        """
        return errors

    def validar_datos_compania(self):
        errors = []
        if not self.company_id.partner_id.vat:
            errors.append(
                "* No se tiene configurado el RUC de la empresa emisora")

        if not self.company_id.partner_id.tipo_documento:
            errors.append(
                "* No se tiene configurado el tipo de documento de la empresa emisora")
        elif self.company_id.partner_id.tipo_documento != '6':
            errors.append(
                "* El Tipo de Documento de la empresa emisora debe ser RUC")

        if not self.company_id.partner_id.zip:
            errors.append(
                "* No se encuentra configurado el Ubigeo de la empresa emisora.")

        if not self.company_id.partner_id.street:
            errors.append(
                "* No se encuentra configurado la dirección de la empresa emisora.")

        if not self.company_id.partner_id.registration_name:
            errors.append(
                "* No se encuentra configurado la Razón Social de la empresa emisora.")

        return errors

    def validar_diario(self):
        errors = []
        if self.journal_id.tipo_envio != self.company_id.tipo_envio:
            errors.append(
                "* El tipo de envío configurado en la compañía debe coincidir con el tipo de envío del Diario que ha seleccionado.")
        return errors

    def validar_fecha_emision(self):
        errors = []
        now = datetime.strptime(fields.Date.today(), "%Y-%m-%d")
        if now < datetime.strptime(self.date_invoice, "%Y-%m-%d"):
            errors.append(
                "* La fecha de la emisión del comprobante debe ser menor o igual a la fecha del día de hoy.")
        elif abs(datetime.strptime(self.date_invoice, "%Y-%m-%d") - now).days > 7:
            errors.append(
                "* La fecha de Emisión debe tener como máximo una antiguedad de 7 días.")

        return errors

    # Validar si Unidad de medida de las líneas poseen códigos válidos
    # Validar que la descripción de los productos no tengan espacios al inicio y al final
    # validar que la descripción no tenga saltos de línea
    # validar que la descripción tenga más de 4 carácteres y menos que 250
    # validar que la cantidad por item sea mayor  0

    def validar_lineas(self):
        errors = []
        for line in self.invoice_line_ids:
            if line.name:
                if len(line.name) < 4 and len(line.name) > 250:
                    errors.append(
                        "* La cantidad de carácteres de la descripción del producto debe ser mayor a 4 y menor a 250")
                    break
            else:
                errors.append(
                    "* La descripción del detalle de los productos esta vacío.")
                break

            if not line.uom_id.code:
                errors.append(
                    "* La Unidad de medida del detalle de las líneas del comprobante esta vacío.")
            else:
                if line.uom_id.code not in codigo_unidades_de_medida:
                    errors.append(
                        "* El código de la unida de medida del detalle de las líneas del comprobante es invalido.")
                    break

            if line.quantity <= 0:
                errors.append(
                    "* La cantidad del detalle de las líneas del comprobante es mayor a 0.")
                break

            if len(line.invoice_line_tax_ids) == 0:
                errors.append(
                    "* Las líneas del detalle del comprobante deben poseer al menos un impuesto.")
                break
            else:
                for line_tax in line.invoice_line_tax_ids:
                    if not line_tax.tipo_afectacion_igv:
                        errors.append(
                            "* El impuesto seleccionado en las líneas del comprobante no posee tipo de afectación al IGV.")
                        break
                    else:
                        if line_tax.tipo_afectacion_igv.code not in codigos_tipo_afectacion_igv:
                            errors.append(
                                "* El código de tipo de afectación ingresado no es Válido. Consulte con su Administrador del Sistema.")
                            break

            if line.discount == 100:
                errors.append(
                    "El descuento no puede ser del 100%. Si el producto es gratuito, use el impuesto GRATUITO.")
                break

            if line.price_unit == 0 and len([1 for tax in line.invoice_line_tax_ids if tax.tipo_afectacion_igv.code in ["31", "32", "33", "34", "35", "36"]]) > 0:
                errors.append(
                    "El precio unitario de los productos debe ser siempre mayor a 0. Revise el producto {} y cambie el precio a un valor mayor a 0.".format(line.name))
                break

            # if line.price_unit == 0 and len([1 for tax in line.invoice_line_tax_ids if tax.tipo_afectacion_igv.code in ["31","32","33","34","35","36"]]) == 0:

        return errors

    def validar_datos_cliente(self):
        errors = []
        if self.tipo_documento_sunat == '6':
            if self.numero_documento:
                if not patron_ruc.match(self.numero_documento):
                    errors.append(
                        "* El número de documento del cliente no tiene el formato de un número de RUC.")
            else:
                errors.append("* Debe ingresar el número de RUC del cliente.")
        elif self.tipo_documento_sunat == '1':
            if self.numero_documento:
                if not patron_ruc.match(self.numero_documento):
                    errors.append(
                        "* El número de documento del cliente no tiene el formato de un número de DNI.")
            else:
                errors.append("* Debe ingresar el número de DNI del cliente.")

        if not self.partner_id.name:
            errors.append("* El nombre del cliente es obligatorio")
        else:
            if len(self.partner_id.name) < 4 or len(self.partner_id.name) > 250:
                errors.append(
                    "* La cantidad de carácteres del nombre del cliente debe ser mayor a 4 y menor a 250.")

        return errors

    def validar_tipo_operacion(self):
        pass

    def validar_impuestos(self):
        pass

    def validar_comprobante(self):
        if self.company_id.parent_id:
            self.company_id = self.company_id.parent_id.id
        self.action_invoice_open()
        # self.get_comprobante()

    def cron_enviar_comprobante(self):
        account_invoice_ids = self.env["account.invoice"].search([["status_envio", "in", ["P", "", False]],
                                                                  ["state", "in", [
                                                                      "open", "paid"]],
                                                                  ["estado_comprobante_electronico", "in", ["-"]]])
        factura_ids = account_invoice_ids.filtered(lambda comp: comp.journal_id.invoice_type_code_id in [
                                                   "01"] and re.match("^F\w{3}-\d{1,8}$", comp.move_name))

        nota_ids = account_invoice_ids.filtered(lambda comp: comp.journal_id.invoice_type_code_id in ["07", "08"] and re.match(
            "^F\w{3}-\d{1,8}$", comp.move_name) and comp.refund_invoice_id.estado_comprobante_electronico == "1_ACEPTADO")

        account_invoice_ids = factura_ids + nota_ids

        now = datetime.strptime(fields.Date.today(), "%Y-%m-%d")
        for ai in account_invoice_ids:
            if abs((datetime.strptime(ai.date_invoice, "%Y-%m-%d") - now).days) <= 7:
                try:
                    ai.enviar_comprobante()
                except Exception as e:
                    os.system("echo '%s'" % (str(e)))
            self.env.cr.commit()
        return True

    def enviar_comprobante(self):
        try:
            self.btn_consulta_validez_comprobante()
        except Exception as e:
            pass

        if self.journal_id.invoice_type_code_id in ["07", "08"]:
            if self.refund_invoice_id.estado_comprobante_electronico != "1_ACEPTADO":
                raise UserError(
                    "El comprobante de referencia debe haber sido ACEPTADO por SUNAT")

        if self.estado_emision == 'A' or self.estado_comprobante_electronico == "1_ACEPTADO":
            raise UserError("Este comprobante ya ha sido Aceptado.")
        if self.estado_comprobante_electronico == "2_ANULADO":
            raise UserError("Este comprobante ha sido Anulado.")

        self.write({'tipo_cambio_fecha_factura': oauth.get_tipo_cambio(
            self, 2) if self.currency_id.name == 'USD' else 1.0})
        oauth.enviar_doc(self, self.company_id.endpoint)

    # def action_invoice_open(self):
    def post(self):
        if self.type == "in_invoice":
            if self.reference:
                self._validar_reference(self)
            else:
                raise UserError(
                    "La Referencia de Proveedor de la Factura de compra es obligatoria")
            return super(AccountInvoice, self).post()

        if self.journal_id.formato_comprobante == 'fisico':
            obj = super(AccountInvoice, self).post()
            return obj
        # Validaciones cuando el comprobante es factura
        msg_error = []
        msg_error += self.validar_datos_compania()
        msg_error += self.validar_diario()
        msg_error += self.validar_fecha_emision()
        msg_error += self.validar_lineas()

        if self.journal_id.invoice_type_code_id == "01":
            msg_error += self.validacion_factura()
            if len(msg_error) > 0:
                msg = "\n\n".join(msg_error)
                raise UserError(msg)

        if self.journal_id.invoice_type_code_id == "03":
            msg_error += self.validacion_boleta()
            if len(msg_error) > 0:
                msg = "\n\n".join(msg_error)
                raise UserError(msg)

        if self.partner_id.tipo_documento != "6" and self.journal_id.invoice_type_code_id == "01":
            raise UserError("Tipo de documento del receptor no valido")

        obj = super(AccountInvoice, self).post()

        if self.journal_id.resumen:
            return obj

        self.write({'tipo_cambio_fecha_factura': oauth.get_tipo_cambio(
            self, 2) if self.currency_id.name == 'USD' else 1.0})

        # oauth.enviar_doc(self, self.company_id.endpoint)

        return obj

    @profile
    @api.model
    def create(self, vals):
        return super(AccountInvoice, self.with_context(mail_create_nolog=True, mail_notrack=True)).create(vals)

    @api.model
    def _validar_reference(self, obj):
        reference = obj.reference
        if reference:
            if len(reference) == 13:
                if reference[4:5] == "-" and reference[5:13].isdigit():
                    return True
                else:
                    raise UserError(
                        "La referencia debe tener el formato XXXX-########")
            else:
                raise UserError(
                    "La referencia debe tener el formato XXXX-########")
        else:
            raise UserError("Debe colocar la Referencia del proveedor")

    @api.multi
    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('account.email_template_edi_invoice', False)
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='account.invoice',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="account.mail_template_data_notification_email_account_invoice"
        )

        fname = self.number+".xml"
        cdr_fname = self.number+"_cdr.xml"
        if len(self.account_log_status_ids) > 0:
            log_status = self.account_log_status_ids[-1]
            data_signed_xml = log_status.signed_xml_data_without_format
            ctx["default_attachment_ids"] = []
            if data_signed_xml:
                datas = base64.b64encode(data_signed_xml.encode())
                ctx["default_attachment_ids"].append(self.env["ir.attachment"].create(
                    {"name": fname, "type": "binary", "datas": datas, "mimetype": "text/xml", "datas_fname": fname}).id)

            response_xml = log_status.response_xml_without_format
            if response_xml:
                datas = base64.b64encode(response_xml.encode())
                ctx["default_attachment_ids"].append(self.env["ir.attachment"].create(
                    {"name": cdr_fname, "type": "binary", "datas": datas, "mimetype": "text/xml", "datas_fname": cdr_fname}).id)

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def get_comprobante(self):
        ruc = self.company_id.vat
        tipo_comprobante = self.invoice_type_code
        id = self.move_name
        serie_comprobante = id.split("-")[0]
        numero_comprobante = id.split("-")[1]

        r = consulta_comprobante(
            self.company_id, ruc, tipo_comprobante, serie_comprobante, numero_comprobante)
        try:
            response = json.loads(r.text)
            mensaje = response["result"]["Description"]
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom.pop.message',
                'target': 'new',
                'context': {
                    'default_name': mensaje
                }
            }
        except Exception as exp:
            return {
                'name': 'Message',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom.pop.message',
                'target': 'new',
                'context': {
                    'default_name': r.text
                }
            }

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        return self.env.ref('account.account_invoices').report_action(self)

    @api.multi
    def cron_cambiar_a_no_existe(self):
        try:
            _logger.info("Inicio de cron_cambiar_a_no_existe")
            fecha_hoy = datetime.strptime(fields.Date.today(), '%Y-%m-%d')
            fecha_hoy = datetime.strftime(fecha_hoy, '%Y-%m-%d 00:00:00')
            comprobantes = self.env["account.invoice"].sudo().search([["estado_comprobante_electronico", "=", "0_NO_EXISTE"],
                                                                      ["state", "not in", [
                                                                          "draft", "cancel"]],
                                                                      ["date_invoice",
                                                                          "<=", fecha_hoy],
                                                                      ["move_name",
                                                                          "!=", False],
                                                                      ["journal_id", "!=", False]])
            comprobantes = comprobantes.filtered(lambda comp: comp.journal_id.invoice_type_code_id in ['01', '03', '07', '08'] and (
                re.match("^F\w{3}-\d{1,8}$", comp.move_name) or re.match("^B\w{3}-\d{1,8}$", comp.move_name)))
            return comprobantes.write({"estado_comprobante_electronico": "-"})

        except Exception as e:
            _logger.info("Error en cron_cambiar_a_no_existe: {}".format(e))
        finally:
            _logger.info("Fin de cron_cambiar_a_no_existe")

    def cron_consulta_validez_comprobante(self):
        fecha_hoy = datetime.strptime(fields.Date.today(), '%Y-%m-%d')
        fecha_hoy = datetime.strftime(fecha_hoy, '%Y-%m-%d 00:00:00')

        invoices_with_baja = self.env["account.invoice"].sudo().search(
            [["estado_comprobante_electronico", "=", "1_ACEPTADO"], ["documento_baja_id.state", "in", ["E", "A"]]])

        invoices = self.env["account.invoice"].sudo().search([["estado_comprobante_electronico", "in", ["-"]],
                                                              ["state", "not in", [
                                                                  "draft", "cancel"]],
                                                              ["date_invoice",
                                                                  "<", fecha_hoy],
                                                              ["move_name",
                                                                  "!=", False],
                                                              ["journal_id", "!=", False]])

        invoices = invoices.filtered(lambda inv: inv.journal_id.invoice_type_code_id in ['01', '03', '07', '08'] and (
            re.match("^F\w{3}-\d{1,8}$", inv.move_name) or re.match("^B\w{3}-\d{1,8}$", inv.move_name)))
        invoices = invoices + invoices_with_baja
        # invoices.mapped("company_id") selecciona a las compañias únicas de los comprobantes
        for company in invoices.mapped("company_id"):
            invoices_by_company = invoices.filtered(
                lambda r: r.company_id == company)
            chunks = [invoices_by_company[x:x+25]
                      for x in range(0, len(invoices_by_company), 25)]
            for ch_invs in chunks:
                if len(ch_invs) >= 1:
                    try:
                        ch_invs.sudo().btn_consulta_validez_comprobante()
                    except Exception as e:
                        os.system("echo '%s'" % (str(ch_invs)))
                        os.system("echo '%s'" % (str(e)))
                        pass
                self.env.cr.commit()
        return True

    def cron_actualizacion_estado_emision_sunat(self):
        comprobantes = self.env["account.invoice"].sudo().search(
            [["estado_comprobante_electronico", "=", "1_ACEPTADO"], ["estado_emision", "in", [False, "N"]]])
        return comprobantes.sudo().write({"estado_emision": "A"})
        # return True

    def btn_consulta_validez_comprobante_masivo(self):
        """
        Acción de servidor que es llamada para validar un pull de comprobantes
        """
        invoices = self
        if len(invoices) >= 1:
            # invoices.mapped("company_id") selecciona a las compañias únicas de los comprobantes
            for company in invoices.mapped("company_id"):
                # Filtra a las facturas por compañia y realiza la validez de comprobante por grupo
                invs_by_company = invoices.filtered(lambda inv: inv.company_id == company and inv.journal_id.invoice_type_code_id in [
                                                    '01', '03', '07', '08'] and (re.match("^F\w{3}-\d{1,8}$", inv.move_name) or re.match("^B\w{3}-\d{1,8}$", inv.move_name)))
                invs_by_company.btn_consulta_validez_comprobante()

    @api.multi
    def btn_consulta_validez_comprobante(self):
        if len(self.mapped("company_id")) != 1:
            raise UserError(
                "Solo se puede consultar comprobantes de una compañía a la vez")
        if len(self) <= 40 and len(self) >= 1:
            # Se toma la compañia del primer comprobante como representante del grupo de facturas a validar
            company = self[0].company_id
            lista_consultas = []
            for record in self:
                move_name = record.move_name
                try:
                    if record.move_name:
                        if re.match("^F\w{3}-\d{1,8}$", move_name) or re.match("^B\w{3}-\d{1,8}$", move_name):
                            split = move_name.split("-")
                            serie = split[0]
                            numero_comprobante = str(int(split[1]))
                        else:
                            raise UserError(
                                "El comprobante {} tiene un formato incorrecto.".format(move_name))

                        tipo_comprobante = record.invoice_type_code
                        fecha_emision = record.date_invoice
                        fecha_emision = datetime.strptime(
                            fecha_emision, "%Y-%m-%d")
                        fecha_emision = fecha_emision.strftime("%d/%m/%Y")

                        monto = record.amount_total
                        consulta = {
                            "tipo_comprobante": tipo_comprobante,
                            "serie": serie,
                            "numero_comprobante": numero_comprobante,
                            "fecha_emision": fecha_emision,
                            "monto": str(round(monto, 2))
                        }

                        lista_consultas.append(consulta)
                except Exception as e:
                    pass

            if len(lista_consultas) == 0:
                raise UserError(
                    "No se han encontrado comprobantes para validar.")

            # _logger.info(lista_consultas)
            # _logger.info(self.read(["move_name","company_id"]))
            response = consultar_validez_comprobante(company, lista_consultas)
            # _logger.info(response.text)

            errors = []
            try:
                response = response.json()
                #{"success": true, "result": [{"data": {"numRuc": "10801221781", "codComp": "01", "numeroSerie": "FP01", "numero": "531", "fechaEmision": "18/05/2019", "monto": "70.5"}, "errors": [], "response": {"success": true, "message": "Operation Success! ", "data": {"estadoCp": "1", "estadoRuc": "00", "condDomiRuc": "00", "observaciones": ["- El comprobante de pago consultado ha sido emitido a otro contribuyente."]}}}]}
                if "result" in response:
                    result = response["result"]
                    for res in result:
                        if len(res.get("errors", [])) == 0:
                            if "data" in res:
                                data = res["data"]
                                if "numeroSerie" in data and "numero" in data:
                                    numero_comprobante = res["data"]["numeroSerie"] + \
                                        "-"+res["data"]["numero"].zfill(8)
                                    comprobante_obj = self.env["account.invoice"].search(
                                        [["move_name", "=", numero_comprobante], ["company_id", "=", company.id]])
                                else:
                                    errors.append("Error en el siguiente registro: {}".format(
                                        json.dumps(res, indent=4)))

                            if "response" in res:
                                if type(res["response"]) == dict:
                                    if res["response"].get("success"):
                                        if "data" in res["response"]:
                                            data = res["response"]["data"]
                                            if "estadoCp" in data:
                                                estadoCp = data["estadoCp"]
                                                comprobante_obj.estado_comprobante_electronico = estado_comprobante_electronico[
                                                    estadoCp]
                                            if "estadoRuc" in data:
                                                estadoRuc = data["estadoRuc"]
                                                comprobante_obj.estado_contribuyente_ruc = estado_contribuyente_ruc[
                                                    estadoRuc]
                                            if "condDomiRuc" in data:
                                                condDomiRuc = data["condDomiRuc"]
                                                comprobante_obj.condicion_domicilio_contribuyente = condicion_domicilio_contribuyente[
                                                    condDomiRuc]
                                    else:
                                        errors.append("Se ha encontrado un error en la consulta: {}".format(
                                            json.dumps(res["response"], indent=4)))
                                else:
                                    errors.append("Se ha encontrado un error en la consulta: {}".format(
                                        json.dumps(res["response"], indent=4)))
                            else:
                                errors.append("No se ha encontrado a 'response' en el registro: {}".format(
                                    json.dumps(res, indent=4)))
                        else:
                            errors.append(res.get("errors"))
                else:
                    raise UserError(json.dumps(response, indent=4))
            except Exception as e:
                raise UserError(json.dumps(response, indent=4))

            if len(errors) > 0:
                return {
                    'name': 'Error en una o más consulta de la valides de comprobantes',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'custom.pop.message',
                    'target': 'new',
                    'context': {
                        'default_name': "\n\n".join(errors)
                    }
                }

        else:
            raise UserError(
                "La consulta masiva de comprobantes es de por lo menos 1 y a lo más 40 registros")

    def action_context_default_guia_remision(self):
        return {
            "default_documento_asociado": "comprobante_pago",
            "default_fecha_emision": fields.Date.today(),
            "default_fecha_inicio_traslado": fields.Date.today(),
            # "default_modalidad_transporte":"02",
            "default_motivo_traslado": "01",
            "default_comprobante_pago_ids": [(6, 0, [self.id])],
            "default_destinatario_partner_id": self.partner_id.id,
            "default_company_partner_id": self.partner_id.id
        }

    def action_open_guia_remision(self):
        action = {
            "type": "ir.actions.act_window",
            "res_model": "efact.guia_remision",
            "context": self.action_context_default_guia_remision(),
            "target": "self",
            "view_mode": "form"
        }
        return action

    def action_view_guia_remision(self):
        context = {
            "default_documento_asociado": "comprobante_pago",
            "default_fecha_emision": fields.Date.today(),
            "default_fecha_inicio_traslado": fields.Date.today(),
            "default_modalidad_transporte": "02",
            "default_motivo_traslado": "01",
            "default_comprobante_pago_ids": [(6, 0, [self.id])],
            "default_destinatario_partner_id": self.partner_id.id,
            "default_company_partner_id": self.partner_id.id
        }
        if len(self.guia_remision_ids) == 1:
            action = {
                "type": "ir.actions.act_window",
                "res_model": "efact.guia_remision",
                "target": "self",
                "view_mode": "form",
                "res_id": self.guia_remision_ids.id,
                "context": context
            }
        elif len(self.guia_remision_ids) > 1:
            action = {
                "type": "ir.actions.act_window",
                "res_model": "efact.guia_remision",
                "target": "self",
                "view_mode": "tree",
                "domain": [("id", "in", self.guia_remision_ids.ids)],
                "context": context
            }

        return action


class CustomPopMessage(models.TransientModel):
    _name = "custom.pop.message"
    name = fields.Char('Message')
    accion = fields.Text(string="Accion a realizar")


class InvoiceNota(models.Model):
    _name = "efact.invoice_nota"

    name = fields.Char("Nombre", required=True)
    descripcion = fields.Text("Descripción", required=True)
