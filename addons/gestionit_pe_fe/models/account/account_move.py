# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.addons.gestionit_pe_fe.models.parameters import oauth
from datetime import datetime, timedelta


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
codigos_tipo_afectacion_igv = [
    "10", "11", "12", "13", "14", "15", "16", "20", "30", "31", "34", "35", "36", "40"
]


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def default_get(self, fields_list):
        res = super(AccountMove, self).default_get(fields_list)
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

    # invoice_type_code_str = fields.Char(
    #     "Tipo de Comrpobante*", compute="_compute_tipo_comprobante", store=True)

    # def _compute_tipo_comprobante(self):
    #     for record in self:
    #         if record.invoice_type_code == "01":
    #             record.invoice_type_code_str = "Factura Electrónica"
    #         elif record.invoice_type_code == "03":
    #             record.invoice_type_code_str = "Boleta de Venta Electrónica"
    #         elif record.invoice_type_code == "07":
    #             record.invoice_type_code_str = "Nota de crédito Electrónica"
    #         elif record.invoice_type_code == "08":
    #             record.invoice_type_code_str = "Nota de débito Electrónica"

    # account_log_status_ids = fields.One2many(
    #     "account.log.status", "account_invoice_id", string="Registro de Envíos", copy=False)
    # tipo_comprobante_elect_ref = fields.Selection(
    #     related="refund_invoice_id.invoice_type_code")
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

    # partner_id = fields.Many2one(
    #     'res.partner',
    #     string='Partner',
    #     change_default=True,
    #     readonly=True,
    #     states={'draft': [('readonly', False)]},
    #     track_visibility='always')

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

    tipo_cambio_fecha_factura = fields.Float(
        string="Tipo de cambio a la fecha de factura",
        default=1.0)

    tipo_operacion = fields.Selection(selection=[(
        "01", "Venta Interna"), ("02", "Exportación")], default="01", required=True, copy=False)

    descuento_global = fields.Float(
        string="Descuento Global (%)",
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=0.0)

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

    amount_igv = fields.Monetary(
        string="IGV",
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

    # monto_en_letras = fields.Char("Monto en letras",compute=_compute_monto_en_letras)
    # tiene_guia_remision = fields.Boolean("Tienes guía de Remisión",default=False,copy=False)
    invoice_picking_id = fields.Many2one(
        "stock.picking", string="Documento de Envío", copy=False)
    stock_picking_id = fields.Many2one(
        "stock.picking", string="Documento de Envío", copy=False)
    # numero_guia = fields.Char("Número de Guía",related="invoice_picking_id.numero_guia",copy=False)
    # numero_guia_remision =  fields.Char("Número de Guía de Remisión",copy=False)

    # guia_remision_ids = fields.Many2many("efact.guia_remision",string="Guía de Remisión")
    # guia_remision_count = fields.Integer("Cantidad de GRE",compute="_compute_guia_remision_count")

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',)
    def _compute_amount(self):
        invoice_ids = [move.id for move in self if move.id and move.is_invoice(
            include_receipts=True)]
        self.env['account.payment'].flush(['state'])
        if invoice_ids:
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                UNION
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE payment.state IN ('posted', 'sent')
                    AND journal.post_at = 'bank_rec'
                    AND move.id IN %s
                ''', [tuple(invoice_ids), tuple(invoice_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
        else:
            in_payment_set = {}

        for move in self:
            self.total_descuento_global = sum(
                [
                    line.price_subtotal
                    for line in self.invoice_line_ids
                    if len([line.price_subtotal for line_tax in line.tax_ids
                            if line_tax.tax_group_id.tipo_afectacion not in ["31", "32", "33", "34", "35", "36"]])
                ])*self.descuento_global/100.0

            self.total_venta_gravado = sum(
                [
                    line.price_subtotal
                    for line in self.invoice_line_ids
                    if len([line.price_subtotal for line_tax in line.tax_ids
                            if line_tax.tax_group_id.tipo_afectacion in ["10"]])
                ])*(1-self.descuento_global/100.0)

            self.total_venta_inafecto = sum(
                [
                    line.price_subtotal
                    for line in self.invoice_line_ids
                    if len(
                        [line.price_subtotal for line_tax in line.tax_ids
                            if line_tax.tax_group_id.tipo_afectacion in ["40", "30"]])
                ])*(1-self.descuento_global/100.0)

            self.total_venta_exonerada = sum(
                [
                    line.price_subtotal
                    for line in self.invoice_line_ids
                    if len(
                        [line.price_subtotal for line_tax in line.tax_ids
                            if line_tax.tax_group_id.tipo_afectacion in ["20"]])
                ])*(1-self.descuento_global/100.0)

            self.total_venta_gratuito = sum(
                [
                    line.price_unit*line.quantity
                    for line in self.invoice_line_ids
                    if len([1 for line_tax in line.tax_ids
                            if line_tax.tax_group_id.tipo_afectacion in ["31", "32", "33", "34", "35", "36", "37"]])
                ])

            self.total_descuentos = sum(
                [
                    ((line.price_subtotal / (1-line.discount/100.0))
                        * line.discount/100.0) + line.descuento_unitario
                    for line in self.invoice_line_ids
                    if line.discount < 100
                ])+self.total_descuento_global

            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        # if line.tax_ids[0].tax_group_id.tipo_afectacion not in ["31", "32", "33", "34", "35", "36", "37"]:
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * \
                (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * \
                (total_tax_currency if len(currencies) == 1 else total_tax)
            #
            move.amount_igv = move.amount_tax + move.total_venta_gratuito
            #
            move.amount_total = sign * \
                (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * \
                (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(
                total) if move.type == 'entry' else -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies.pop(
            ) or move.company_id.currency_id
            is_paid = currency and currency.is_zero(
                move.amount_residual) or not move.amount_residual

            # Compute 'invoice_payment_state'.
            if move.type == 'entry':
                move.invoice_payment_state = False
            elif move.state == 'posted' and is_paid:
                if move.id in in_payment_set:
                    move.invoice_payment_state = 'in_payment'
                else:
                    move.invoice_payment_state = 'paid'
            else:
                move.invoice_payment_state = 'not_paid'

    def post(self):
        if self.type == "in_invoice":
            if self.reference:
                self._validar_reference(self)
            else:
                raise UserError(
                    "La Referencia de Proveedor de la Factura de compra es obligatoria")
            return super(AccountMove, self).post()

        if self.journal_id.formato_comprobante == 'fisico':
            obj = super(AccountMove, self).post()
            return obj
        # Validaciones cuando el comprobante es factura
        msg_error = []
        msg_error += self.validar_datos_compania()
        msg_error += self.validar_diario()
        # msg_error += self.validar_fecha_emision()
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

        if self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code != "6" and self.journal_id.invoice_type_code_id == "01":
            raise UserError("Tipo de documento del receptor no valido")

        obj = super(AccountMove, self).post()

        if self.journal_id.resumen:
            return obj

        self.write({'tipo_cambio_fecha_factura': oauth.get_tipo_cambio(
            self, 2) if self.currency_id.name == 'USD' else 1.0})

        oauth.enviar_doc(self, self.company_id.endpoint)
        # enviar_doc(self, self.company_id.endpoint)

        return obj

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

    def validar_datos_compania(self):
        errors = []
        if not self.company_id.partner_id.vat:
            errors.append(
                "* No se tiene configurado el RUC de la empresa emisora")

        if not self.company_id.partner_id.l10n_latam_identification_type_id:
            errors.append(
                "* No se tiene configurado el tipo de documento de la empresa emisora")
        elif self.company_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code != '6':
            errors.append(
                "* El Tipo de Documento de la empresa emisora debe ser RUC")

        if not self.company_id.partner_id.zip:
            errors.append(
                "* No se encuentra configurado el Ubigeo de la empresa emisora.")

        if not self.company_id.partner_id.street:
            errors.append(
                "* No se encuentra configurado la dirección de la empresa emisora.")

        if not self.company_id.partner_id.name:
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

            if not line.product_uom_id.code:
                errors.append(
                    "* La Unidad de medida del detalle de las líneas del comprobante esta vacío.")
            else:
                if line.product_uom_id.code not in codigo_unidades_de_medida:
                    errors.append(
                        "* El código de la unida de medida del detalle de las líneas del comprobante es invalido.")
                    break

            if line.quantity <= 0:
                errors.append(
                    "* La cantidad del detalle de las líneas del comprobante es mayor a 0.")
                break

            if len(line.tax_ids) == 0:
                errors.append(
                    "* Las líneas del detalle del comprobante deben poseer al menos un impuesto.")
                break
            else:
                for line_tax in line.tax_ids:
                    if not line_tax.tax_group_id.tipo_afectacion:
                        errors.append(
                            "* El impuesto seleccionado en las líneas del comprobante no posee tipo de afectación al IGV.")
                        break
                    else:
                        if line_tax.tax_group_id.tipo_afectacion not in codigos_tipo_afectacion_igv:
                            errors.append(
                                "* El código de tipo de afectación ingresado no es Válido. Consulte con su Administrador del Sistema.")
                            break

            if line.discount == 100:
                errors.append(
                    "El descuento no puede ser del 100%. Si el producto es gratuito, use el impuesto GRATUITO.")
                break

            if line.price_unit == 0 and len([1 for tax in line.tax_ids if tax.tax_group_id.tipo_afectacion in ["31", "32", "33", "34", "35", "36"]]) > 0:
                errors.append(
                    "El precio unitario de los productos debe ser siempre mayor a 0. Revise el producto {} y cambie el precio a un valor mayor a 0.".format(line.name))
                break

            # if line.price_unit == 0 and len([1 for tax in line.invoice_line_tax_ids if tax.tipo_afectacion_igv.code in ["31","32","33","34","35","36"]]) == 0:

        return errors

    def validacion_factura(self):
        errors = []
        # if self.partner_id.company_type != "company":
        #     errors.append('''* El cliente seleccionado debe ser de tipo Compañía para las facturas
        #                     Recuerda: que para un cliente de tipo compañía, los campos de tipo de documento,
        #                     Documento y Razón Social son Obligatorios. Además el tipo de Documento debe ser RUC.''')
        if self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code != "6":
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
            if len(line.tax_ids) == 0:
                errors.append(
                    "* El Producto debe tener al menos un tipo de impuesto Asociado")
            for tax in line.tax_ids:
                if not tax.tax_group_id.tipo_afectacion:
                    errors.append(
                        "* El Tipo de Afectacion al IGV no esta configurado para el Impuesto %s del item %s" % (tax.name, line.name))
            # Falta Validar los tipos de Afectación al IGV
            if not line.product_uom_id.code:
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

    warehouse_id = fields.Many2one("stock.warehouse")
    journal_ids = fields.Many2many(
        "account.journal", string="Series permitidas", related="warehouse_id.journal_ids")
    warehouses_allowed_ids = fields.Many2many(
        "stock.warehouse", string="Almacénes Permitidos", related="user_id.warehouse_ids")
