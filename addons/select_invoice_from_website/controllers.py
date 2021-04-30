from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)

class WebsiteSaleExtend(WebsiteSale):
        
    def _get_mandatory_billing_fields(self):
        res = super(WebsiteSaleExtend,self)._get_mandatory_billing_fields()
        res.append("vat")
        res.append("invoice_type_code")
        res.append("l10n_latam_identification_type_id")
        return res
    
    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message  = super(WebsiteSaleExtend,self).checkout_form_validate(mode, all_form_values, data)
        _logger.info(all_form_values)
        _logger.info(data)
        return error, error_message