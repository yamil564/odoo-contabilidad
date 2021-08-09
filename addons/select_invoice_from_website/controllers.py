from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)

class WebsiteSaleExtend(WebsiteSale):
        
    def _get_mandatory_billing_fields(self):
        res = super(WebsiteSaleExtend,self)._get_mandatory_billing_fields()
        res.append("vat")
        res.append("l10n_latam_identification_type_id")
        res.remove("street")
        res.remove("city")
        res.remove("country_id")
        return res
    
    def _get_mandatory_shipping_fields(self):
        res = super(WebsiteSaleExtend,self)._get_mandatory_shipping_fields()
        res.remove("street")
        res.remove("city")
        res.remove("country_id")
        return res
        
    
    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message  = super(WebsiteSaleExtend,self).checkout_form_validate(mode, all_form_values, data)
        # _logger.info(all_form_values)
        # _logger.info(data)
        # Se valida el tipo de docuemnto de identidad con el tipo de comprobante
        return error, error_message

    
    @http.route("/change_invoice_type_code",type="json",method="POST",csrf=True,auth="public", website=True)
    def change_invoice_type_code(self,**kargs):
        # _logger.info(kargs)
        order = request.website.sale_get_order()
        order.sudo().write({"invoice_type_code":kargs.get("invoice_type_code")})
        return True

    def checkout_redirection(self,order):
        res = super(WebsiteSaleExtend,self).checkout_redirection(order)
        # _logger.info(order)
        # _logger.info(order.read())
        return res