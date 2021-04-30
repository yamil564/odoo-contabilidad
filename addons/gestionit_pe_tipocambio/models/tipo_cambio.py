import odoo
import requests
from odoo import api, models, fields
from datetime import date
import datetime
import json
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)


class Tipocambio(models.Model):
    _inherit = "res.currency.rate"

    fecha = fields.Date("Fecha")
    cambio_compra = fields.Float("Compra", digits=(1, 3))
    cambio_venta = fields.Float("Venta", digits=(1, 3))

    def actualizar_ratio_compra_venta(self, fecha=False):
        currency_usd = self.env['res.currency'].search([['name', '=', 'USD']])
        user_id = self.env.context.get('uid', False)

        # if user_id:
        user = self.env["res.users"].sudo().browse(user_id)
        token = user.company_id.api_migo_token
        if not fecha:
            ruta = "exchange/latest"
            data = {
                "token": token
            }
        else:
            ruta = "exchange/date"
            data = {
                "token": token,
                "fecha": fecha
            }
        url = user.company_id.api_migo_endpoint + ruta

        try:
            headers = {
                'Content-Type': 'application/json'
            }

            res = requests.request(
                "POST", url, headers=headers, data=json.dumps(data))
            res = res.json()

            if res.get("success", False):
                tipo_cambio = float(res.get("precio_venta", False))
                tipo_cambio = 1/tipo_cambio if tipo_cambio != 0.0 else 0.0
                fecha_cambio = res.get("fecha", False)
                return self.env['res.currency.rate'].create({
                    # 'name': fields.Datetime.now(),
                    'name': fecha_cambio,
                    'currency_id': currency_usd.id,
                    'rate': tipo_cambio,
                    'fecha': date.today(),
                    'cambio_compra': float(res.get("precio_compra", False)),
                    'cambio_venta': float(res.get("precio_venta", False))
                })

            return None
        except Exception as e:
            return None
            # curr_id = self.env['res.currency.rate'].search([])[0]
            # return self.env['res.currency.rate'].create({
            #     'name': fields.Datetime.now(),
            #     'currency_id': curr_id.currency_id.id,
            #     'rate': curr_id.rate,
            #     'fecha': date.today(),
            #     'cambio_compra': curr_id.cambio_compra,
            #     'cambio_venta': curr_id.cambio_venta
            # })


class invoice(models.Model):
    _inherit = "account.move"

    tipo_cambio = fields.Float("T/C", digits=(1, 3))

    @api.constrains('tipo_cambio')
    def _check_tipo_cambio(self):
        for record in self:
            if record.tipo_cambio <= 0:
                raise ValidationError(
                    "Valor del tipo de Cambio incorrecto. Debe actualizar el tipo de cambio.")

    @api.onchange('invoice_date')
    def get_ratio(self, fecha=False):
        # actualizar_ratio_compra_venta
        rate_obj = self.env['res.currency.rate']
        if fecha:
            rate = rate_obj.search([('name', "=", fecha)])
        else:
            rate = rate_obj.search([('name', "=", self.invoice_date)])

        if rate.exists():
            if self.type == "in_invoice" or self.type == "in_refund":
                self.tipo_cambio = rate[0].cambio_venta

            if self.type == "out_invoice" or self.type == "out_refund":
                self.tipo_cambio = rate[0].cambio_compra
        else:
            gr = rate_obj.actualizar_ratio_compra_venta(
                str(self.invoice_date))
            if gr != None:
                self.get_ratio()
            else:
                current_date_temp = datetime.datetime.strptime(
                    str(self.invoice_date), "%Y-%m-%d")
                newdate = current_date_temp + datetime.timedelta(days=-1)
                self.get_ratio(newdate)
                # _logger.info(newdate.strftime('%Y-%m-%d'))

                # if not self.tipo_cambio:
                #     self.tipo_cambio == 0
