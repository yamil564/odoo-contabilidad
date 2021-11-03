from odoo import http
from odoo.http import request
import requests
import json
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
import re
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
        return error, error_message

    @http.route("/change_invoice_type_code",type="json",method="POST",csrf=True,auth="public", website=True)
    def change_invoice_type_code(self,**kargs):

        order = request.website.sale_get_order()
        order.sudo().write({"invoice_type_code":kargs.get("invoice_type_code")})
        return True

    def checkout_redirection(self,order):
        res = super(WebsiteSaleExtend,self).checkout_redirection(order)
        return res

    @http.route(['/change_vat'], type='json', auth="public", website=True)
    def change_vat(self, **kw):
        """
            Este Método regresa la información concerniente a el numero de identificación
            :param kwargs:
            :return:
        """

        partner_id = request.env['res.partner'].sudo().search([('vat','=', str(kw.get("vat")))], limit=1)
        type = request.env['l10n_latam.identification.type'].sudo().search([('id','=', int(kw['type']))], limit=1)
        patron_ruc = re.compile("[12]\d{10}$")
        patron_dni = re.compile("\d{8}$")
        razon = False

        type = request.env['l10n_latam.identification.type'].search([('id', '=', int(kw['type']))])

        if type.l10n_pe_vat_code == '1':

            if len(kw['vat'].strip()) == 8:
                partner = self.request_migo_dni(kw['vat'].strip(), "dni")
                validate = True
            else:
                partner = False
                validate = False

        if type.l10n_pe_vat_code == '6':

            partner = False
            validate = True
            if patron_ruc.match(kw['vat']):
                vat_arr = [int(c) for c in kw['vat']]
                arr = [5,4,3,2,7,6,5,4,3,2]
                s = sum([vat_arr[r]*arr[r] for r in range(0,10)])
                num_ver = (11-s%11)%10
                if vat_arr[10] != num_ver:
                    validate = False
                else:
                    partner = self.request_migo_dni(kw['vat'].strip(), "ruc")
                    razon = partner
            else:
                validate = False
        vals = {
            'name':partner,
            'validate':validate,
            'razon':razon,
        }
        return vals

    def request_migo_dni(self, dni, type):
        companys = request.env.context.get('allowed_company_ids', False)
        if companys:
            company = request.env["res.company"].sudo().browse(companys[0])
            url = company.api_migo_endpoint + type
            token = company.api_migo_token
            headers = {'Content-Type': 'application/json'}
            if type == "dni":
                data = {"token": "yQfQ97SvS38y3ZF9GMYZjBChKa1ajM4OzuRspcm7Eq22H7OETuxj9c17Vv3F", "dni": dni}
            else:
                data = {"token": "yQfQ97SvS38y3ZF9GMYZjBChKa1ajM4OzuRspcm7Eq22H7OETuxj9c17Vv3F", "ruc": dni}
            _logger.info("De nuevo por aca")
            _logger.info("De nuevo por aca")
            _logger.info("De nuevo por aca")
            _logger.info(data)
            _logger.info(headers)
            _logger.info(url)
        else:
            return False

        try:
            res = requests.request("POST", url, headers=headers, data=json.dumps(data))
            res = res.json()
            _logger.info("Por aca mi bru")
            _logger.info("Por aca mi bru")
            _logger.info("Por aca mi bru")
            _logger.info(res)
            if res.get("success", False):
                if type == "dni":
                    return res.get("nombre", False)
                else:
                    return res.get("nombre_o_razon_social", False)
            return False
        except Exception as e:
            return False

    def _checkout_form_save(self, mode, checkout, all_values):

        Partner = request.env['res.partner']
        if mode[0] == 'new':
            partner_id = Partner.sudo().with_context(tracking_disable=True).create(checkout)
            partner_id.state_id = int(all_values['state_id'])
            partner_id.province_id = int(all_values['province_id'])
            partner_id.district_id = int(all_values['district_id'])
            partner_id = partner_id.id
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                # double check
                order = request.website.sale_get_order()
                shippings = Partner.sudo().search([("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                    return Forbidden()
                Partner.browse(partner_id).sudo().write(checkout)
        return partner_id

    # @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    # def address(self, **kw):
    #
    #     Partner = request.env['res.partner'].with_context(show_address=1).sudo()
    #     order = request.website.sale_get_order()
    #
    #     redirection = self.checkout_redirection(order)
    #     if redirection:
    #         return redirection
    #
    #     mode = (False, False)
    #     can_edit_vat = False
    #     def_country_id = order.partner_id.country_id
    #     values, errors = {}, {}
    #
    #     partner_id = int(kw.get('partner_id', -1))
    #
    #     # IF PUBLIC ORDER
    #     if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
    #         mode = ('new', 'billing')
    #         can_edit_vat = True
    #         country_code = request.session['geoip'].get('country_code')
    #         if country_code:
    #             def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
    #         else:
    #             def_country_id = request.website.user_id.sudo().country_id
    #     # IF ORDER LINKED TO A PARTNER
    #     else:
    #         if partner_id > 0:
    #             if partner_id == order.partner_id.id:
    #                 mode = ('edit', 'billing')
    #                 can_edit_vat = order.partner_id.can_edit_vat()
    #             else:
    #                 shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
    #                 if partner_id in shippings.mapped('id'):
    #                     mode = ('edit', 'shipping')
    #                 else:
    #                     return Forbidden()
    #             if mode:
    #                 values = Partner.browse(partner_id)
    #         elif partner_id == -1:
    #             mode = ('new', 'shipping')
    #         else: # no mode - refresh without post?
    #             return request.redirect('/shop/checkout')
    #
    #     # IF POSTED
    #     if 'submitted' in kw:
    #         pre_values = self.values_preprocess(order, mode, kw)
    #         _logger.info(pre_values)
    #         _logger.info(kw.items())
    #         errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
    #         post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)
    #
    #         if errors:
    #             errors['error_message'] = error_msg
    #             values = kw
    #         else:
    #             partner_id = self._checkout_form_save(mode, post, kw) #
    #             if mode[1] == 'billing':
    #                 order.partner_id = partner_id
    #                 order.with_context(not_self_saleperson=True).onchange_partner_id()
    #                 # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
    #                 order.partner_invoice_id = partner_id
    #                 if not kw.get('use_same'):
    #                     kw['callback'] = kw.get('callback') or \
    #                         (not order.only_services and (mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
    #             elif mode[1] == 'shipping':
    #                 order.partner_shipping_id = partner_id
    #
    #             order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
    #             if not errors:
    #                 return request.redirect(kw.get('callback') or '/shop/confirm_order')
    #
    #     country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
    #     country = country and country.exists() or def_country_id
    #     render_values = {
    #         'website_sale_order': order,
    #         'partner_id': partner_id,
    #         'mode': mode,
    #         'checkout': values,
    #         'can_edit_vat': can_edit_vat,
    #         'country': country,
    #         'countries': country.get_website_sale_countries(mode=mode[1]),
    #         "states": country.get_website_sale_states(mode=mode[1]),
    #         'error': errors,
    #         'callback': kw.get('callback'),
    #         'only_services': order and order.only_services,
    #     }
    #     return request.render("website_sale.address", render_values)
