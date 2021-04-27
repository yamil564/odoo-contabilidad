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

    """
    def actualizar_ratio_compra_venta(self):

        url = "http://www.sunat.gob.pe/a/txt/tipoCambio.txt"
        r = requests.get(url)
        if r.ok:
            valores = r.text.split('|')
            self.fecha = self.name[0:10]
           # self.fecha=valores[0][6:10]+"-"+ valores[0][3:5]+"-"+valores[0][0:2]
            self.cambio_compra = float(valores[1])
            self.cambio_venta = float(valores[2])
    """

    def actualizar_ratio_compra_venta(self):
        currency_usd = self.env['res.currency'].search([['name', '=', 'USD']])
        user_id = self.env.context.get('uid', False)
        if user_id:
            user = self.env["res.users"].sudo().browse(user_id)
            url = user.company_id.api_migo_endpoint + "exchange/latest"
            token = user.company_id.api_migo_token

        try:
            headers = {
                'Content-Type': 'application/json'
            }
            data = {
                "token": token
            }
            res = requests.request(
                "POST", url, headers=headers, data=json.dumps(data))
            res = res.json()

            if res.get("success", False):
                # return res
                tipo_cambio = float(res.get("precio_venta", False))
                tipo_cambio = 1/tipo_cambio if tipo_cambio != 0.0 else 0.0
                return self.env['res.currency.rate'].create({
                    'name': fields.Datetime.now(),
                    'currency_id': currency_usd.id,
                    'rate': tipo_cambio,
                    'fecha': date.today(),
                    'cambio_compra': float(res.get("precio_compra", False)),
                    'cambio_venta': float(res.get("precio_venta", False))
                })
            return None
        except Exception as e:
            # raise e
            curr_id = self.env['res.currency.rate'].search([])[0]
            return self.env['res.currency.rate'].create({
                'name': fields.Datetime.now(),
                'currency_id': curr_id.currency_id.id,
                'rate': curr_id.rate,
                'fecha': date.today(),
                'cambio_compra': curr_id.cambio_compra,
                'cambio_venta': curr_id.cambio_venta
            })


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
    def get_ratio(self):
        if self.invoice_date:
            rate = self.env['res.currency.rate'].search(
                [('fecha', "=", self.invoice_date)])
            if rate.exists():
                if self.type == "in_invoice" or self.type == "in_refund":
                    self.tipo_cambio = rate[0].cambio_venta

                if self.type == "out_invoice" or self.type == "out_refund":
                    self.tipo_cambio = rate[0].cambio_compra
            else:
                if not self.tipo_cambio:
                    self.tipo_cambio == 0
