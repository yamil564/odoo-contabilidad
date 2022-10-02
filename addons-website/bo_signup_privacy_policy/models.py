import logging
import werkzeug
from odoo import models,fields,api
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = "website"

    signup_privacy_policies_active = fields.Boolean("Activar",
                                            default=True)
    signup_privacy_policies_label = fields.Html("Label de Política de seguridad en registro",
                                            default="<span>He leído y acepto la <a href='/politica_privacidad' target='_blank'>Política de privacidad</a></span>") 

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    signup_privacy_policies_active = fields.Boolean("Política de seguridad en registro de cliente",
                                            related="website_id.signup_privacy_policies_active",
                                            readonly=False)
    signup_privacy_policies_label = fields.Html("Label de Política de seguridad en registro",
                                            related="website_id.signup_privacy_policies_label",
                                            readonly=False)

class ResUsers(models.Model):
    _inherit = "res.users"
    accept_privacy_policies = fields.Boolean("Acepto políticas de privacidad?",default=False)


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    accept_privacy_policies = fields.Boolean("Acepto políticas de privacidad?",default=False)



# class AuthSinupHomeCustom(AuthSignupHome):

#     def do_signup(self, qcontext):
#         """ Shared helper that creates a res.partner out of a token """
#         values = { key: qcontext.get(key) for key in ('login', 'name', 'password','accept_privacy_policies') }
#         _logger.info(request.website)
#         _logger.info(qcontext)
#         if not values:
#             raise UserError(_("The form was not properly filled in."))
#         if values.get('password') != qcontext.get('confirm_password'):
#             raise UserError(_("Passwords do not match; please retype them."))
#         if not values.get('accept_privacy_policies',False):
#             raise UserError("Debe aceptar las políticas de privacidad para poder registrarse.")

#         supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
#         lang = request.context.get('lang', '')
#         if lang in supported_lang_codes:
#             values['lang'] = lang
#         self._signup_with_values(qcontext.get('token'), values)
#         request.env.cr.commit()