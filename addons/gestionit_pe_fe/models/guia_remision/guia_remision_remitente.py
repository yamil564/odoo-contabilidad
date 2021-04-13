from requests.exceptions import (
    RequestException, Timeout, URLRequired,
    TooManyRedirects, HTTPError, ConnectionError,
    FileModeWarning, ConnectTimeout, ReadTimeout
)
from odoo import models, api, fields
from odoo.exceptions import UserError, ValidationError, Warning
import requests
import os
import re
import json
import re
from ..account.api_facturacion import api_models
import logging
_logger = logging.getLogger(__name__)


patron_dni = re.compile("\d{8}$")
patron_ruc = re.compile("[12]\d{10}$")

codigo_unidades_de_medida = [
    "DZN",
    "DAY",
    "HUR",
    "LTR",
    "NIU",
    "CMT",
    "GLL",
    "OZI",
    "GRM",
    "GLL",
    "KGM",
    "LBR",
    "MTR",
    "LBR",
    "SMI",
    "ONZ",
    "FOT",
    "INH",
    "LTN",
    "BX"
]


class ModalidadTransporte(models.Model):
    _name = "gestionit.modalidad_transporte"
    code = fields.Char("Código")
    name = fields.Char("Descripción")


class MotivoTraslado(models.Model):
    _name = "gestionit.motivo_traslado"
    code = fields.Char("Código")
    name = fields.Char("Descripción")
    active = fields.Boolean("Activo", default=True)


class GuiaRemisionLine(models.Model):
    _name = "gestionit.guia_remision_line"
    product_id = fields.Many2one("product.product", required=True)
    uom_id = fields.Many2one("uom.uom", string="UM", required=True)
    qty = fields.Float(string="Cantidad")
    guia_remision_id = fields.Many2one(
        "gestionit.guia_remision", ondelete='cascade')
    description = fields.Char(string="Descripción", required=True)
    stock_picking_id = fields.Many2one("stock.picking", "Movimiento de Stock")
    sequence = fields.Integer()

    @api.constrains('uom_id')
    def _check_uom_id(self):
        for record in self:
            if record.uom_id.code not in codigo_unidades_de_medida:
                raise UserError(
                    "La unidad de medida seleccionada no posee un código válido.")

    @api.constrains('description')
    def _check_description(self):
        for record in self:
            if len(record.description) < 4 and len(record.description) > 100:
                raise UserError(
                    "La Descripción del producto debe tener por lo menos 4 carácteres y a lo ás 100 carácteres.")

    @api.onchange('description')
    def _onchange_description(self):
        if self.description:
            self.description = self.description.strip().replace("\n", "")

    @api.onchange('product_id')
    def _onchange_product(self):
        for record in self:
            self.description = self.product_id.name
            self.uom_id = self.product_id.uom_id.id

    @api.constrains('qty')
    def _check_qty(self):
        for record in self:
            if record.qty < 0:
                raise UserError(
                    "La cantidad de las líneas de producto no pueden ser negativas.")


class ResPartner(models.Model):
    _inherit = 'res.partner'
    es_conductor = fields.Boolean(string="Es Conductor", default=False)
    es_empresa_transporte_publico = fields.Boolean(
        string="Es empresa de transporte publico", default=False)
    vehiculo_ids = fields.One2many(
        "gestionit.vehiculo", "propietario_id", string="Vehículos")
    licencia = fields.Char("Licencia")

    def action_view_conductores_privados(self):
        return {
            'name': 'Conductores Privados',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [[self.env.ref("gestionit_pe_fe.view_tree_partner_conductor").id, "tree"], [self.env.ref("gestionit_pe_fe.view_form_partner_conductor").id, "form"]],
            'res_model': 'res.partner',
            'target': 'self',
            'domain': [('es_conductor', '=', True), ('parent_id', '!=', False), ('parent_id', '=', self.env.user.company_id.id)],
            'context': {
                "default_es_conductor": True,
                "default_parent_id": self.env.user.company_id.id,
                "default_country_id": 173
            }
        }


class Vehiculo(models.Model):
    _name = 'gestionit.vehiculo'
    _rec_name = "numero_placa"
    numero_placa = fields.Char("Número de placa")
    tipo_transporte = fields.Selection(selection=[("carretera", "Carretera"),
                                                  ("maritimo", "Maritimo"),
                                                  ("ferroviaria", "Ferroviaria"),
                                                  ("area", "Aerea"),
                                                  ("pluvial", "Pluvial"),
                                                  ("lacustre", "Lacustre")], default="carretera")
    marca = fields.Char("Marca")
    modelo = fields.Char("Modelo")
    inscripcion_mtc = fields.Char("N° Inscripción MTC")
    operativo = fields.Selection(string="Operativo",
                                 selection=[("operativo", "Operativo"),
                                            ("fuera_de_servicio", "Fuera de Servicio")],
                                 default="operativo")

    descripcion = fields.Text("Descripción")
    propietario_id = fields.Many2one("res.partner", "Propietario")
    company_id = fields.Many2one("res.company", string="Compañía",
                                 default=lambda self: self.env.user.company_id.id)

    def action_view_vehiculos_privados(self):
        return {
            'name': 'Vehículos Privados',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'views': [[self.env.ref("gestionit_pe_fe.view_tree_vehiculo").id, "tree"], [self.env.ref("gestionit_pe_fe.view_form_vehiculo").id, "form"]],
            'res_model': 'gestionit.vehiculo',
            'target': 'self',
            'domain': [('propietario_id', '=', self.env.user.company_id.id)],
            'context': {
                "default_propietario_id": self.env.user.company_id.id,
            }
        }


class PopupFormSelectUbigeo(models.TransientModel):
    _name = 'gestionit.popup_form_seleccion_ubigeo'

    departamento_id = fields.Many2one(
        "res.country.state", string="Departamento")
    provincia_id = fields.Many2one("res.country.state", string="Provincia")
    distrito_id = fields.Many2one(
        "res.country.state", string="Distrito", required=True)
    guia_remision_id = fields.Many2one(
        "gestionit.guia_remision", required=True)
    tipo_lugar = fields.Selection(
        selection=[("partida", "Partida"), ("llegada", "Llegada")], required=True)
    ubigeo = fields.Char("Ubigeo")
    ubigeo_code = fields.Many2one("res.country.state", string="Ubigeo Code")

    @api.onchange('distrito_id')
    def _onchange_ubigeo(self):
        for record in self:
            record.ubigeo = record.distrito_id.code if record.distrito_id else ""

    def set_ubigeo(self):
        record = self
        # os.system("echo '{}'".format(record.guia_remision_id.numero))
        if record.tipo_lugar == "partida":
            # os.system("echo '{}'".format("partida"))
            record.guia_remision_id.write(
                {"lugar_partida_ubigeo": record.ubigeo})
            # record.guia_remision_id.write({"lugar_partida_ubigeo":record.ubigeo})
        elif record.tipo_lugar == "llegada":
            # os.system("echo '{}'".format("llegada"))
            record.guia_remision_id.write(
                {"lugar_llegada_ubigeo": record.ubigeo})


class GuiaRemision(models.Model):
    _name = "gestionit.guia_remision"
    _rec_name = "numero"

    company_id = fields.Many2one("res.company", string="Compañía",
                                 default=lambda self: self.env.user.company_id.id,
                                 states={'validado': [('readonly', True)]})

    company_partner_id = fields.Many2one(
        "res.partner", related="company_id.partner_id", readonly=True)

    # SERIE Y CORRELATIVO
    journal_id = fields.Many2one("account.journal", string="Serie", states={
                                 'validado': [('readonly', True)]})
    correlativo = fields.Integer(string="Correlativo", copy=False)
    serie = fields.Char("Prefijo", related="journal_id.code", copy=False)
    numero = fields.Char(
        "Número", default="Guía de Remisión - Borrador", copy=False)
    name = fields.Char("Nombre", index=True, states={
                       'validado': [('readonly', True)]}, copy=False)

    request_json = fields.Text("Petición JSON", states={
                               'validado': [('readonly', True)]}, copy=False)
    response_json = fields.Text("Respuesta JSON", states={
                                'validado': [('readonly', True)]}, copy=False)

    @api.model
    def default_get(self, flds):
        res = super(GuiaRemision, self).default_get(flds)
        journals = self.env["account.journal"].search(
            [("invoice_type_code_id", "=", "09")])
        if len(journals) > 0:
            res.update({
                "journal_id": journals[0].id
            })
            res.update({
                "correlativo": journals[0].sequence_number_next,
                "numero": "Guía de Remisión Electrónica",
                "motivo_traslado": "01",
                # "modalidad_transporte":"02",
                "fecha_emision": fields.Datetime.now()
            })

        return res

    @api.onchange("journal_id")
    def _onchange_numero_guia_remision(self):
        for record in self:
            if record.journal_id:
                record.correlativo = record.journal_id.sequence_number_next

    @api.onchange("modalidad_transporte")
    def _onchange_modalidad_transporte(self):
        for record in self:
            if record.modalidad_transporte == "01":
                record.conductor_privado_partner_id = False
                record.vehiculo_privado_id = False
                record.conductor_publico_id = False
                record.vehiculo_publico_id = False
            elif record.modalidad_transporte == "02":
                record.transporte_partner_id = False

    def default_direccion_llegada_id(self):
        return self.destinatario_partner_id.child_ids[0].id if len(self.destinatario_partner_id.child_ids) else False

    @api.onchange("motivo_traslado")
    def _onchange_motivo_traslado(self):
        for record in self:
            record.numero_bultos = 0
            record.partner_direccion_llegada_id = False
            record.partner_direccion_partida_id = False
            # record.destinatario_partner_id = False
            record.proveedor_partner_id = False
            record.direccion_llegada_id = False
            record.direccion_partida_id = False
            if record.motivo_traslado in ['01', '09', '19', '13', '09']:
                record.partner_direccion_partida_id = record.company_partner_id.id
                record.partner_direccion_llegada_id = record.destinatario_partner_id.id
                record.direccion_partida_id = record.company_partner_id.child_ids[0].id if len(
                    record.company_partner_id.child_ids) else False
                record.direccion_llegada_id = record.default_direccion_llegada_id()
            if record.motivo_traslado in ['04', '18']:
                record.partner_direccion_llegada_id = record.company_partner_id.id
                record.partner_direccion_partida_id = record.company_partner_id.id
                record.destinatario_partner_id == record.company_partner_id.id
            if record.motivo_traslado in ['02']:
                record.destinatario_partner_id = record.company_partner_id.id
                record.partner_direccion_llegada_id = record.company_partner_id.id

    @api.constrains('peso_bruto_total')
    def _check_peso_bruto_total(self):
        for record in self:
            if record.peso_bruto_total < 0:
                raise UserError(
                    "El peso bruto total del envío debe ser mayor a 0.")

    # DESTINATARIO
    motivo_traslado = fields.Selection(selection="_list_motivo_traslado", string="Motivo de Traslado", states={
                                       'validado': [('readonly', True)]})

    def _list_motivo_traslado(self):
        motivo_traslado_objs = self.env["gestionit.motivo_traslado"].search([])
        return [(mt.code, mt.name) for mt in motivo_traslado_objs]

    destinatario_partner_id = fields.Many2one(
        "res.partner", string="Destinatario", states={'validado': [('readonly', True)]})
    destinatario_tipo_documento_identidad = fields.Char(
        string="Tipo de Documento", related="destinatario_partner_id.l10n_latam_identification_type_id.name")
    #destinatario_tipo_documento_identidad_id = fields.Many2one("einvoice.catalog.06",string="Tipo de Documento",related="destinatario_partner_id.catalog_06_id")
    destinatario_numero_documento_identidad = fields.Char(
        string="Número de Documento", related="destinatario_partner_id.vat")
    destinatario_direccion = fields.Char(
        string="Dirección", related="destinatario_partner_id.street")
    destinatario_ubigeo = fields.Char(
        string="Ubigeo", related="destinatario_partner_id.ubigeo")
    #destinatario_ubigeo_code = fields.Many2one("res.country.state",string="Ubigeo Destinatario Code")

    proveedor_partner_id = fields.Many2one("res.partner", string="Proveedor")
    proveedor_tipo_documento_identidad = fields.Char(
        string="Tipo de Documento", related="proveedor_partner_id.l10n_latam_identification_type_id.name")
    #proveedor_tipo_documento_identidad_id = fields.Many2one("einvoice.catalog.06",string="Tipo de Documento",related="proveedor_partner_id.catalog_06_id")
    proveedor_numero_documento_identidad = fields.Char(
        string="Número de Documento", related="proveedor_partner_id.vat")
    proveedor_direccion = fields.Char(
        string="Dirección", related="proveedor_partner_id.street")
    proveedor_ubigeo = fields.Char(
        string="Ubigeo", related="proveedor_partner_id.ubigeo")
    #proveedor_ubigeo_code = fields.Many2one("res.country.state",string="Ubigeo Proveedor Code")

    @api.onchange("destinatario_partner_id")
    def _onchange_destinatario_partner(self):
        for record in self:
            record.proveedor_partner_id = False
            # 01 - VENTA
            # 09 - EXPORTACIÓN
            # 19 - TRASLADO A ZONA PRIMARIA
            #13 - OTROS
            if record.motivo_traslado in ['01', '09', '19', '13']:
                # record.direccion_llegada_id = False
                record.partner_direccion_llegada_id = record.destinatario_partner_id.id
                record.partner_direccion_partida_id = record.company_partner_id.id
            # 04 - TRASLADO ENTRE ESTABLECIMIENTOS DE LA MISMA EMPRESA
            # 18 - TRASLADO A EMISOR ITINERANTE CP
            if record.motivo_traslado in ['04', '18']:
                record.partner_direccion_llegada_id = record.company_partner_id.id
                record.partner_direccion_partida_id = record.company_partner_id.id
            # 08-EXPORTACIÓN
            if record.motivo_traslado in ['09']:
                record.partner_direccion_partida_id = record.company_partner_id.id
                record.direccion_llegada_id = False
                record.partner_direccion_llegada_id = record.destinatario_partner_id.id
            # 08-IMPORTACIÓN
            if record.motivo_traslado in ['08']:
                record.partner_direccion_partida_id = record.proveedor_partner_id.id
                record.direccion_llegada_id = False
                record.partner_direccion_llegada_id = record.destinatario_partner_id.id

    @api.onchange("proveedor_partner_id")
    def _onchange_proveedor_partner(self):
        for record in self:
            #record.destinatario_partner_id = False
            # 02-COMPRA
            if record.motivo_traslado in ['02']:
                record.direccion_partida_id = False
                record.partner_direccion_llegada_id = record.company_partner_id.id
                record.partner_direccion_partida_id = record.proveedor_partner_id.id
            # 08-IMPORTACIÓN
            if record.motivo_traslado in ['08']:
                record.direccion_partida_id = False
                record.partner_direccion_partida_id = record.proveedor_partner_id.id
                record.partner_direccion_llegada_id = record.destinatario_partner_id.id

    # DOCUMENTOS ASOCIADOS
    documento_asociado = fields.Selection(selection=[("comprobante_pago", "Factura/Boleta"),
                                                     ("orden_venta", "Venta"),
                                                     ("movimiento_stock", "Movimiento de Stock")],
                                          string="Documento Asociado", default="movimiento_stock")

    comprobante_pago_ids = fields.Many2many(
        "account.move", string="Comprobante de Pagos")

    movimiento_stock_ids = fields.Many2many(
        "stock.picking", string="Movimientos", states={'validado': [('readonly', True)]})

    sale_order_ids = fields.Many2many("sale.order", string="Ventas", states={
                                      'validado': [('readonly', True)]})

    # @api.onchange("documento_asociado")
    # def _onchange_documento_asociado(self):
    #     for record in self:
    #         if record.documento_asociado:
    #             record.guia_remision_line_ids = [(6,0,[])]

    @api.onchange("movimiento_stock_ids")
    def _onchange_movimiento_stock(self):
        for record in self:
            guia_remision_lines = []
            guia_remision_lines_temp = {}
            ids = []

            if record.documento_asociado == "movimiento_stock":
                record.guia_remision_line_ids = [(6, 0, [])]
                for movimiento_stock_id in record.movimiento_stock_ids:
                    for move_lines in movimiento_stock_id.move_ids_without_package:
                        guia_remision_lines += [{
                                                "product_id": mls.product_id.id,
                                                "description": mls.product_id.name,
                                                "qty": mls.quantity_done,
                                                "uom_id": mls.uom_id.id,
                                                "stock_picking_id": movimiento_stock_id.id,
                                                } for mls in move_lines]

                for line in guia_remision_lines:
                    if line["product_id"] not in guia_remision_lines_temp:
                        guia_remision_lines_temp[line["product_id"]] = line
                    else:
                        guia_remision_lines_temp[line["product_id"]
                                                 ]["qty"] += line["qty"]

                guia_remision_lines = list(guia_remision_lines_temp.values())
                # _logger.info(guia_remision_lines)
                for line in guia_remision_lines:
                    ids.append(
                        self.env["gestionit.guia_remision_line"].create(line).id)

                record.guia_remision_line_ids = [(6, 0, ids)]

    @api.onchange("comprobante_pago_ids")
    def _onchange_comprobante_pago(self):
        for record in self:
            guia_remision_lines = []
            guia_remision_lines_temp = {}

            if record.documento_asociado == "comprobante_pago":
                record.guia_remision_line_ids = [(6, 0, [])]
                for comprobante_pago in record.comprobante_pago_ids:
                    for invoice_line in comprobante_pago.invoice_line_ids:
                        guia_remision_lines += [{
                                                "product_id": inv_line.product_id.id,
                                                "description": inv_line.name,
                                                "qty": inv_line.quantity,
                                                "uom_id": inv_line.product_uom_id.id,
                                                "stock_picking_id": False,
                                                } for inv_line in invoice_line]

                for line in guia_remision_lines:
                    if line["product_id"] not in guia_remision_lines_temp:
                        guia_remision_lines_temp[line["product_id"]] = line
                    else:
                        guia_remision_lines_temp[line["product_id"]
                                                 ]["qty"] += line["qty"]

                guia_remision_lines = list(guia_remision_lines_temp.values())
                record.guia_remision_line_ids = [
                    (0, 0, grl) for grl in guia_remision_lines]

    @api.onchange("sale_order_ids")
    def _onchange_sale_orders(self):
        for record in self:
            guia_remision_lines = []
            guia_remision_lines_temp = {}
            if record.documento_asociado == "orden_venta":
                record.guia_remision_line_ids = [(6, 0, [])]
                for sale_order in record.sale_order_ids:
                    # for line in sale_order.order_line:
                    guia_remision_lines += [{
                        "product_id": line.product_id.id,
                        "description": line.name,
                        "qty": line.product_uom_qty,
                        "uom_id": line.product_uom.id,
                        "stock_picking_id": False
                    } for line in sale_order.order_line]
                for line in guia_remision_lines:
                    if line.get("product_id", False) not in guia_remision_lines_temp:
                        guia_remision_lines_temp[line["product_id"]] = line
                    else:
                        guia_remision_lines_temp[line["product_id"]
                                                 ]["qty"] += line["qty"]

                guia_remision_lines = list(guia_remision_lines_temp.values())
                record.guia_remision_line_ids = guia_remision_lines

    # ENVÍO
    fecha_emision = fields.Date(string="Fecha de Emisión", states={
                                'validado': [('readonly', True)]})
    fecha_inicio_traslado = fields.Date(string="Fecha inicio de traslado", states={
                                        'validado': [('readonly', True)]})
    #peso_bruto_total_uom_id = fields.Many2one("product.uom",string="UM",default="_default_peso_bruto_total_uom")

    peso_bruto_total = fields.Float(string="Peso Bruto Total (KGM)", states={
                                    'validado': [('readonly', True)]})

    # modalidad_transporte = fields.Selection(selection="_list_modalidad_transporte", string="Modalidad de Transporte", states={'validado': [('readonly', True)]})
    modalidad_transporte = fields.Selection(
        selection="_list_modalidad_transporte", string="Modalidad de Transporte")

    def _list_modalidad_transporte(self):
        modalidad_transporte_objs = self.env["gestionit.modalidad_transporte"].search([
        ])
        return [(mt.code, mt.name) for mt in modalidad_transporte_objs]

    numero_bultos = fields.Integer(string="Número de Bultos", states={
                                   'validado': [('readonly', True)]})

    partner_direccion_partida_id = fields.Many2one("res.partner")
    direccion_partida_id = fields.Many2one(
        "res.partner", states={'validado': [('readonly', True)]})
    lugar_partida_direccion = fields.Char(
        string="Lugar de Partida - Dirección")
    lugar_partida_ubigeo_code = fields.Many2one(
        "res.country.state", string="Partida Ubigeo Code")

    @api.onchange("direccion_partida_id")
    def _onchange_direccion_partida(self):
        for record in self:
            record.lugar_partida_direccion = record.direccion_partida_id.street
            record.lugar_partida_ubigeo_code = record.direccion_partida_id.district_id.id

    partner_direccion_llegada_id = fields.Many2one("res.partner")
    direccion_llegada_id = fields.Many2one(
        "res.partner", states={'validado': [('readonly', True)]})
    lugar_llegada_direccion = fields.Char(
        string="Lugar de llegada - Dirección")
    lugar_llegada_ubigeo_code = fields.Many2one(
        "res.country.state", string="Llegada Ubigeo Code")

    @api.onchange("direccion_llegada_id")
    def _onchange_direccion_llegada(self):
        for record in self:
            record.lugar_llegada_direccion = record.direccion_llegada_id.street
            record.lugar_llegada_ubigeo_code = record.direccion_llegada_id.district_id.id

    # DETALLE DE ENVÍO
    guia_remision_line_ids = fields.One2many("gestionit.guia_remision_line", "guia_remision_id",
                                             string="Detalle de líneas",
                                             ondelete='cascade', states={'validado': [('readonly', True)]})

    # TRANSPORTE PRIVADO
    conductor_privado_partner_id = fields.Many2one(
        "res.partner", string="Conductor", states={'validado': [('readonly', True)]})
    vehiculo_privado_id = fields. Many2one(
        "gestionit.vehiculo", string="Vehículo", states={'validado': [('readonly', True)]})

    # TRANSPORTE PÚBLICO
    transporte_partner_id = fields.Many2one(
        "res.partner", string="Empresa Transportista", states={'validado': [('readonly', True)]})
    conductor_publico_id = fields.Many2one("res.partner", string="Conductor", states={
                                           'validado': [('readonly', True)]})
    vehiculo_publico_id = fields.Many2one(
        "gestionit.vehiculo", string="Vehículo", states={'validado': [('readonly', True)]})

    state = fields.Selection(
        selection=[('borrador', 'Borrador'), ('validado', 'Validado')], default="borrador")
    digest_value = fields.Char("DigestValue")
    estado_emision = fields.Selection(
        selection=[
            ('B', 'Borrador'),
            ('A', 'Aceptado'),
            ('E', 'Enviado a SUNAT'),
            ('N', 'Envio Erróneo'),
            ('O', 'Aceptado con Observación'),
            ('R', 'Rechazado'),
            ('P', 'Pendiente de envió a SUNAT'),
        ],
        string="Estado Emisión a SUNAT",
        copy=False,
        default="B",
        states={'validado': [('readonly', True)]}
    )

    def set_view_lugar_partida_ubigeo(self):

        return {
            'name': 'Lugar de Partida de Ubigeo',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            "views": [[self.env.ref("gestionit_pe_fe.view_popup_form_seleccion_ubigeo").id, "form"]],
            'res_model': 'gestionit.popup_form_seleccion_ubigeo',
            'target': 'new',
            'context': {
                    "default_guia_remision_id": self.id,
                    "default_tipo_lugar": "partida",
            }
        }

    def set_view_lugar_llegada_ubigeo(self):
        return {
            'name': 'Lugar de llegada de Ubigeo',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            "views": [[self.env.ref("gestionit_pe_fe.view_popup_form_seleccion_ubigeo").id, "form"]],
            'res_model': 'gestionit.popup_form_seleccion_ubigeo',
            'target': 'new',
            'context': {
                    "default_guia_remision_id": self.id,
                    "default_tipo_lugar": "llegada",
            }
        }

    def validar_datos_compania(self):
        errors = []
        if not self.company_id.partner_id.vat:
            errors.append(
                "* No se tiene configurado el RUC de la empresa emisora.")
        elif not patron_ruc.match(self.company_id.partner_id.vat):
            errors.append(
                "* El RUC de la empresa emisora no tiene el formato de RUC.")

        if not self.company_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code:
            errors.append(
                "* No se tiene configurado el tipo de documento de la empresa emisora")
        elif self.company_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code != '6':
            errors.append(
                "* El Tipo de Documento de la empresa emisora debe ser RUC")
        if not self.company_id.partner_id.ubigeo:
            errors.append(
                "* No se encuentra configurado el Ubigeo de la empresa emisora.")
        if not self.company_id.partner_id.street:
            errors.append(
                "* No se encuentra configurado la dirección de la empresa emisora.")
        if not self.company_id.partner_id.name:
            errors.append(
                "* No se encuentra configurado la Razón Social de la empresa emisora.")
        return errors

    def validar_datos_destinatario(self):
        errors = []
        partner = self.destinatario_partner_id
        if not partner.l10n_latam_identification_type_id.l10n_pe_vat_code:
            errors.append(
                "* El tipo de Documento del destinatario es obligatorio")
        else:
            if partner.l10n_latam_identification_type_id.l10n_pe_vat_code == "6":
                if not partner.vat:
                    errors.append(
                        "* El Número de documento del destinatario esta vacío.")
                elif not patron_ruc.match(partner.vat):
                    errors.append(
                        "* El Número de documento del destinatario tiene un RUC inválido.")
            elif partner.l10n_latam_identification_type_id.l10n_pe_vat_code == "1":
                if not partner.vat:
                    errors.append(
                        "* El Número de documento del destinatario esta vacío.")
                elif not patron_dni.match(partner.vat):
                    errors.append(
                        "* El Número de documento del destinatario tiene un DNI inválido.")
            else:
                errors.append(
                    "* El tipo de Documento del Destinatario no es válido, seleccion un RUC o DNI ")

        if not partner.name:
            errors.append(
                "* El nombre o razón social del destinatario esta vacío.")
        elif len(partner.name) < 3:
            errors.append(
                "* El nombre o razón social del destinatario debe poseer más de 3 carácteres.")
        return errors

    def validar_motivo_traslado(self):
        errors = []
        motivoTraslado = self.motivo_traslado

        if self.motivo_traslado == "08" and self.numero_bultos == 0:
            errors.append(
                "* El número de bulltos o Pallets es mayor a 0 sólo cuando es Importación.")
        elif self.motivo_traslado == "08" and self.numero_bultos < 0:
            errors.append(
                "* El número de bulltos o Pallets no puede ser negativo.")

        if not motivoTraslado:
            errors.append("* El Motivo de Traslado es Obligatorio.")
        motivo_traslado_activos = self.env["gestionit.motivo_traslado"].sudo().search([
            ("active", "=", True)])

        if motivoTraslado not in [mt.code for mt in motivo_traslado_activos]:
            errors.append(
                "* El Motivo de Traslado seleccionado no existe o no esta habilitado. Consulte con el Administrador")
        return errors

    def validar_datos_envio(self):
        errors = []
        if type(self.peso_bruto_total) != float:
            errors.append(
                "* El tipo de dato del Peso Total es {} y debería ser Flotante".format(type(self.peso_bruto_total)))
        elif self.peso_bruto_total == 0:
            errors.append("* El Peso Total debe ser mayor a 0.")

        return errors

    def validar_ubigeo(self, ubigeo):
        ubigeo_objs = self.env["res.country.state"].sudo().search(
            [("code", "=", ubigeo)])
        if ubigeo_objs.exists():
            return True
        else:
            return False

    def validar_lugar_partida(self):
        errors = []
        if not self.lugar_partida_direccion:
            errors.append(
                "* La dirección del lugar de partida es obligatorio.")
        elif len(self.lugar_partida_direccion) < 6 and len(self.lugar_partida_direccion) >= 100:
            errors.append(
                "* La dirección del lugar de partida tiene como mínimo 6 carácteres.")

        if not self.lugar_partida_ubigeo_code:
            errors.append("* El ubigeo del lugar de partida es obligatorio.")
        elif not self.validar_ubigeo(self.lugar_partida_ubigeo_code.code):
            errors.append("* El ubigeo de la dirección de partida no existe.")

        return errors

    def validar_lugar_llegada(self):
        errors = []
        if not self.lugar_llegada_direccion:
            errors.append(
                "* La dirección del lugar de llegada es obligatorio.")
        elif len(self.lugar_llegada_direccion) < 6 and len(self.lugar_llegada_direccion) >= 100:
            errors.append(
                "* La dirección del lugar de llegada tiene como mínimo 6 carácteres.")

        if not self.lugar_llegada_ubigeo_code:
            errors.append("* El ubigeo del lugar de llegada es obligatorio.")
        elif not self.validar_ubigeo(self.lugar_llegada_ubigeo_code.code):
            errors.append("* El ubigeo de la dirección de llegada no existe.")

        return errors

    def validar_guia_remision_lineas(self):
        errors = []
        if len(self.guia_remision_line_ids) == 0:
            errors.append(
                "* La guía debe tener al menos un elemento en el detalle de envío.")

        for guia_remision_line in self.guia_remision_line_ids:
            if not guia_remision_line.product_id:
                errors.append(
                    "* El producto de una de las líneas del detalle está vacío.")

            if not guia_remision_line.description:
                errors.append(
                    "* La descripción de una de las líneas del detalle está vacío.")
            elif len(guia_remision_line.description) < 4 or len(guia_remision_line.description) > 250:
                errors.append(
                    "* La longitud de la descripción de un producto debe poseer una longitud mayor a 4 y menor a 250 carácteres.")

            if not guia_remision_line.uom_id:
                errors.append(
                    "* La unidad de medida del producto [{}] esta vacía".format(guia_remision_line.description))
            elif not guia_remision_line.uom_id.code:
                errors.append(
                    "* La unidad de medida del producto [{}] no tiene un código asociado. Comuníquese con su Administrador del Sistema.".format(guia_remision_line.description))
            elif guia_remision_line.uom_id.code not in codigo_unidades_de_medida:
                errors.append("* La unidad de medida [{}] del producto [{}] no esta permitido. Comuníquese con su Administrador del Sistema.".format(
                    guia_remision_line.uom_id.code, guia_remision_line.description))

            if guia_remision_line.qty == 0:
                errors.append("La cantidad del producto [{}], debe ser mayor a 0".format(
                    guia_remision_line.description))

        return errors

    def convertir_a_borrador(self):
        for record in self:
            if record.estado_emision in ["A", "O"]:
                raise UserError(
                    "La Guía de remisión ya ha sido emitida y tiene estado de Aceptada.")
            if record.estado_emision in ["R"]:
                raise UserError(
                    "La Guía de remisión ya ha sido emitida y tiene estado de Rechazada.")
            record.estado_emision = "B"
            record.state = "borrador"
            record.numero = "Guía de Remisión Electrónica"

    def validar_transporte(self):
        errors = []
        if not self.modalidad_transporte:
            errors.append(
                "* La modalidad de transporte no ha sido seleccionado.")
        elif self.modalidad_transporte not in ["01", "02"]:
            errors.append(
                "* La modalidad de transporte seleccionado es incorrecto. Las modalidades de transporte permitidos son 01 - Transporte Público y 02 - Transporte Privado")

        if self.modalidad_transporte == "01":
            if not self.transporte_partner_id:
                errors.append(
                    "* Debe seleccionar una Empresa de Transporte público.")
            else:
                if not self.transporte_partner_id.name:
                    errors.append(
                        "* La empresa de transporte seleccionado no tiene Nombre o Razón Social.")
                elif len(self.transporte_partner_id.name) < 4:
                    errors.append(
                        "* El nombre de la empresa de transporte seleccionada debe tener como mínimo 4 carácteres.")

                if not self.transporte_partner_id.vat:
                    errors.append(
                        "* La empresa de transporte seleccionado no tiene documento.")
                elif not patron_ruc.match(self.transporte_partner_id.vat):
                    errors.append(
                        "* El RUC de la empresa de transporte seleccionada tiene un formato incorrecto.")

                if not self.transporte_partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code:
                    errors.append(
                        "* La empresa de transporte seleccionado no tiene tipo de documento.")
                elif not self.transporte_partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code == "6":
                    errors.append(
                        "* El tipo de documento de la empresa de transporte seleccionada debe ser de tipo 'RUC'")

                if not self.fecha_inicio_traslado:
                    errors.append(
                        "* La fecha de inicio de traslado es obligatorio.")
                """
                if not self.conductor_publico_id:
                    errors.append("* El Conductor público de la empresa es obligatorio.")
                elif not self.conductor_publico_id.tipo_documento:
                    errors.append("* El Conductor público seleccionado no tiene tipo de documento de identidad.")
                elif not self.conductor_publico_id.vat:
                    errors.append("* El Conductor público seleccionado no tiene número de documento de identidad.")
                """
        elif self.modalidad_transporte == "02":
            if not self.conductor_privado_partner_id:
                errors.append("* Debe seleccionar un conductor privado.")
            else:
                if not self.conductor_privado_partner_id.name:
                    errors.append(
                        "* El conductor privado seleccionado no tiene Nombre.")
                elif len(self.conductor_privado_partner_id.name) < 4:
                    errors.append(
                        "* El nombre del conductor privado seleccionado debe tener más de 4 carácteres")

                if not self.conductor_privado_partner_id.vat:
                    errors.append(
                        "* El conductor privado seleccionado no tiene documento.")
                if not self.conductor_privado_partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code:
                    errors.append(
                        "* La conductor privado seleccionado no tiene tipo de documento.")

                if not self.fecha_inicio_traslado:
                    errors.append(
                        "* La fecha de inicio de traslado es obligatorio")

            if not self.vehiculo_privado_id:
                errors.append("* El Vehículo privado es Obligatorio.")
            elif not self.vehiculo_privado_id.numero_placa:
                errors.append(
                    "* El Vehículo pivado seleccionado no tiene Número de Placa")

        return errors

    def generar_comprobante_json(self):
        if not self.name:
            serie = self.journal_id.code
            next_number = self.journal_id.sequence_number_next
            numero = serie + "-" + str(next_number).zfill(8)
            if self.estado_emision in ["A", "O"]:
                raise UserError(
                    "La Guía de Remisión ya ha sido emitida y tiene estado de Aceptada.")
            if self.estado_emision in ["R"]:
                raise UserError(
                    "La Guía de Remisión ya ha sido emitida y tiene estado de Rechazada.")
            if not next_number or not re.match('T\\w{3}-\\d{1,8}', str(numero)):
                raise UserError(
                    "El codigo no tiene el formato correcto: " + str(numero))
        else:
            numero = self.name
            if not re.match('T\\w{3}-\\d{1,8}', str(self.name)):
                raise UserError(
                    "El codigo no tiene el formato correcto: " + str(self.name))
            else:
                serie = self.name.split("-")[0]
                correlativo = self.name.split("-")[1]

        errors = []
        errors += self.validar_datos_compania()
        errors += self.validar_datos_destinatario()
        errors += self.validar_motivo_traslado()
        errors += self.validar_datos_envio()
        errors += self.validar_lugar_partida()
        errors += self.validar_lugar_llegada()
        errors += self.validar_guia_remision_lineas()
        errors += self.validar_transporte()

        if len(errors) > 0:
            return {
                'error': True,
                'name': 'ERROR: Validación de campos',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom.pop.message',
                'target': 'new',
                'context': {
                    'default_name': "Error al validar datos de la compania:",
                    'default_accion': '\n'.join(errors)
                }
            }
        serie, correlativo = numero.split('-')
        correlativo = int(correlativo)
        company = self.company_id.partner_id
        destinatario = self.destinatario_partner_id
        motivo_traslado_id = self.env["gestionit.motivo_traslado"].sudo().search(
            [('code', '=', self.motivo_traslado)])

        documento = {
            "serie": serie,
            "correlativo": correlativo,
            "nombreEmisor": company.name.strip(),
            "tipoDocEmisor": company.l10n_latam_identification_type_id.l10n_pe_vat_code,
            "numDocEmisor": company.vat,
            "tipoDocReceptor": destinatario.l10n_latam_identification_type_id.l10n_pe_vat_code,
            "numDocReceptor": destinatario.vat,
            "nombreReceptor": destinatario.name.strip(),
            "motivoTraslado": self.motivo_traslado,
            "descripcionMotivoTraslado": motivo_traslado_id.name.strip(),
            "transbordoProgramado": False,
            "pesoTotal": round(self.peso_bruto_total, 3),
            "pesoUnidadMedida": "KGM",
            "entregaUbigeo": self.lugar_llegada_ubigeo_code.code,
            "entregaDireccion": self.lugar_llegada_direccion.strip(),
            "salidaUbigeo": self.lugar_partida_ubigeo_code.code,
            "salidaDireccion": self.lugar_partida_direccion.strip(),
        }
        if self.numero_bultos > 0:
            documento.update({"numeroBulltosPallets": self.numero_bultos})

        detalle = []

        for guia_remision_line in self.guia_remision_line_ids:
            detalle.append(
                {
                    "cantidadItem": guia_remision_line.qty,
                    "nombreItem": guia_remision_line.description.strip(),
                    "unidadMedidaItem": guia_remision_line.uom_id.code,
                    "codItem": str(guia_remision_line.product_id.id)
                }
            )

        # Transporte Público
        transportes = []
        if self.modalidad_transporte == '01':
            transporte = {
                "numDocTransportista": self.transporte_partner_id.vat,
                "tipoDocTransportista": self.transporte_partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
                "fechaInicioTraslado": str(self.fecha_inicio_traslado),
                "nombreTransportista": self.transporte_partner_id.name.strip(),
                "modoTraslado": self.modalidad_transporte
            }
            if self.vehiculo_publico_id:
                if self.vehiculo_publico_id.numero_placa:
                    transporte.update(
                        {"placaVehiculo": self.vehiculo_publico_id.numero_placa})
            if self.conductor_publico_id:
                if self.conductor_publico_id.vat:
                    transporte.update(
                        {"numDocConductor": self.conductor_publico_id.vat})
                if self.conductor_publico_id.l10n_latam_identification_type_id.l10n_pe_vat_code:
                    transporte.update(
                        {"tipoDocConductor": self.conductor_publico_id.l10n_latam_identification_type_id.l10n_pe_vat_code})

            transportes.append(transporte)
        # Transporte Privado
        elif self.modalidad_transporte == "02":
            transportes.append({
                "numDocConductor": self.conductor_privado_partner_id.vat,
                "tipoDocConductor": self.conductor_privado_partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code,
                "fechaInicioTraslado": str(self.fecha_inicio_traslado),
                "placaVehiculo": self.vehiculo_privado_id.numero_placa,
                "modoTraslado": self.modalidad_transporte
            })

        nombreEmisor = self.company_id.partner_id.registration_name.strip()
        numDocEmisor = self.company_id.partner_id.vat.strip(
        ) if self.company_id.partner_id.vat else ""
        data = {
            "company": {
                "numDocEmisor": numDocEmisor,
                "nombreEmisor": nombreEmisor,
                "SUNAT_user": self.company_id.sunat_user,
                "SUNAT_pass": self.company_id.sunat_pass,
                "key_private": self.company_id.key_private,
                "key_public": self.company_id.key_public,
            },
            "tipoEnvio": int(self.company_id.tipo_envio),
            "tipoDocumento": "09",
            "transportes": transportes,
            "detalle": detalle,
            "documento": documento,
            "fechaEmision": str(self.fecha_emision)
        }
        return data

    def btn_validar_comprobante(self):
        if self.state == "validado":
            raise UserError("La Guía de remisión ya ha sido validada.")
        doc_json = self.generar_comprobante_json()
        if "error" in doc_json:
            return doc_json
        else:
            # _logger.info(doc_json)
            self.request_json = json.dumps(doc_json, indent=4)
        self.validar_comprobante()
        return self.enviar_comprobante()

    def validar_comprobante(self):
        if self.name == "" or self.name == False:
            serie = self.journal_id.code
            next_number = self.journal_id.sequence_number_next
            numero = serie + "-" + str(next_number).zfill(8)
            if len(self.env["gestionit.guia_remision"].search([("numero", "=", numero), ("state", '=', 'validado')])) > 0:
                raise UserError("El documento de guía de remisión ya existe.")
            self.state = "validado"
            self.numero = self.journal_id.sequence_id.next_by_id()
            self.name = self.numero
        else:
            if len(self.env["gestionit.guia_remision"].search([("numero", "=", self.name), ("state", '=', 'validado')])) > 0:
                raise UserError("El documento de guía de remisión ya existe.")
            self.numero = self.name
            self.state = "validado"

    # @api.multi
    def unlink(self):
        l = []
        for record in self:
            if record.state == "validado" or record.name:
                if record.name:
                    l.append(record.name)
                else:
                    l.append("Guía de Remisión Remitente "+str(record.id))

        if len(l) > 0:
            raise UserError(
                "No es posible eliminar una guía de remisión Validada o que tenga un número asignado. [{}]".format(",".join(l)))

        for record in self:
            result = super(GuiaRemision, record).unlink()

        return True

    def cron_enviar_comprobante(self, cantidad):
        guia_remision_ids = self.env["gestionit.guia_remision"].search(
            [("estado_emision", "in", ["P", False]), ("request_json", "!=", False)], limit=cantidad)
        for gr in guia_remision_ids:
            gr.btn_enviar_comprobante()
        return True

    def btn_enviar_comprobante(self):
        for record in self:
            if record.estado_emision in ["P", "B", False] and record.request_json:
                if len(self) == 1:
                    return record.enviar_comprobante()
                else:
                    record.enviar_comprobante()

    def enviar_comprobante(self):
        # pass

        # token = generate_token_by_company(self.company_id, 10000)
        # data = {
        #     "method": "EFact21.lamdba",
        #     "kwargs": {
        #         "data": json.loads(self.request_json)
        #     }
        # }
        # data = json.dumps(self.request_json, indent=4)
        data = json.loads(self.request_json)
        # headers = {
        #     "Content-Type": "application/json",
        #     "Authorization": token
        # }
        log_status = {
            "request_json": self.request_json,
            "guia_remision_id": self.id,
            "name": self.name,
            "date_request": fields.Datetime.now(),
            "date_issue": self.fecha_emision
        }
        try:
            # r = requests.post(self.company_id.endpoint,
            #                   headers=headers, data=data)
            r = api_models.lamdba(data)
            # _logger.info("R json")
            # _logger.info(r)
            # self.response_json = json.dumps(r.json(), indent=4)
            self.response_json = r
            log_status.update({
                "response_json": self.response_json,
            })
            if r:
                if "errors" not in r:
                    if "signed_xml" in r:
                        log_status.update(
                            {"signed_xml_data": r["signed_xml"]})
                    if "request_id" in r:
                        log_status.update(
                            {"api_request_id": r["request_id"]})
                    if "digest_value" in r:
                        self.digest_value = r["digest_value"]
                        log_status.update(
                            {"digest_value": r["digest_value"]})
                    if "response_xml" in r:
                        log_status.update(
                            {"response_xml": r["response_xml"]})
                    if "response_content_xml" in r:
                        log_status.update(
                            {"content_xml": r["response_content_xml"]})
                    if "sunat_status" in r:
                        self.estado_emision = r["sunat_status"]
                        log_status.update(
                            {"status": r["sunat_status"]})

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
                        'default_accion': "* La guía de remisión ha sido generada de forma exitosa.\n* El tiempo de espera de la respuesta ha sido excedida.\n* El comprobante se enviará de forma automática luego"

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
                        'default_accion': "* La guía de remisión ha sido generada de forma exitosa.\n* No se ha logrado enviar el comprobante.\n* Se intentará enviar luego de forma automática."
                }
            }
        except Exception as e:
            raise
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
                        'default_accion': "* La guía de remisión ha sido generada de forma exitosa.\n* "+str(e)
                }
            }
        finally:
            self.env["account.log.status"].sudo().create(log_status)

    def btn_view_log_guia_remision(self):
        return {
            'name': "Sunat Log - Guía de Remisión ",
            'type': "ir.actions.act_window",
            'view_mode': 'tree,form',
            'domain': [("guia_remision_id", "=", self.id)],
            'res_model': 'account.log.status',
            'target': 'self'
        }


class AccountInvoiceGuiaRemision(models.Model):
    _inherit = "account.move"

    def btn_crear_guia_remision(self):
        pass
