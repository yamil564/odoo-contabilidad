from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import re

class AccountMove(models.Model):
    _inherit = "account.move"


    prefix_code=fields.Char(string="Número Serie")
    invoice_number=fields.Char(string="Correlativo")


    def _validate_inv_supplier_ref(self):
        if not self.inv_supplier_ref:
            raise UserError("Debe colocar el número de comprobante.")



    def post(self):
        for rec in self:
            if rec.type in ['in_invoice','in_refund']:
                rec.inv_supplier_ref='-'
            
        super(AccountMove,self).post()

    ##################################################

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountMove,self)._onchange_partner_id()

        self = self.with_context(force_company=self.journal_id.company_id.id)

        warning = {}
        if self.partner_id:
            if self.currency_id and self.currency_id != self.company_id.currency_id:
                if self.journal_id.invoice_type_code_id=='02':
                    rec_account = self.partner_id.property_account_receivable_me_fees_id
                    pay_account = self.partner_id.property_account_payable_me_fees_id    
                else:
                    rec_account = self.partner_id.property_account_receivable_me_id
                    pay_account = self.partner_id.property_account_payable_me_id
            else:
                if self.journal_id.invoice_type_code_id=='02':
                    rec_account = self.partner_id.property_account_receivable_fees_id
                    pay_account = self.partner_id.property_account_payable_fees_id
                else:
                    rec_account = self.partner_id.property_account_receivable_id
                    pay_account = self.partner_id.property_account_payable_id
            
            if not rec_account and not pay_account:
                action = self.env.ref('account.action_account_config')
                msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
            p = self.partner_id
            if p.invoice_warn == 'no-message' and p.parent_id:
                p = p.parent_id
            if p.invoice_warn and p.invoice_warn != 'no-message':
                # Block if partner only has warning but parent company is blocked
                if p.invoice_warn != 'block' and p.parent_id and p.parent_id.invoice_warn == 'block':
                    p = p.parent_id
                warning = {
                    'title': _("Warning for %s") % p.name,
                    'message': p.invoice_warn_msg
                }
                if p.invoice_warn == 'block':
                    self.partner_id = False
                    return {'warning': warning}

        if self.is_sale_document(include_receipts=True) and self.partner_id:
            self.invoice_payment_term_id = self.partner_id.property_payment_term_id or self.invoice_payment_term_id
            ###################################
            if self.currency_id and self.currency_id != self.company_id.currency_id:
                if self.journal_id.invoice_type_code_id=='02':
                    new_term_account = self.partner_id.commercial_partner_id.property_account_receivable_me_fees_id
                else:
                    new_term_account = self.partner_id.commercial_partner_id.property_account_receivable_me_id
            else:
                if self.journal_id.invoice_type_code_id=='02':
                    new_term_account = self.partner_id.commercial_partner_id.property_account_receivable_fees_id
                else:
                    new_term_account = self.partner_id.commercial_partner_id.property_account_receivable_id
            #######################################
            #new_term_account = self.partner_id.commercial_partner_id.property_account_receivable_id
            self.narration = self.company_id.with_context(lang=self.partner_id.lang).invoice_terms
        elif self.is_purchase_document(include_receipts=True) and self.partner_id:
            self.invoice_payment_term_id = self.partner_id.property_supplier_payment_term_id or self.invoice_payment_term_id
            #######################################
            if self.currency_id and self.currency_id != self.company_id.currency_id:
                if self.journal_id.invoice_type_code_id=='02':
                    new_term_account = self.partner_id.commercial_partner_id.property_account_payable_me_fees_id
                else:
                    new_term_account = self.partner_id.commercial_partner_id.property_account_payable_me_id
            else:
                if self.journal_id.invoice_type_code_id=='02':
                    new_term_account = self.partner_id.commercial_partner_id.property_account_payable_fees_id
                else:
                    new_term_account = self.partner_id.commercial_partner_id.property_account_payable_id
            ############################################
            #new_term_account = self.partner_id.commercial_partner_id.property_account_payable_id
        else:
            new_term_account = None

        for line in self.line_ids:
            line.partner_id = self.partner_id.commercial_partner_id

            if new_term_account and line.account_id.user_type_id.type in ('receivable', 'payable'):
                line.account_id = new_term_account

        self._compute_bank_partner_id()
        self.invoice_partner_bank_id = self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]

        # Find the new fiscal position.
        delivery_partner_id = self._get_invoice_delivery_partner_id()
        new_fiscal_position_id = self.env['account.fiscal.position'].with_context(force_company=self.company_id.id).get_fiscal_position(
            self.partner_id.id, delivery_id=delivery_partner_id)
        self.fiscal_position_id = self.env['account.fiscal.position'].browse(new_fiscal_position_id)
        self._recompute_dynamic_lines()
        if warning:
            return {'warning': warning}


    @api.onchange('journal_id','currency_id')
    def _onchange_journal_id_currency_id(self):
        self._onchange_partner_id()