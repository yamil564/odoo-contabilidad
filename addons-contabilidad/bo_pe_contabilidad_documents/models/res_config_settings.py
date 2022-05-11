from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"


    property_account_payable_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios a Pagar",
        related='company_id.property_account_payable_fees_id',readonly=False,
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        )

    #############################################################################

    group_account_ME = fields.Boolean("Cuentas por Cobrar y por Pagar en Divisa",  implied_group='base.group_multi_currency', default=False)#,
    
    property_account_receivable_me_id=fields.Many2one('account.account',
        string="Cuenta a cobrar ME",
        related='company_id.property_account_receivable_me_id',
        implied_group='base.group_multi_currency',
        readonly=False,
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        )

    property_account_payable_me_id=fields.Many2one('account.account',
        string="Cuenta a pagar ME",
        related='company_id.property_account_payable_me_id',
        implied_group='base.group_multi_currency',
        readonly=False,
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        )

    group_account_fees_ME = fields.Boolean("Cuentas de Recibos por Honorario por Pagar en Divisa",  implied_group='base.group_multi_currency', default=False)#,


    property_account_payable_me_fees_id=fields.Many2one('account.account',
        string="Cuenta Recibo Honorarios a Pagar ME",
        related='company_id.property_account_payable_me_fees_id',
        implied_group='base.group_multi_currency',readonly=False,
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        )

    
    def sync_account_me_partners(self):
    	query_update="""
    		update res_partner set property_account_receivable_me_id=%s,
    			property_account_payable_me_id=%s 
    		where 
    			active=true and 
    			massive_update_account_me=true """%(
    				self.property_account_receivable_me_id.id,
    				self.property_account_payable_me_id.id)

    	self.env.cr.execute(query_update)

    def sync_account_fees_partners(self):
    	query_update="""
    		update res_partner set property_account_payable_fees_id=%s 
    		where 
    			active=true and 
    			massive_update_account_fees=true """%(self.property_account_payable_fees_id.id)

    	self.env.cr.execute(query_update)


    def sync_account_me_fees_partners(self):
    	query_update="""
    		update res_partner set property_account_payable_me_fees_id=%s 
    		where 
    			active=true and 
    			massive_update_account_fees_me=true """%(self.property_account_payable_me_fees_id.id)

    	self.env.cr.execute(query_update)

