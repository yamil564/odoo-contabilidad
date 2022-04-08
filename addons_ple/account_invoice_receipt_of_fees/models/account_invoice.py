from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

import logging
_logger=logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    is_receipt_of_fees = fields.Boolean(string="Recibo por Honorario", default=False)
    ## el modelo account.journal poseera un check de identificacion de recibo por honorario

    @api.multi
    @api.onchange('currency_id', 'is_receipt_of_fees')
    def set_domain_for_journal_fees_id(self):

        type = self.type
        #or self.env.context.get('type', 'out_invoice')
        if type in ['in_invoice']:
            if self.is_receipt_of_fees:
                records = []
                #if self.currency_id:
                records = self.env['account.journal'].search([('is_receipt_of_fees', '=', True),('currency_id', 'in',[self.currency_id.id,None]),('type','in',['purchase']),
                                                                  ('company_id','=',self.env['res.company']._company_default_get('account.invoice')[0].id)])

                res = {}
                res['domain'] = {'journal_id': [('id', 'in', [i.id for i in records])]}
                return res
            else:
                records = []
                records = self.env['account.journal'].search(
                    [('es_contingencia', '=',False), ('company_id', 'in',[self.env['res.company']._company_default_get('account.invoice')[0].id]),
                    ('type', 'in', ['purchase'])])

                res = {}
                res['domain'] = {'journal_id': [('id', 'in', [i.id for i in records])]}
                return res

    @api.multi
    @api.onchange('is_receipt_of_fees','currency_id','partner_id')
    def onchange_account_fees_id(self):
        type = self.type
        #or self.env.context.get('type', 'out_invoice')
        if self.is_receipt_of_fees and type in ['in_invoice'] and self.partner_id:
            if self.currency_id in [None,self.company_id.currency_id]:
                self.account_id = self.partner_id.fees_account_payable_id or None
            elif self.currency_id and (self.currency_id != self.company_id.currency_id):
                self.account_id= self.partner_id.fees_account_payable_me_id or None
            else:
                self.account_id=None

        elif not self.is_receipt_of_fees:
            self._onchange_currency_id()


    @api.onchange('currency_id', 'is_receipt_of_fees')
    def onchange_journal_fees_id(self):
        type = self.type
        #or self.env.context.get('type', 'out_invoice')
        if type in ['in_invoice']:
            records = []
            if self.is_receipt_of_fees:
                if self.currency_id and (self.currency_id != self.company_id.currency_id):
                    records = self.env['account.journal'].search(
                        [('is_receipt_of_fees', '=', True),('currency_id', 'in', [self.currency_id.id]),
                         ('type', 'in', ['purchase']),
                         ('company_id', '=', self.env['res.company']._company_default_get('account.invoice')[0].id)],limit=1)
                else:
                    records = self.env['account.journal'].search([('is_receipt_of_fees', '=', True),('type','in',['purchase']),
                                                                  ('company_id','=',self.env['res.company']._company_default_get('account.invoice')[0].id),
                                                                  ('currency_id', 'in', [False,'',None,self.company_id.currency_id.id])],limit=1)
                if not len(records):
                    raise UserError(_('NO EXISTE NINGÚN DIARIO DE RECIBO POR HONORARIOS, POR FAVOR CONFIGURE UNO !'))
            else:
                records = self.env['account.journal'].search(
                    [('es_contingencia', '=', False),
                     ('company_id', 'in', [self.env['res.company']._company_default_get('account.invoice')[0].id]),
                     ('type', 'in', ['purchase'])],limit=1)
            self.journal_id = records or None


