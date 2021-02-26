import requests
from odoo.exceptions import UserError, ValidationError
import json
import os
import datetime
from bs4 import BeautifulSoup
import jwt
import time
# from ..utils.number_to_letter import to_word
import re
from odoo import fields
from xml.dom.minidom import parse, parseString
from requests.exceptions import (
    RequestException, Timeout, URLRequired,
    TooManyRedirects, HTTPError, ConnectionError,
    FileModeWarning, ConnectTimeout, ReadTimeout
)

# from odoo.addons.gestionit_pe_fe.api_facturacion.models import EFact21

import logging
_logger = logging.getLogger(__name__)


def enviar_doc_url(data_doc, tipoEnvio):
    data_doc["tipoEnvio"] = int(tipoEnvio)
    # efact = EFact21()
    # r = efact21.lamdba(data_doc)

    _logger.info(
        "---------------------------------------------------------------------||||||||||||||||||||||||||---------------------------------")
    _logger.info(efact.prueba())
    # _logger.info(data_doc)

    return r


def enviar_doc(self):
    self.invoice_type_code = self.journal_id.invoice_type_code_id
    if self.invoice_type_code == "01" or self.invoice_type_code == "03":
        data_doc = crear_json_fac_bol(self)
    # elif self.invoice_type_code == "07" or self.invoice_type_code == "08":
    #     data_doc = crear_json_not_cred_deb(self)
    else:
        raise UserError("Tipo de documento no valido")

    self.json_comprobante = json.dumps(data_doc, indent=4)
    data = {
        "request_json": self.json_comprobante,
        "name": self.name,
        "date_request": fields.Datetime.now(),
        "date_issue": self.invoice_date,
        "account_invoice_id": self.id
    }
    try:
        response_env = enviar_doc_url(data_doc, self.company_id.tipo_envio)
        self.json_respuesta = json.dumps(response_env.json(), indent=4)
        data.update({
            "response_json": self.json_respuesta,
        })
        if response_env.status_code == 200:
            # Envío exitoso
            response_env = response_env.json()
            if "result" in response_env:
                result = response_env["result"]
                if "sunat_status" in result:
                    if result["sunat_status"] in ["A", "O", "P", "E", "N", "B"]:
                        self.estado_emision = result["sunat_status"]
                    else:
                        self.estado_emision = "P"

                if "digest_value" in result:
                    data["digest_value"] = result["digest_value"]
                    self.digest_value = result["digest_value"]

                if "signed_xml" in result:
                    try:
                        ps = parseString(result["signed_xml"])
                        data["signed_xml_data"] = ps.toprettyxml()
                    except Exception as e:
                        data["signed_xml_data"] = result["signed_xml"]
                    data["signed_xml_data_without_format"] = result["signed_xml"]

                if "response_content_xml" in result:
                    try:
                        ps = parseString(result["response_content_xml"])
                        data["content_xml"] = ps.toprettyxml()
                    except Exception as e:
                        data["content_xml"] = result["response_content_xml"]

                if "response_xml" in result:
                    try:
                        ps = parseString(result["response_xml"])
                        data["response_xml"] = ps.toprettyxml()
                    except Exception as e:
                        data["response_xml"] = result["response_xml"]
                    data["response_xml_without_format"] = result["response_xml"]

                if "tipoDocumento" in data_doc:
                    tipo_documento = data_doc["tipoDocumento"]
                    if tipo_documento == '01':
                        data["name"] = "Factura electrónica "+self.name
                    elif tipo_documento == '03':
                        data["name"] = "Boleta Electrónica "+self.number
                    elif tipo_documento == '07':
                        data["name"] = "Nota de Crédito "+self.number
                    elif tipo_documento == '08':
                        data["name"] = "Nota de Débito "+self.number

                if "unsigned_xml" in result:
                    try:
                        ps = parseString(result["unsigned_xml"])
                        data["unsigned_xml"] = ps.toprettyxml()
                    except Exception as e:
                        data["unsigned_xml"] = result["unsigned_xml"]

                if "sunat_status" in result:
                    data["status"] = result["sunat_status"]
                if 'request_id' in response_env['result']:
                    data["api_request_id"] = result['request_id']

    except Timeout as e:
        self.estado_emision = "P"
        return {
            'name': 'Tiempo de espera excedido',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'custom.pop.message',
            'target': 'new',
            'context': {
                    'default_name': "Alerta",
                    'default_accion': "* El Comprobante ha sido generado de forma exitosa.\n* El tiempo de espera de la respuesta ha sido excedida.\n* El comprobante se enviará de forma automática luego"

            }
        }
    except ConnectionError as e:
        self.estado_emision = "P"
        return {
            'name': 'Error en la conexión',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'custom.pop.message',
            'target': 'new',
            'context': {
                    'default_name': "Alerta",
                    'default_accion': "* El Comprobante ha sido generado de forma exitosa.\n* No se ha logrado enviar el comprobante.\n* Se intentará enviar luego de forma automática."
            }
        }
    except Exception as e:
        self.estado_emision = "P"
        return {
            'name': 'Error',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'custom.pop.message',
            'target': 'new',
            'context': {
                    'default_name': "Alerta",
                    'default_accion': "* El Comprobante ha sido generada de forma exitosa.\n* "+str(e)
            }
        }
    finally:
        self.account_log_status_ids = [(0, 0, data)]


def get_tipo_cambio(self, compra_o_venta=2):  # 1 -> compra , 2->venta
    ratios = self.currency_id.rate_ids
    tipo_cambio = 1.0
    ratio_actual = False
    for ratio in ratios:
        if str(ratio.name)[0:10] == str(self.invoice_date):
            tipo_cambio = ratio.rate
            ratio_actual = True

    if ratio_actual:
        return tipo_cambio
    else:
        now = datetime.datetime.now()
        if self.invoice_date > now.strftime("%Y-%m-%d"):
            raise ValidationError(
                "Fecha de factura no valida, no se puede obtener tipo de cambio de esa fecha")
        url = "https://www.sbs.gob.pe/app/pp/SISTIP_PORTAL/Paginas/Publicacion/TipoCambioPromedio.aspx"
        r = requests.get(url)
        if r.ok:
            soup = BeautifulSoup(r.text, 'html.parser')
            tipo_cambio = float(soup.find(id="ctl00_cphContent_rgTipoCambio_ctl00__0").find_all(
                'td')[compra_o_venta].string)
            self.env['res.currency.rate'].create({
                'name': now.strftime("%Y-%m-%d"),
                'currency_id': self.currency_id.id,
                'rate': tipo_cambio
            })
            return tipo_cambio
        else:
            raise ValidationError("Error al obtener tipo de cambio en SBS")


def crear_json_fac_bol(self):

    if self.invoice_type_code == '01':
        if not re.match("^F\w{3}-\d{1,8}$", self.name):
            raise UserError("El Formato de la Factura es incorrecto.")
    elif self.invoice_type_code == '03':
        if not re.match("^B\w{3}-\d{1,8}$", self.name):
            raise UserError("El Formato de la Boleta es Incorrecto.")
    elif self.invoice_type_code == '07':
        if self.refund_invoice_id.invoice_type_code == '01':
            if not re.match("^F\w{3}-\d{1,8}$", self.name):
                raise UserError(
                    "El Formato de la Nota de Crédito para la factura es incorrecto. ")
        if self.refund_invoice_id.invoice_type_code == '03':
            if not re.match("^B\w{3}-\d{1,8}$", self.name):
                raise UserError(
                    "El Formato de la Nota de Crédito para la Boleta es Incorrecto. ")
    elif self.invoice_type_code == '08':
        if self.refund_invoice_id.invoice_type_code == '01':
            if not re.match("^F\w{3}-\d{1,8}$", self.name):
                raise UserError(
                    "El Formato de la Nota de Débito para la factura es incorrecto. ")
        if self.refund_invoice_id.invoice_type_code == '03':
            if not re.match("^B\w{3}-\d{1,8}$", self.name):
                raise UserError(
                    "El Formato de la Nota de Débito para la Boleta es Incorrecto. ")
    else:
        raise UserError("El Tipo de Documento del Comprobante es Obligatorio")

    nombreEmisor = self.company_id.partner_id.registration_name.strip()
    numDocEmisor = self.company_id.partner_id.vat.strip(
    ) if self.company_id.partner_id.vat else ""

    numDocReceptor = self.partner_id.vat.strip() if self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code in [
        "1", "6"] and self.partner_id.vat else "-"
    nombreReceptor = self.partner_id.registration_name if self.partner_id.registration_name not in [
        "-", False, "", " - "] else self.partner_id.name
    nombreReceptor = nombreReceptor.strip()
    tipoDocReceptor = self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code
    direccionReceptor = self.partner_id.street if self.partner_id.street else "-"
    nombreComercialReceptor = replace_false(
        self.partner_id.name if self.partner_id.name else self.partner_id.registration_name)

    correlativo = int(self.name.split("-")[1])
    data = {
        "company": {
            "SUNAT_user": self.company_id.sunat_user,
            "SUNAT_pass": self.company_id.sunat_pass,
            "key_private": self.company_id.key_private,
            "key_public": self.company_id.key_public,
        },
        "tipoDocumento": self.invoice_type_code,
        "fechaEmision": str(self.invoice_date),
        "idTransaccion": self.name,
        "correoReceptor": replace_false(self.partner_id.email if self.partner_id.email else "-"),
        "documento": {
            "serie": self.journal_id.code,
            "correlativo": correlativo,
            "nombreEmisor": nombreEmisor,
            "tipoDocEmisor": self.company_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
            "numDocEmisor": numDocEmisor,
            "direccionReceptor": direccionReceptor,
            "direccionOrigen": replace_false(self.company_id.partner_id.street),
            "direccionUbigeo": replace_false(self.company_id.partner_id.zip),
            "nombreComercialEmisor": replace_false(self.company_id.partner_id.registration_name),
            "tipoDocReceptor": tipoDocReceptor,
            "numDocReceptor":  numDocReceptor,
            "nombreReceptor": nombreReceptor,
            "nombreComercialReceptor": replace_false(self.partner_id.name if self.partner_id.name else self.partner_id.registration_name),
            # VERIFICAR
            # "tipoDocReceptorAsociado": replace_false(self.partner_id.tipo_documento),
            # "numDocReceptorAsociado": self.partner_id.vat if self.partner_id.tipo_documento in ["1", "6"] and self.partner_id.vat else "-",
            # "nombreReceptorAsociado": replace_false(self.partner_id.registration_name if self.partner_id.registration_name else self.partner_id.name),
            # "direccionDestino" : "",#solo para boletas
            "tipoMoneda": self.currency_id.name,
            # "sustento" : "", #solo notas
            # "tipoMotivoNotaModificatoria" : "", #solo_notas
            "mntNeto": round(self.total_venta_gravado, 2),
            "mntExe": round(self.total_venta_inafecto, 2),
            "mntExo": round(self.total_venta_exonerada, 2),
            "mntTotalIgv": round(self.amount_igv, 2),
            "mntTotal": round(self.amount_total, 2),
            # solo para facturas y boletas
            "mntTotalGrat": round(self.total_venta_gratuito, 2),
            "fechaVencimiento": str(self.invoice_date_due) if self.invoice_date_due else datetime.now().strftime("%Y-%m-%d"),
            "glosaDocumento": "VENTA",  # verificar
            "codContrato": replace_false(self.name),
            # "codCentroCosto" : "",
            # verificar
            "tipoCambioDestino": round(self.tipo_cambio_fecha_factura, 4),
            "mntTotalIsc": 0.0,
            "mntTotalOtros": 0.0,
            "mntTotalOtrosCargos": 0.0,
            # "mntTotalAnticipos" : 0.0, #solo factura y boleta
            "tipoFormatoRepresentacionImpresa": "GENERAL",
            # "mntTotalLetras": to_word(round(self.amount_total, 2), self.currency_id.name)
        },
        "descuento": {
            "mntDescuentoGlobal": round(self.total_descuento_global, 2),
            "mntTotalDescuentos": round(self.total_descuentos, 2)
        },
        # solo factura y boleta
        # "servicioHospedaje": { },
        # solo factura y boleta, con expecciones

        "indicadores": {
            # VERIFICAR ESTOS CAMPOS
            "indVentaInterna": True if self.tipo_operacion == "01" else 0,
            "indExportacion": True if self.tipo_operacion == "02" else 0,
            # "indNoDomiciliados" : False, #valido para notas
            "indAnticipo": True if self.tipo_operacion == "04" else 0,
            # "indDeduccionAnticipos" : False,
            # "indServiciosHospedaje" : False,
            "indVentaItinerante": True if self.tipo_operacion == "05" else 0
            # "indTrasladoBienesConRepresentacionImpresa" : False,
            # "indVentaArrozPilado" : False,
            # "indComprobantePercepcion" : False,
            # "indBienesTransferidosAmazonia" : False,
            # "indServiciosPrestadosAmazonia" : False,
            # "indContratosConstruccionEjecutadosAmazonia" : False

        },

        # solo factura y boleta
        # "percepcion": {
        # "mntBaseImponible" : 0.0,
        # "mntPercepcion" : 0.0,
        # "mntTotalMasPercepcion" : 0.0,
        # "tasaPercepcion" : 1.0
        # },
        # "datosAdicionales": {},
    }
    data_impuesto = []
    data_detalle = []
    data_referencia = []  # solo para notas
    data_anticipo = []  # solo facturas y boletas
    data_anexo = []  # si hay anexos

    if self.descuento_global:
        data["documento"]["descuentoGlobal"] = {
            "factor": round(self.descuento_global/100.00, 2),
            "montoDescuento": round(self.total_descuento_global, 2),
            # El atributo amount_untaxed es el monto del total de ventas sin impuestos
            "montoBase": round(self.amount_untaxed + self.total_descuento_global, 2)
        }

    # if self.numero_guia_remision:
    #     data["documento"]["numero_guia"] = self.numero_guia_remision

    # if self.nota_id:
    #     data["nota"] = self.nota_id.descripcion
    ###############
    self.total_venta_gravado = sum(
        [
            line.price_subtotal
            for line in self.invoice_line_ids
            if len([line.price_subtotal for line_tax in line.tax_ids
                    if line_tax.tax_group_id.tipo_afectacion in ["10"]])
        ])*(1-self.descuento_global/100.0)

    self.total_venta_inafecto = sum(
        [
            line.price_subtotal
            for line in self.invoice_line_ids
            if len(
                [line.price_subtotal for line_tax in line.tax_ids
                    if line_tax.tax_group_id.tipo_afectacion in ["40", "30"]])
        ])*(1-self.descuento_global/100.0)

    self.total_venta_exonerada = sum(
        [
            line.price_subtotal
            for line in self.invoice_line_ids
            if len(
                [line.price_subtotal for line_tax in line.tax_ids
                    if line_tax.tax_group_id.tipo_afectacion in ["20"]])
        ])*(1-self.descuento_global/100.0)

    self.total_venta_gratuito = sum(
        [
            line.price_unit*line.quantity
            for line in self.invoice_line_ids
            if len([1 for line_tax in line.tax_ids
                    if line_tax.tax_group_id.tipo_afectacion in ["31", "32", "33", "34", "35", "36", "37"]])
        ])
    ##########
    taxlen = 0
    for line in self.invoice_line_ids:
        for tax in line.tax_ids:
            data_impuesto.append({
                "codImpuesto": str(tax.tax_group_id.codigo),
                "montoImpuesto": round(line.tax_base_amount, 2),
                "tasaImpuesto": round(tax.amount/100, 2)
            })
            taxlen += 1

    if taxlen == 0:
        data_impuesto.append({
            "codImpuesto": "1000",
            "montoImpuesto": 0.0,
            "tasaImpuesto": 0.18
        })
    # if len(self.tax_ids) == 0:
    #     data_impuesto.append({
    #         "codImpuesto": "1000",
    #         "montoImpuesto": 0.0,
    #         "tasaImpuesto": 0.18
    #     })

    for item in self.invoice_line_ids:
        #price_unit = item.price_unit*(1-(item.discount/100)) - item.descuento_unitario
        #descuento = item.price_unit*item.discount/100 + item.descuento_unitario
        """
        price_unit = item.price_unit
        descuento_unitario = item.descuento_unitario
        descuento = 0
        tasaIgv = item.invoice_line_tax_ids[0].amount /100 if len(item.invoice_line_tax_ids) else ""
        if (item.invoice_line_tax_ids.price_include):

            if (item.invoice_line_tax_ids.amount == 0):
                montoImpuestoUni = 0
                base_imponible = price_unit
                descuento = (base_imponible*item.discount /
                             100 + descuento_unitario)
            else:
                base_imponible = price_unit / (1+tasaIgv)
                descuento_unitario = descuento_unitario / (1+tasaIgv)
                descuento = (base_imponible*item.discount /
                             100 + descuento_unitario)
                montoImpuestoUni = price_unit - base_imponible - descuento*tasaIgv
            precioItem = price_unit
        else:
            base_imponible = price_unit
            descuento = (base_imponible*item.discount/100 + descuento_unitario)
            montoImpuestoUni = (price_unit - descuento)*tasaIgv
            precioItem = price_unit + montoImpuestoUni
            base_imponible = price_unit

        montoItem = round((base_imponible) * item.quantity, 2)
        nombreItem = item.name.strip().replace("\n","")
        """
        # if item.invoice_line_tax_ids:
        #     taxes = item.invoice_line_tax_ids.compute_all(item.price_unit)
        # precioItemSinIgv = taxes["total_excluded"]

        # tasaIgv = item.invoice_line_tax_ids[0].amount / \
        #     100 if len(item.invoice_line_tax_ids) else ""

        datac = {
            "cantidadItem": round(item.quantity, 2),
            "unidadMedidaItem": item.product_uom_id.code,
            "codItem": str(item.product_id.id),
            "nombreItem": item.name[0:250].strip().replace("\n", " "),
            "precioItem": round(item.price_unit, 2) if len([item for line_tax in item.tax_ids
                                                            if line_tax.tax_group_id.tipo_afectacion in ["31", "32", "33", "34", "35", "36"]]) == 0 else 0,  # Precio unitario con IGV

            # "precioItemSinIgv": round(precioItemSinIgv, 2) if len([item for line_tax in item.tax_ids
            #                                                        if line_tax.tax_group_id.tipo_afectacion in ["31", "32", "33", "34", "35", "36"]]) == 0 else 0,  # Precio unitario sin IGV y sin descuento

            # Monto total de la línea sin IGV
            "montoItem": round(item.price_unit*item.quantity, 2) if item.no_onerosa else round(item.price_subtotal, 2),

            # "descuentoMonto": round((item.price_subtotal*item.discount/100.0)/(1-item.discount/100.0), 2),  # solo factura y boleta
            "codAfectacionIgv": item.tax_ids[0].tax_group_id.tipo_afectacion if len(item.tax_ids) else "",
            # "tasaIgv": round(tasaIgv*100, 2),
            # Monto Total del IGV
            "montoIgv": round(item.price_total-item.price_subtotal, 2),
            "codSistemaCalculoIsc": "01",  # VERIFICAR
            "montoIsc": 0.0,  # VERIFICAR
            # "tasaIsc" : 0.0, #VERIFICAR
            # VERIFICAR
            "precioItemReferencia": round(item.price_unit, 2),
            "idOperacion": str(self.id),
            "no_onerosa": True if item.no_onerosa else False
        }
        if item.discount:
            datac["descuento"] = {
                "factor": round(item.discount/100.0, 2),
                "montoDescuento": round((item.price_subtotal*item.discount/100.0)/(1-item.discount/100.0), 2),
                "montoBase": round(item.price_subtotal/(1-item.discount/100.0), 2)
            }

        data_detalle.append(datac)

    # data["impuesto"] = data_impuesto
    data["detalle"] = data_detalle
    if len(data_anticipo):
        data["anticipos"] = data_anticipo
    if len(data_anexo):
        data["anexos"] = data_anexo

    return data
    # return json.dumps(data,indent=4)


def replace_false(dato):
    if dato:
        return dato
    else:
        return ""
