#!/usr/bin/env python2

from odoo import models, api, fields, _
from odoo.exceptions import UserError
from datetime import datetime
import json
from . import oauth
import requests
from xml.dom.minidom import parse, parseString
import pytz
from pytz import timezone
import os
import time
from datetime import datetime, timedelta
import math
import re
from odoo.addons.gestionit_pe_fe.models.account.api_facturacion import api_models
from odoo.addons.gestionit_pe_fe.models.account.api_facturacion.controllers import main
from odoo.addons.gestionit_pe_fe.models.account.oauth import send_summary_xml
import logging
_logger = logging.getLogger(__name__)


class SummarySequence(models.Model):
    _name = "summary.sequence"

    type = fields.Selection(selection=[('RA','RA'),('RC','RC')])
    next_number = fields.Integer("Siguiente Número",default=1)
    date = fields.Date("Fecha")
    company_id = fields.Many2one("res.company",default=lambda self:self.env.company.id)

    @api.model
    def get_next_number(self,date,type,company_id):
        seq = self.search([("type","=",type),("company_id","=",company_id),("date","=",date)])
        if seq.exists():
            seq.next_number = seq.next_number + 1
        else:
            seq = self.create({"type":type,"company_id":company_id,"date":date})

        return seq.next_number

class AccountInvoice(models.Model):
    _inherit = "account.move"
    account_summary_id = fields.Many2one("account.summary",
                                         string="Resumen Diario",
                                         ondelete="set null",
                                         default=False)

class AccountSummaryLine(models.Model):
    _name = "account.summary.line"

    account_summary_id = fields.Many2one(
        "account.summary", string="Resumen Diario", ondelete="set null")
    invoice_id = fields.Many2one("account.move")
    serie = fields.Char(string="Serie")
    correlativo = fields.Char(string="Correlativo")
    tipo_documento = fields.Selection(string="Tipo de Documento", selection=[(
        '03', "Boleta"), ("07", "Nota de Crédito"), ("08", "Nota de Débito")])
    tipo_doc_receptor = fields.Char(string="Tipo documento Receptor")
    numero_doc_receptor = fields.Char(string="Número documento receptor")
    tipo_moneda = fields.Char(string="Tipo de Moneda")

    numero_documento_inicio = fields.Char(string="Número de Documento Inicio")
    numero_documento_fin = fields.Char(string="Número de Documento Fin")

    codigo_afectacion_igv = fields.Char(string="Código de Afectación al IGV")
    monto_igv = fields.Float(string="Monto IGV", digits=(10, 2))
    monto_isc = fields.Float(string="Monto ISC", digits=(10, 2))
    # cod_operacion = fields.Char(string="Código Operación",default="1")

    cod_operacion = fields.Selection(string="Código Operación", selection=[
                                     ("1", "Adicionar"), ("2", "Modificar"), ("3", "Anular")])

    monto_total = fields.Float(string="Monto Total", digits=(10, 2))
    monto_neto = fields.Float(string="Monto Neto", digits=(10, 2))
    monto_exe = fields.Float(string="Monto Inafecto", digits=(10, 2))
    monto_exo = fields.Float(string="Monto Exonerado", digits=(10, 2))
    monto_exp = fields.Float(string="Monto Exportación", digits=(10, 2))
    monto_grat = fields.Float(string="Monto Gratuito", digits=(10, 2))
    monto_otros = fields.Float(string="Monto Otros", digits=(10, 2))
    tipo_doc_referencia = fields.Char(string="Tipo doc. referencia")
    num_doc_referencia = fields.Char(string="Número doc. referencia")


class AccountSummary(models.Model):
    _name = "account.summary"
    _rec_name = "identificador_resumen"
    _order = "create_date desc"

    company_id = fields.Many2one("res.company", required=True, string="Compañia",
                                 default=lambda self: self.env.user.company_id.id)
    fecha_generacion = fields.Date("Fecha de Generación", default=fields.Date.today(), required="True")
    fecha_emision_documentos = fields.Date("Fecha de Emisión de Documentos", default=fields.Date.today(), required="True")
    identificador_resumen = fields.Char("Identificador de Resumen", default="Resumen Diario",related="current_log_status_id.name")
    summary_line_ids = fields.One2many("account.summary.line", "account_summary_id", string="Líneas de Resumen", ondelete='cascade')
    resumen_diario_json = fields.Text("Resumen Diario JSON")

    cod_operacion = fields.Selection(string="Código Operación", selection=[("1", "Adicionar"), ("2", "Modificar"), ("3", "Anular")], required="True", default="1")
        
    account_invoice_ids = fields.One2many("account.move", "account_summary_id", string="Comprobantes")
    
    ticket = fields.Char("Ticket")
    summary_ticket = fields.Char("Ticket", related="current_log_status_id.ticket")

    summary_description_response = fields.Char(related="current_log_status_id.summary_description_response")
    summary_code_response = fields.Char(related="current_log_status_id.summary_code_response")
    # estado = fields.Selection(selection=[("borrador", "Borrador"),
    #                                      ("enviado", "Enviado"),
    #                                      ("resumen_valido", "Resumen Valido"),
    #                                      ("resumen_rechazado", "Resumen Rechazado")], default="borrador")

    estado_emision = fields.Selection([
        ('B', 'Borrador'),
        ('A', 'Aceptado'),
        ('E', 'Enviado a SUNAT'),
        ('N', 'Envio Erroneo'),
        ('O', 'Aceptado con Observacion'),
        ('R', 'Rechazado'),
        ('P', 'Pendiente de envio a SUNAT'),
    ], string="Estado Emision a SUNAT", related="current_log_status_id.status")

    summary_sequence = fields.Integer(string="Sec. de envío del día",related="current_log_status_id.account_summary_sequence")
    json_respuesta = fields.Text(string="JSON de respuesta")
    digestValue = fields.Text(string="JSON Estado de Resumen")

    account_log_status_ids = fields.One2many("account.log.status", "account_summary_id", string="Registro de Envíos", copy=False)
    current_log_status_id = fields.Many2one("account.log.status",copy=False,string="Actual envío")

    # @api.multi
    def unlink(self):
        for record in self:
            if record.estado_emision in ["B",False]:
                result = super(AccountSummary, record).unlink()
            else:
                raise UserError("El resumen debe estar en estado borrador para ser eliminado")

    numero_envio = fields.Integer(string="Número de Envío")
    

    @api.constrains('fecha_generacion')
    def consistencia_fecha_generacion_emision(self):
        if self.fecha_emision_documentos > self.fecha_generacion:
            raise UserError("La fecha de generación del Resumen Diario debe ser mayor o igual a las fecha de emisión de los comprobantes")
        if self.fecha_generacion > fields.Date.today():
            raise UserError("La fecha de generación del Resumen diario no debe ser mayor a la fecha de hoy.")

    # @api.onchange("account_invoice_ids")
    # def _change_account_invoice_ids(self):
    #     for record in self:
    #         account_invoices = record.account_invoice_ids
    #         account_invoices = [{
    #             "id": invoice.id,
    #             "serie": invoice.name.split("-")[0],
    #             "correlativo":int(invoice.name.split("-")[1]),
    #             "tipo_documento":invoice.journal_id.invoice_type_code_id,
    #             "tipo_doc_receptor":invoice.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
    #             "numero_doc_receptor":invoice.partner_id.vat,
    #             "tipo_moneda":invoice.currency_id.name,
    #             # "codigo_afectacion_igv":(invoice.tax_line_ids[0].tax_id.tipo_afectacion_igv.code if len(invoice.tax_line_ids) > 0 else "10"),
    #             "monto_total":invoice.amount_total,
    #             "monto_neto":invoice.total_venta_gravado,
    #             "monto_igv":invoice.amount_tax,
    #             "monto_isc":0.0,
    #             "monto_exe":invoice.total_venta_inafecto,
    #             "monto_exo":invoice.total_venta_exonerada,
    #             "monto_grat":invoice.total_venta_gratuito,
    #             "monto_exp":0.0,
    #             "monto_otros":0.0,
    #             "account_summary_id":record.id,
    #             "tipo_doc_referencia":invoice.reversed_entry_id.invoice_type_code if invoice.reversed_entry_id else "",
    #             "num_doc_referencia":invoice.reversed_entry_id.name if invoice.reversed_entry_id else ""
    #         } for invoice in account_invoices]

    #         summary_line_ids = []
    #         for ai in account_invoices:
    #             summary_line_ids.append(
    #                 self.env["account.summary.line"].create(ai).id)
    #         record.summary_line_ids = [(6, _, summary_line_ids)]
    #         record.generar_resumen_diario()

    # def actualizar_lineas_resumen(self):
    #     for record in self:
    #         account_invoices = record.account_invoice_ids
    #         account_invoices = [{
    #             "id": invoice.id,
    #             "serie": invoice.name.split("-")[0],
    #             "correlativo":int(invoice.name.split("-")[1]),
    #             "tipo_documento":invoice.invoice_type_code,
    #             "tipo_doc_receptor":invoice.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code if invoice.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code in ["0", "1", "4", "6", "7", "A"] else "0",
    #             "numero_doc_receptor":invoice.partner_id.vat,
    #             "tipo_moneda":invoice.currency_id.name,
    #             # "codigo_afectacion_igv":(invoice.tax_line_ids[0].tax_id.tipo_afectacion_igv.code if len(invoice.tax_line_ids) > 0 else "10"),
    #             "monto_total":invoice.amount_total,
    #             "monto_neto":invoice.total_venta_gravado,
    #             "monto_igv":invoice.amount_tax,
    #             "monto_isc":0.0,
    #             "monto_exe":invoice.total_venta_inafecto,
    #             "monto_exo":invoice.total_venta_exonerada,
    #             "monto_grat":invoice.total_venta_gratuito,
    #             "monto_exp":0.0,
    #             "monto_otros":0.0,
    #             "tipo_doc_referencia":invoice.reversed_entry_id.invoice_type_code if invoice.reversed_entry_id else "",
    #             "num_doc_referencia":invoice.reversed_entry_id.name if invoice.reversed_entry_id else ""
    #         } for invoice in account_invoices]

    #         if len(record.summary_line_ids):
    #             for sl in record.summary_line_ids:
    #                 sl.unlink()

    #         summary_line_ids = []
    #         for ai in account_invoices:
    #             summary_line_ids.append(
    #                 self.env["account.summary.line"].create(ai).id)

    #         record.summary_line_ids = [(6, _, summary_line_ids)]

    def cargar_comprobantes(self):
        if self.cod_operacion in ["2","3"]:
            raise UserError("La carga de comprobantes solo esta disponible para el código de operación 1-Adicionar")
        if not self.fecha_emision_documentos:
            raise UserError("La fecha de emisión de los documentos es obligatoria.")
        if not self.company_id:
            raise UserError("Debe seleccionar una compañía")

        # Boletas de Venta
        account_invoices = self.env["account.move"].search([("invoice_date","=",self.fecha_emision_documentos),
                                                                ("state","in",["posted"]),
                                                                ("journal_id.invoice_type_code_id","=","03"),
                                                                ("partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code","in",["0","1","6"]),
                                                                ("partner_id.vat","!=",False),
                                                                ("company_id","=",self.company_id.id),
                                                                ("estado_comprobante_electronico", "in", ["-", False, "0_NO_EXISTE"])])

        # account_invoices = [b for b in account_invoices]

        # Listar las notas de Crédito
        nota_credito_ids = self.env["account.move"].search([("invoice_date","=",self.fecha_emision_documentos),
                                                                    ("state","in",["posted"]),
                                                                    ("journal_id.invoice_type_code_id","=","07"),
                                                                    ("partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code","in",["0","1","6"]),
                                                                    ("partner_id.vat","!=",False),
                                                                    ("reversed_entry_id","!=",False),
                                                                    ("company_id","=",self.company_id.id),
                                                                    ("estado_comprobante_electronico", "in", ["-", False, "0_NO_EXISTE"])])

        # nota_credito_ids = [nc for nc in nota_credito_ids if nc.reversed_entry_id.invoice_type_code == "03"]
        nota_credito_ids = nota_credito_ids.filtered(lambda nc: nc.reversed_entry_id.invoice_type_code == "03" and nc.reversed_entry_id.estado_comprobante_electronico == "1_ACEPTADO")

        # Listar las notas de Débito
        nota_debito_ids = self.env["account.move"].search([("invoice_date","=",self.fecha_emision_documentos),
                                                                    ("state","in",["posted"]),
                                                                    ("journal_id.invoice_type_code_id","=","08"),
                                                                    ("partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code","in",["0","1","6"]),
                                                                    ("partner_id.vat","!=",False),
                                                                    ("reversed_entry_id.estado_comprobante_electronico","=","1_ACEPTADO"),
                                                                    ("estado_comprobante_electronico", "in", ["-", False, "0_NO_EXISTE"])])

        # nota_debito_ids = [nd for nd in nota_debito_ids if nd.reversed_entry_id.invoice_type_code == "03"]
        nota_debito_ids = nota_debito_ids.filtered(lambda nd: nd.debit_origin_id.invoice_type_code == "03" and nd.debit_origin_id.estado_comprobante_electronico == "1_ACEPTADO")

        # Consolidado Boleta y Notas Asociadas
        account_invoices = account_invoices + nota_credito_ids + nota_debito_ids

        account_summary_lines = [{
            "invoice_id": invoice.id,
            "serie": invoice.name.split("-")[0],
            "correlativo":int(invoice.name.split("-")[1]),
            "tipo_documento":invoice.journal_id.invoice_type_code_id,
            "tipo_doc_receptor":invoice.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
            "numero_doc_receptor":invoice.partner_id.vat,
            "tipo_moneda":invoice.currency_id.name,
            # "codigo_afectacion_igv":(invoice.tax_line_ids[0].tax_id.tipo_afectacion_igv.code if len(invoice.tax_line_ids) > 0 else "10"),
            "monto_total":invoice.amount_total,
            "monto_neto":invoice.total_venta_gravado,
            "monto_igv":invoice.amount_tax,
            "cod_operacion": self.cod_operacion,
            "monto_isc":0.0,
            "monto_exe":invoice.total_venta_inafecto,
            "monto_exo":invoice.total_venta_exonerada,
            "monto_grat":invoice.total_venta_gratuito,
            "monto_exp":0.0,
            "monto_otros":0.0,
            "tipo_doc_referencia":invoice.reversed_entry_id.invoice_type_code if invoice.reversed_entry_id else "",
            "num_doc_referencia":invoice.reversed_entry_id.name if invoice.reversed_entry_id else "",
            "account_summary_id":self.id
        } for invoice in account_invoices[:200]]

        self.account_invoice_ids = [(6, 0, [account_invoice["invoice_id"] for account_invoice in account_summary_lines])]

        self.summary_line_ids = [(6, 0, [])]
        if len(account_summary_lines) > 0:
            self.summary_line_ids = [(0,0,line) for line in account_summary_lines]

        

    @api.constrains('cod_operacion')
    def _check_cod_operacion(self):
        for record in self:
            if record.estado_emision not in [False,"B"]:
                raise UserError(
                    "Sólo puede cambiar el código de operación cuando el estado del comprobante posee estado 'Borrador v  '")

    @api.onchange("cod_operacion")
    def _onchange_cod_operacion(self):
        for sl in self.summary_line_ids:
            sl.cod_operacion = self.cod_operacion

    def convertir_a_borrador(self):
        if self.current_log_status_id:
            self.current_log_status_id.action_set_last_log_unlink()
        # for record in self:
            # record.estado_emision = "B"

    # Por Eliminar
    def cargar_resumen_lineas(self):
        account_invoices = self.account_invoice_ids
        account_summary_lines = [{
            "id": invoice.id,
            "serie": invoice.name.split("-")[0],
            "correlativo":int(invoice.name.split("-")[1]),
            "tipo_documento":invoice.journal_id.invoice_type_code_id,
            "tipo_doc_receptor":invoice.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
            "numero_doc_receptor":invoice.partner_id.vat,
            "tipo_moneda":invoice.currency_id.name,
            "monto_total":invoice.amount_total,
            "monto_neto":invoice.total_venta_gravado,
            "monto_igv":invoice.amount_tax,
            "cod_operacion": self.cod_operacion,
            "monto_isc":0.0,
            "monto_exe":invoice.total_venta_inafecto,
            "monto_exo":invoice.total_venta_exonerada,
            "monto_grat":invoice.total_venta_gratuito,
            "monto_exp":0.0,
            "monto_otros":0.0,
            "tipo_doc_referencia":invoice.reversed_entry_id.invoice_type_code if invoice.reversed_entry_id else "",
            "num_doc_referencia":invoice.reversed_entry_id.name if invoice.reversed_entry_id else ""
        } for invoice in account_invoices]

        self.account_invoice_ids = [
            (6, 0, [account_invoice["id"] for account_invoice in account_summary_lines])]

        if self.summary_line_ids:
            for sl in self.summary_line_ids:
                sl.unlink()
        sl_ids = []
        for i in account_summary_lines:
            sl = self.env['account.summary.line'].create(i)
            sl_ids.append(sl.id)

        self.summary_line_ids = [(6, 0, sl_ids)]

    def generar_identificador_resumen(self):
        for record in self:
            if not record.numero_envio:
                documents = self.env['account.summary'].search(
                    [['fecha_generacion', '=', record.fecha_generacion]])
                documents = documents.sorted(
                    key=lambda r: r.numero_envio, reverse=True)

                if len(documents) == 0:
                    record.numero_envio = 1
                else:
                    record.numero_envio = documents[0].numero_envio + 1

                if record.fecha_generacion:
                    fecha = record.fecha_generacion.strftime("%Y%m%d")
                    record.identificador_resumen = "RC-"+fecha + \
                        "-"+str(record.numero_envio).zfill(3)

    def generar_resumen_diario(self):
        for record in self:
            nombreEmisor = self.company_id.partner_id.registration_name.strip()
            numDocEmisor = self.company_id.partner_id.vat.strip(
            ) if self.company_id.partner_id.vat else ""
            resumen_diario_json = {}
            resumen_diario_json["company"] = {
                "numDocEmisor": numDocEmisor,
                "nombreEmisor": nombreEmisor,
                "SUNAT_user": self.company_id.sunat_user,
                "SUNAT_pass": self.company_id.sunat_pass,
                "key_private": self.company_id.cert_id.key_private,
                "key_public": self.company_id.cert_id.key_public,
            }
            resumen_diario_json["resumen"] = {
                "numDocEmisor": record.company_id.partner_id.vat,
                "tipoDocEmisor": record.company_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
                "fechaReferente": record.fecha_emision_documentos.strftime("%Y-%m-%d"),
                "nombreEmisor": record.company_id.partner_id.name,
                "id": record.numero_envio
            }
            resumen_diario_json["fechaGeneracion"] = record.fecha_generacion.strftime(
                "%Y-%m-%d")
            resumen_diario_json["tipoResumen"] = "RC"
            resumen_diario_json["idTransaccion"] = record.identificador_resumen
            resumen_diario_json["detalle"] = []

            for summary_line in record.summary_line_ids:
                # _logger.info(summary_line)
                resumen_diario_json["detalle"].append({
                    "serie": summary_line.serie,
                    "correlativo": summary_line.correlativo,
                    "tipoDocumento": summary_line.tipo_documento,
                    "tipoDocReceptor": summary_line.tipo_doc_receptor,
                    "numDocReceptor": summary_line.numero_doc_receptor,
                    "tipoMoneda": summary_line.tipo_moneda,
                    # "codAfectacionIgv": summary_line.codigo_afectacion_igv,
                    "mntIgv": round(summary_line.monto_igv, 2),
                    "mntIsc": round(summary_line.monto_isc, 2),
                    "codOperacion": summary_line.cod_operacion,
                    "mntTotal": round(summary_line.monto_total, 2),
                    "mntNeto": round(summary_line.monto_neto, 2),
                    "mntExo": round(summary_line.monto_exo, 2),
                    "mntExe": round(summary_line.monto_exe, 2),
                    "mntExp": round(summary_line.monto_exp, 2),
                    "mntGrat": round(summary_line.monto_grat, 2),
                    "mntOtros": round(summary_line.monto_otros, 2),
                    "tipoDocReferencia": summary_line.tipo_doc_referencia,
                    "numDocReferencia": summary_line.num_doc_referencia
                })
            record.resumen_diario_json = json.dumps(
                resumen_diario_json, indent=4)

    def _generate_summary_json(self):
        summary_sequence = self.env["summary.sequence"].sudo().get_next_number(self.fecha_generacion,"RC",self.company_id.id)
        name = "{}-{}-{}".format("RC",
                                self.fecha_generacion.strftime("%Y%m%d"),
                                str(summary_sequence).zfill(3))
        
        nombreEmisor = self.company_id.partner_id.registration_name.strip()
        numDocEmisor = self.company_id.partner_id.vat.strip() if self.company_id.partner_id.vat else ""
        resumen_diario_json = {}
        resumen_diario_json["company"] = {
            "numDocEmisor": numDocEmisor,
            "nombreEmisor": nombreEmisor,
            "SUNAT_user": self.company_id.sunat_user,
            "SUNAT_pass": self.company_id.sunat_pass,
            "key_private": self.company_id.cert_id.key_private,
            "key_public": self.company_id.cert_id.key_public,
        }
        resumen_diario_json["resumen"] = {
            "numDocEmisor": self.company_id.partner_id.vat,
            "tipoDocEmisor": self.company_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
            "fechaReferente": self.fecha_emision_documentos.strftime("%Y-%m-%d"),
            "nombreEmisor": self.company_id.partner_id.name,
            "id":summary_sequence
        }
        resumen_diario_json["fechaGeneracion"] = self.fecha_generacion.strftime("%Y-%m-%d")
        resumen_diario_json["tipoResumen"] = "RC"
        resumen_diario_json["idTransaccion"] = name
        resumen_diario_json["detalle"] = []

        for summary_line in self.summary_line_ids:
            resumen_diario_json["detalle"].append({
                "serie": summary_line.serie,
                "correlativo": summary_line.correlativo,
                "tipoDocumento": summary_line.tipo_documento,
                "tipoDocReceptor": summary_line.tipo_doc_receptor,
                "numDocReceptor": summary_line.numero_doc_receptor,
                "tipoMoneda": summary_line.tipo_moneda,
                "mntIgv": round(summary_line.monto_igv, 2),
                "mntIsc": round(summary_line.monto_isc, 2),
                "codOperacion": summary_line.cod_operacion,
                "mntTotal": round(summary_line.monto_total, 2),
                "mntNeto": round(summary_line.monto_neto, 2),
                "mntExo": round(summary_line.monto_exo, 2),
                "mntExe": round(summary_line.monto_exe, 2),
                "mntExp": round(summary_line.monto_exp, 2),
                "mntGrat": round(summary_line.monto_grat, 2),
                "mntOtros": round(summary_line.monto_otros, 2),
                "tipoDocReferencia": summary_line.tipo_doc_referencia,
                "numDocReferencia": summary_line.num_doc_referencia
            })
        return resumen_diario_json

    def action_generate_and_signed_xml(self):
        if not self.company_id:
            raise UserError("El campo de compañía es Obligatoria.")
        tipo_envio = self.company_id.tipo_envio
        summary_json = self._generate_summary_json()

        credentials = {
            "ruc": summary_json["company"]["numDocEmisor"],
            'razon_social': summary_json["company"]["nombreEmisor"],
            'usuario': summary_json["company"]["SUNAT_user"],
            'password': summary_json["company"]["SUNAT_pass"],
            'key_private': summary_json["company"]["key_private"],
            'key_public': summary_json["company"]["key_public"],
        }
        request = main.handle(summary_json,credentials)
        log_status = {
            "account_summary_id":self.id,
            "request_json": json.dumps(summary_json,indent=4),
            "name": summary_json.get("idTransaccion"),
            "account_summary_sequence":summary_json.get("id"),
            "date_request": self.fecha_generacion,
            "date_issue": self.fecha_emision_documentos,
            "status":"P",
            "digest_value":request.get("digest_value","-"),
            "signed_xml_data":request.get("signed_xml","-") if request.get("signed_xml",False) else "",
            "signed_xml_with_creds":parseString(request.get("final_xml")).toprettyxml() if request.get("final_xml",False) else "",
        }
        log_status_obj = self.env["account.log.status"].sudo().create(log_status)
        log_status_obj.sudo().action_set_last_log()


    def action_send_summary(self):
        if not self.current_log_status_id:
            self.action_generate_and_signed_xml()
        result = {}
        try:
            result = send_summary_xml(self)
            self.current_log_status_id.write(result)
        except Exception as e:
            _logger.info(e)
            return result

    def post(self):
        pass

    # def btn_enviar_resumen_diario(self):
    #     if self.cod_operacion in ["2", "3"]:
    #         if len(self.account_invoice_ids) != len([inv for inv in self.account_invoice_ids if inv.estado_comprobante_electronico == "1_ACEPTADO"]):
    #             self.estado_emision = "P"
    #         else:
    #             self.cargar_resumen_lineas()
    #             self.generar_identificador_resumen()
    #             self.generar_resumen_diario()
    #             self.enviar_resumen_diario()
    #     elif self.cod_operacion == "1":
    #         self.cargar_resumen_lineas()
    #         self.generar_identificador_resumen()
    #         self.generar_resumen_diario()
    #         self.enviar_resumen_diario()
    

    def enviar_resumen_diario(self):
        if not self.company_id:
            raise UserError("El campo de compañía es Obligatoria.")
        tipo_envio = self.company_id.tipo_envio
        data = json.loads(self.resumen_diario_json)

        try:
            response_env = oauth.enviar_doc_resumen_url(data, tipo_envio)
        except Exception as e:
            self.estado_emision = "P"
            return 0
        response = response_env
        self.json_respuesta = json.dumps(response, indent=4)

        if response_env["success"]:
            result = response.get("result", False)
            self.estado_emision = response["sunat_status"]
            self.ticket = response["ticket"]
            return True, ""
        else:
            recepcionado, estado_emision, msg_error = oauth.extraer_error(
                response)
            if recepcionado:
                self.estado_emision = estado_emision
                return True, msg_error
            else:
                return False, msg_error

    def cron_consulta_estado_resumen(self):
        resumenes = self.env["account.summary"].search([["estado_emision", "=", "E"]])
        for resumen in resumenes:
            try:
                resumen.consulta_estado_resumen()
            except Exception as e:
                pass
            self.env.cr.commit()
        return True

    def action_request_status_ticket(self):
        if not self.current_log_status_id:
            raise UserError("El campo de ticket esta vacío")
        self.current_log_status_id.action_request_status_ticket()

    # Por eliminar
    def consulta_estado_resumen(self):
        if not self.ticket:
            raise UserError("El campo de Ticket esta vacío")

        nombreEmisor = self.company_id.partner_id.registration_name.strip()
        numDocEmisor = self.company_id.partner_id.vat.strip() if self.company_id.partner_id.vat else ""

        summary = {
            "company": {
                "numDocEmisor": numDocEmisor,
                "nombreEmisor": nombreEmisor,
                "SUNAT_user": self.company_id.sunat_user,
                "SUNAT_pass": self.company_id.sunat_pass,
                "key_private": self.company_id.cert_id.key_private,
                "key_public": self.company_id.cert_id.key_public,
            },
            "ticket": self.ticket,
            "tipoEnvio": int(self.company_id.tipo_envio)
        }

        response = api_models.consultaResumen(summary)
        # r = requests.post(endpoint, headers=headers, data=json.dumps(data))

        # response = r.json()

        # os.system("echo '%s'"%(json.dumps(r.json(), indent=4)))

        # result = response.get("result", False)
        if response:
            status = response.get("status", False)
            if status:
                self.estado_emision = status
                if status == "A":
                    if self.cod_operacion == "1":
                        self.account_invoice_ids.sudo().write({"estado_comprobante_electronico": "1_ACEPTADO"})
                        # self.estado = "resumen_valido"
                    elif self.cod_operacion == "3":
                        self.account_invoice_ids.sudo().write({"estado_comprobante_electronico": "2_ANULADO"})
                        # self.estado = "resumen_valido"
            else:
                raise UserError(json.dumps(response.get("description")))
            data = {}
            if response.get("status"):
                data["status"] = response["status"]
            if response.get("digestValue"):
                data["digest_value"] = response.get("digestValue")
            if response.get("description"):
                data["description"] = response.get("description")
            if response.get("cdr"):
                try:
                    ps = parseString(response.get("cdr"))
                    data["response_xml"] = ps.toprettyxml()
                except Exception as e:
                    data["response_xml"] = response.get("cdr")

            data["account_summary_id"] = self.id
            self.env["account.log.status"].sudo().create(data)

        else:
            raise UserError(json.dumps(response))

    def cron_crear_resumenes_diarios(self):
        # tz = self.env.user.tz or "America/Lima"
        # fecha_ayer = datetime.strptime(datetime.now(tz=timezone(tz)), '%Y-%m-%d')
        # fecha_ayer = datetime.strftime(fecha_ayer, '%Y-%m-%d')
        fecha_ayer = datetime.now().strftime('%Y-%m-%d')

        invoices = self.env["account.move"].search([("estado_comprobante_electronico","in",["0_NO_EXISTE","-"]),
                                                            ("name","!=",False),
                                                            ("state","=","posted"),
                                                            ("partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code","in",["0","1","6"]),
                                                            ("partner_id.vat","!=",False),
                                                            ("invoice_date","<",fecha_ayer),
                                                            # ("account_summary_id.cod_operacion","in",[False,"3"]),
                                                            ('invoice_type_code','=','03')])

        invoices += self.env["account.move"].search([("invoice_date","<",fecha_ayer),
                                                        ("state","=","posted"),
                                                        ("invoice_type_code","=","07"),
                                                        ("partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code","in",["0","1","6"]),
                                                        ("partner_id.vat","!=",False),
                                                        ("reversed_entry_id","!=",False),
                                                        ("estado_comprobante_electronico","in",["0_NO_EXISTE","-"]),
                                                        ("reversed_entry_id.invoice_type_code","=","03"),
                                                        # ("account_summary_id.cod_operacion","in",[False,"3"]),
                                                        ("reversed_entry_id.estado_comprobante_electronico","=","1_ACEPTADO")])
        
        invoices += self.env["account.move"].search([("invoice_date","<",fecha_ayer),
                                                        ("state","=","posted"),
                                                        ("invoice_type_code","=","08"),
                                                        ("partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code","in",["0","1","6"]),
                                                        ("partner_id.vat","!=",False),
                                                        ("debit_origin_id","!=",False),
                                                        ("estado_comprobante_electronico","in",["0_NO_EXISTE","-"]),
                                                        ("debit_origin_id.invoice_type_code","=","03"),
                                                        # ("account_summary_id.cod_operacion","in",[False,"3"]),
                                                        ("debit_origin_id.estado_comprobante_electronico","=","1_ACEPTADO")])

        try:
            for company in invoices.mapped("company_id"):
                invoices_by_company = invoices.filtered(
                    lambda inv: inv.company_id == company and re.match("^B\w{3}-\d{1,8}$", inv.name))
                invoice_dates = list(
                    set(invoices_by_company.mapped("invoice_date")))

                for invoice_date in invoice_dates:
                    invoices_by_company_by_date = invoices_by_company.filtered(
                        lambda inv: inv.invoice_date == invoice_date)
                    chunks = [invoices_by_company_by_date[x:x+300]
                              for x in range(0, len(invoices_by_company_by_date), 300)]
                    for invs in chunks:
                        resumen = {
                            "fecha_generacion": datetime.now(),
                            "fecha_emision_documentos": invoice_date,
                            "cod_operacion": "1",
                            "account_invoice_ids": [(6, 0, invs.mapped("id"))],
                            "company_id": company.id
                        }
                        resumen_obj = self.env["account.summary"].sudo().create(resumen)
                        resumen_obj.cargar_resumen_lineas()
                        resumen_obj.generar_identificador_resumen()
                        resumen_obj.generar_resumen_diario()
                        resumen_obj.enviar_resumen_diario()
                        self.env.cr.commit()
        except Exception as e:
            _logger.info(e)
            return True


class AccountSummaryAnularComprobante(models.TransientModel):
    _name = 'account.summary.anulacion'
    _description = 'Anular Comprobante'

    account_invoice_id = fields.Many2one(
        "account.move", string="Comprobante Electrónico")

    def btn_anular_comprobante(self):
        resumen = {
            "fecha_generacion": fields.Date.today(),
            "fecha_emision_documentos": self.account_invoice_id.invoice_date,
            "cod_operacion": "3",
            "account_invoice_ids": [(6, 0, [self.account_invoice_id.id])]
        }
        resumen_obj = self.env["account.summary"].create(resumen)
        self.account_invoice_id.resumen_anulacion_id = resumen_obj.id
        resumen_obj.generar_identificador_resumen()
        resumen_obj.cargar_resumen_lineas()
        resumen_obj.generar_resumen_diario()

        resumen_obj.btn_enviar_resumen_diario()
