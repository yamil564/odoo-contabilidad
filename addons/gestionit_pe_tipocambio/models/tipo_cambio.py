import odoo
import requests
from odoo import api, models, fields
from datetime import date,datetime
import json
from pytz import timezone
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)


class ResCurrency(models.Model):
    _inherit = "res.currency"
    
    cambio_compra = fields.Float("T/C Compra", digits=(1, 4),compute="_compute_current_rate_sale_purchase")
    cambio_venta = fields.Float("T/C Venta", digits=(1, 4),compute="_compute_current_rate_sale_purchase")

    @api.depends('rate_ids.name')
    def _compute_current_rate_sale_purchase(self):
        for currency in self:
            currency.cambio_compra = currency.rate_ids[:1].cambio_compra
            currency.cambio_venta = currency.rate_ids[:1].cambio_venta

    def action_get(self):
        view_id = self.sudo().env.ref("gestionit_pe_tipocambio.view_form_rate_simple").id
        tz = self.env.user.tz or "America/Lima"
        today = datetime.now(tz=timezone(tz))
        action = {
            "name":"Tipo de Cambio {}".format(self.name),
            "type":"ir.actions.act_window",
            "res_model":"res.currency.rate",
            "views":[[view_id,"form"]],
            "view_mode":"form",
            "target":"new",
        }
        res_id = self.env["res.currency.rate"].sudo().search([("name","=",today.strftime("%Y-%m-%d"))])
        
        if res_id.exists():
            action.update({"res_id":res_id[0].id})
        else: 
            action.update({"context":{"default_currency_id":self.id,"default_name":today.strftime("%Y-%m-%d"),"default_fecha":today}})
        return action


class Tipocambio(models.Model):
    _inherit = "res.currency.rate"

    # fecha = fields.Date("Fecha")
    cambio_compra = fields.Float("T/C Compra", digits=(1, 4))
    cambio_venta = fields.Float("T/C Venta", digits=(1, 4))

    def actualizar_ratio_compra_venta_pen_usd(self,company_id):
        currency_usd = self.env['res.currency'].search([['name', '=', 'USD']])
        company = self.env["res.company"].sudo().browse(company_id)
        token = company.api_migo_token
        endpoint = company.api_migo_endpoint
        fecha_hoy = datetime.now(tz=timezone("America/Lima")).strftime("%Y-%m-%d")
        currency_rate_exists = self.env["res.currency.rate"].sudo().search([("currency_id","=",currency_usd.id),("name","=",fecha_hoy),("company_id","=",company_id)]).exists()
        if currency_rate_exists:
            return None

        if not endpoint:
            return None
        else:
            endpoint = endpoint.strip()
            endpoint = endpoint if endpoint[-1] == "/" else "{}/".format(endpoint)
            
        url = "{}exchange/date".format(endpoint)
        
        data = {
            "token": token,
            "fecha": fecha_hoy
        }
        
        try:
            headers = {
                'Content-Type': 'application/json'
            }

            res = requests.request("POST", url, headers=headers, data=json.dumps(data))
            res = res.json()
            if res.get("success", False):
                tipo_cambio = float(res.get("precio_venta", False))
                tipo_cambio = 1/tipo_cambio if tipo_cambio != 0.0 else 0.0
                currency_rate = self.env['res.currency.rate'].sudo().create({
                    'name': fecha_hoy,
                    'currency_id': currency_usd.id,
                    'rate': tipo_cambio,
                    'cambio_compra': float(res.get("precio_compra", False)),
                    'cambio_venta': float(res.get("precio_venta", False)),
                    'company_id':company.id
                })
                return currency_rate
            return None
        except Exception as e:
            return None

    def save(self):
        return

class AccountMove(models.Model):
    _inherit = "account.move"

    tipo_cambio = fields.Float(string="T/C", digits=(1, 4))
    # fecha_cambio = fields.Date(string="Fecha de cambio")

    @api.onchange("invoice_date")
    def _change_fecha_cambio(self):
        self.fecha_cambio = self.invoice_date

    def post(self):
        tz = self.env.user.tz or "America/Lima"
        for move in self:
            if not move.invoice_date:
                move.invoice_date = datetime.now(tz = timezone(tz))

            if move.company_currency_id != move.currency_id:
                if not move.tipo_cambio or move.tipo_cambio == 0 :
                    currency_rate = self.env["res.currency.rate"].sudo().search([("name","=",move.invoice_date.strftime("%Y-%m-%d")),("currency_id","=",move.currency_id.id)])
                    if currency_rate.exists():
                        if move.journal_id.type == "sale":
                            move.tipo_cambio = currency_rate[0].cambio_compra

                        if move.journal_id.type == "purchase":
                            move.tipo_cambio =  currency_rate[0].cambio_venta
                    else:
                        raise UserError("Debe actualizar el tipo de cambio de compra/venta para la fecha {}.".format(move.invoice_date.strftime("%Y-%m-%d")))
            else:
                move.tipo_cambio =  1

        super(AccountMove, self).post()

    # @api.constrains('tipo_cambio')
    # def _check_tipo_cambio(self):
    #     for record in self:
    #         if record.tipo_cambio <= 0:
    #             raise ValidationError(
    #                 "Valor del tipo de Cambio incorrecto. Debe actualizar la fecha de facturación.")

    @api.onchange("invoice_date","currency_id")
    def get_ratio(self):
        if self.invoice_date:
            if self.company_currency_id != self.currency_id:
                # if not self.tipo_cambio or self.tipo_cambio == 0:
                currency_rate = self.env["res.currency.rate"].sudo().search([("name","=",self.invoice_date.strftime("%Y-%m-%d")),("currency_id","=",self.currency_id.id)])
                if currency_rate.exists():
                    if self.journal_id.type == "sale":
                        self.tipo_cambio = currency_rate[0].cambio_compra

                    if self.journal_id.type == "purchase":
                        self.tipo_cambio =  currency_rate[0].cambio_venta
                else:
                    raise UserError("Debe actualizar el tipo de cambio de compra/venta para la fecha {}.".format(self.invoice_date.strftime("%Y-%m-%d")))
            else:
                self.tipo_cambio =  1