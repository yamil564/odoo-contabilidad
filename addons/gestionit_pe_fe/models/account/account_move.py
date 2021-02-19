# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_type_code = fields.Selection(selection=[('00', 'Otros'),
                                                    ('01', 'Factura'),
                                                    ('03', 'Boleta'),
                                                    ('07', 'Nota de crédito'),
                                                    ('08', 'Nota de débito')],
                                         string="Tipo de Comprobante", related="journal_id.invoice_type_code_id",
                                         readonly=True
                                         )

    # descuento_global = fields.Float(
    #     string="Descuento Global (%)",
    #     readonly=True,
    #     states={'draft': [('readonly', False)]},
    #     default=0.0)

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
    # total_descuentos = fields.Monetary(
    #     string="Total Descuentos",
    #     default=0.0,
    #     compute="_compute_amount",
    #     currency_field='company_currency_id')
    # total_descuento_global = fields.Monetary(
    #     string="Total Descuentos Global",
    #     default=0.0,
    #     compute="_compute_amount",
    #     currency_field='company_currency_id')

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
            # self.total_descuento_global = sum(
            #     [
            #         line.price_subtotal
            #         for line in self.invoice_line_ids
            #         if len([line.price_subtotal for line_tax in line.tax_ids
            #                 if line_tax.tax_group_id.tipo_afectacion not in ["31", "32", "33", "34", "35", "36"]])
            #     ])*self.descuento_global/100.0

            self.total_venta_gravado = sum(
                [
                    line.price_subtotal
                    for line in self.invoice_line_ids
                    if len([line.price_subtotal for line_tax in line.tax_ids
                            if line_tax.tax_group_id.tipo_afectacion in ["10"]])
                ])
            # *(1-self.descuento_global/100.0)

            self.total_venta_inafecto = sum(
                [
                    line.price_subtotal
                    for line in self.invoice_line_ids
                    if len(
                        [line.price_subtotal for line_tax in line.tax_ids
                            if line_tax.tax_group_id.tipo_afectacion in ["40", "30"]])
                ])
            # *(1-self.descuento_global/100.0)

            self.total_venta_exonerada = sum(
                [
                    line.price_subtotal
                    for line in self.invoice_line_ids
                    if len(
                        [line.price_subtotal for line_tax in line.tax_ids
                            if line_tax.tax_group_id.tipo_afectacion in ["20"]])
                ])
            # *(1-self.descuento_global/100.0)

            self.total_venta_gratuito = sum(
                [
                    line.price_unit*line.quantity
                    for line in self.invoice_line_ids
                    if len([1 for line_tax in line.tax_ids
                            if line_tax.tax_group_id.tipo_afectacion in ["31", "32", "33", "34", "35", "36", "37"]])
                ])

            # self.total_descuentos = sum(
            #     [
            #         ((line.price_subtotal / (1-line.discount/100.0))
            #             * line.discount/100.0) + line.descuento_unitario
            #         for line in self.invoice_line_ids
            #         if line.discount < 100
            #     ])+self.total_descuento_global

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
