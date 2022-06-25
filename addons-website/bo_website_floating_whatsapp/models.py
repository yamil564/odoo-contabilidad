from odoo import models,fields,api
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = "website"

    website_floating_whatsapp = fields.Char("Celular Whatsapp")
    website_floating_whatsapp_message_shop = fields.Text("Mensaje WSP Shop")
    website_floating_whatsapp_message_product = fields.Text("Mensaje WSP Producto")
    website_floating_whatsapp_message_order = fields.Text("Mensaje WSP Orden")

    def get_whatsapp_url(self):
        url = "https://wa.me/{}?text={}"
        # _logger.info(request.httprequest.__dict__)
        path = request.httprequest.__dict__.get("path","")
        _logger.info(path)
        order = self.sale_get_order()
        if "/shop/product" in path and ("{producto}" in self.website_floating_whatsapp_message_product):
            path = path.split("?")[0]
            product_id = path.split("-")[-1]
            # _logger.info(product_id)
            product = self.env["product.template"].browse(int(product_id))
            # _logger.info(product.read())
            return url.format(self.website_floating_whatsapp,self.website_floating_whatsapp_message_product.format(producto=product.display_name))
        elif ("/shop" in path or "/payment" in path or "/chechout" in path) and len(order.order_line) > 0:
            return url.format(self.website_floating_whatsapp,self.website_floating_whatsapp_message_order.format(orden=order.name))
        elif "/shop" in path or "/" == path:
            return url.format(self.website_floating_whatsapp,self.website_floating_whatsapp_message_shop)
        return False

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    website_floating_whatsapp = fields.Char(related="website_id.website_floating_whatsapp",
                                            readonly=False,
                                            default="")
    website_floating_whatsapp_message_shop = fields.Text(related="website_id.website_floating_whatsapp_message_shop",
                                            readonly=False,
                                            default="Hola, estoy interesado en sus productos.")
    website_floating_whatsapp_message_product = fields.Text(related="website_id.website_floating_whatsapp_message_product",
                                            readonly=False,
                                            default="Hola, estoy interesado en este producto {producto}.")
    website_floating_whatsapp_message_order = fields.Text(related="website_id.website_floating_whatsapp_message_order",
                                            readonly=False,
                                            default="Hola, mi número de compra es {orden}, me puedes ayudar con mi compra porfavor.")


    
