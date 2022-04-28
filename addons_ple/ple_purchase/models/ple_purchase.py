import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError

import logging
_logger=logging.getLogger(__name__)

options=[
	('in','esta en'),
	('not in','no esta en')
	]

class PlePurchase(models.Model):
	_name='ple.purchase'
	_inherit='ple.base'
	_description = "Modulo PLE Libros de Compras"

	ple_purchase_line_ids=fields.One2many('ple.purchase.line','ple_purchase_id',string="Registros de compra" ,readonly=True, states={'draft': [('readonly', False)]})
	ple_purchase_line_no_domiciliados_ids=fields.One2many('ple.purchase.line','ple_purchase_id_no_domiciliados',string="Registros de compra" , readonly=True, states={'draft': [('readonly', False)]})
	ple_purchase_line_recibo_honorarios_ids=fields.One2many('ple.purchase.line','ple_purchase_id_recibo_honorarios',string="Registros de compra" , readonly=True, states={'draft': [('readonly', False)]})
	
	identificador_operaciones = fields.Selection(selection=[('0','Cierre de operaciones'),('1','Empresa operativa'),('2','Cierre de libro')],
		string="Identificador de operaciones", required=True, default="1")
	identificador_libro = fields.Selection(selection='available_formats_purchase_sunat', string="Identificador de libro" )
	print_order = fields.Selection(default="date")

	######################### FILTROS DINAMICOS, NUEVOS CAMPOS AGREGADOS !!!
	partner_ids = fields.Many2many('res.partner','ple_purchase_partner_rel','partner_id','ple_purchase_id_1' ,string="Socio" ,readonly=True , states={'draft': [('readonly', False)]})
	journal_ids = fields.Many2many('account.journal','ple_purchase_journal_rel','journal_id','ple_purchase_id_3',string="Diario" ,readonly=True , states={'draft': [('readonly', False)]})
	move_ids = fields.Many2many('account.move','ple_purchase_move_rel','move_id','ple_purchase_id_4',string='Asiento Contable' ,readonly=True , states={'draft': [('readonly', False)]})
	currency_ids = fields.Many2many('res.currency','ple_purchase_currency_rel','currency_id','ple_purchase_id_6', string="Moneda" ,readonly=True , states={'draft': [('readonly', False)]})
	##################################################################################
	partner_option=fields.Selection(selection=options , string="",readonly=True , states={'draft': [('readonly', False)]})
	journal_option=fields.Selection(selection=options , string="",readonly=True , states={'draft': [('readonly', False)]})
	move_option=fields.Selection(selection=options , string="",readonly=True , states={'draft': [('readonly', False)]})
	currency_option=fields.Selection(selection=options , string="",readonly=True , states={'draft': [('readonly', False)]})

	########################################################
	## CAMPO PARA IMPRIMIR RECIBO POR HONORARIOS EN LOS REPORTES DE DOMICILIADOS
	imprimir_recibo_honorarios=fields.Boolean(string="Incluir Recibos por Honorarios", default=False)

	fecha=fields.Boolean(string="Fecha" ,readonly=True , states={'draft': [('readonly', False)]})
	periodo=fields.Boolean(string="Periodo" ,readonly=True , states={'draft': [('readonly', False)]})

	date_from=fields.Date(string="Desde:" ,readonly=True , states={'draft': [('readonly', False)]})
	date_to=fields.Date(string="Hasta:" ,readonly=True , states={'draft': [('readonly', False)]})

	fecha_inicio=''
	fecha_fin=''
	############## CHECK para indicar si se incluye o no registros anteriores no declarados
	
	incluir_anteriores_no_declarados = fields.Boolean(string="Incluir registros anteriores no declarados", default=False)

	######################################
	def button_view_tree_domiciliados(self):
		self.ensure_one()
		view = self.env.ref('ple_purchase.view_ple_purchase_domiciliados_line_tree')
		if self.ple_purchase_line_ids:
			diccionario = {
				'name': 'Libro PLE Compras Domiciliadas',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'ple.purchase.line',
				'view_id': view.id,
				'views': [(view.id,'tree')],
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [i.id for i in self.ple_purchase_line_ids] or [])],
				'context':{
					'search_default_filter_proveedor':1,
					'search_default_filter_tipo_comprobante':1,
					}
			}
			return diccionario
	###########################################
	def button_view_tree_no_domiciliados(self):
		self.ensure_one()
		view = self.env.ref('ple_purchase.view_ple_purchase_no_domiciliados_line_tree')
		if self.ple_purchase_line_ids:
			diccionario = {
				'name': 'Libro PLE Compras No Domiciliadas',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'ple.purchase.line',
				'view_id': view.id,
				'views': [(view.id,'tree')],
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [i.id for i in self.ple_purchase_line_no_domiciliados_ids] or [])],
				'context':{
					'search_default_filter_proveedor':1,
					'search_default_filter_tipo_comprobante':1,
					}
			}
			return diccionario
	#############################################
	def button_view_tree_recibo_honorarios(self):
		self.ensure_one()
		view = self.env.ref('ple_purchase.view_ple_purchase_domiciliados_line_tree')
		if self.ple_purchase_line_ids:
			diccionario = {
				'name': 'Libro PLE Compras Recibo Honorarios',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'ple.purchase.line',
				'view_id': view.id,
				'views': [(view.id,'tree')],
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [i.id for i in self.ple_purchase_line_recibo_honorarios_ids] or [])],
				'context':{
					'search_default_filter_proveedor':1,
					'search_default_filter_tipo_comprobante':1,
					}
			}
			return diccionario

			
	@api.onchange('fecha')
	def onchange_fecha(self):
		for rec in self:
			if rec.fecha:
				rec.periodo=False

	@api.onchange('periodo')
	def onchange_periodo(self):
		for rec in self:
			if rec.periodo:
				rec.fecha=False

	#######################################
	def unlink (self):
		for line in self:
			for line2 in line.ple_purchase_line_ids + line.ple_purchase_line_no_domiciliados_ids + line.ple_purchase_line_recibo_honorarios_ids:
				line2.move_id.write({'declared_ple_8_1_8_2':False})
			return super(PlePurchase, line2).unlink()

	
	def available_formats_purchase_sunat(self):
		formats=[('080100','Domiciliado'),
			('080200','No domiciliado')
			]
		return formats

	
	def criterios_impresion(self):
		res = super(PlePurchase, self).criterios_impresion() or []
		res += [('name',u'N° de documento')]#,('table10_id','Tipo de documento')]
		return res


	def _action_confirm_ple(self):
		array_id=[]
		for line in self.ple_purchase_line_ids + self.ple_purchase_line_no_domiciliados_ids + self.ple_purchase_line_recibo_honorarios_ids:
			array_id.append(line.move_id.id)
		# self.env['account.move'].browse(array_id).write({'declared_ple':True})
		super(PlePurchase , self)._action_confirm_ple('account.move' , array_id ,{'declared_ple_8_1_8_2':True})

	
	def _get_datas(self, domain):
		orden =''
		if self.print_order == 'date':
			orden = "invoice_date asc"		
		elif self.print_order == 'invoice_number':
			orden = "name asc"
		return self._get_query_datas('account.move', domain, orden)


	def _get_order_print(self , object):
		total =''
		if self.print_order == 'date':
			total=sorted(object, key=lambda PlePurchaseLine: PlePurchaseLine.fecha_emision_comprobante)
		elif self.print_order == 'invoice_number':
			total=sorted(object , key=lambda PlePurchaseLine: PlePurchaseLine.numero_comprobante)
		return total


	def _get_domain(self):
		#####################
		if self.fecha:
			self.fecha_inicio=self.date_from
			self.fecha_fin=self.date_to

		elif self.periodo:
			if self.incluir_anteriores_no_declarados:
				self.fecha_inicio= "%s-01-01" %(self.fiscal_year)
				self.fecha_fin= self._get_end_date()
			else:
				self.fecha_inicio= self._get_star_date()
				self.fecha_fin= self._get_end_date()
		#####################

		'''if self.fecha:
			self.fecha_inicio=self.date_from
			self.fecha_fin=self.date_to
		elif self.periodo:
			self.fecha_inicio= self._get_star_date()
			self.fecha_fin= self._get_end_date()'''

		domain = [
			('date','>=',self.fecha_inicio),
			('date','<=',self.fecha_fin),
			('type','in',['in_invoice','in_refund']),
			('state','in',['posted'])
			]


		partners=list(self.partner_ids.mapped('id'))
		len_partners = len(partners or '')
		if len_partners:
			domain.append(('partner_id.id' , self.partner_option or 'in', partners))

		journals = list(self.journal_ids.mapped('id'))
		len_journals = len(journals or '')
		if len(self.journal_ids):
			domain.append(('journal_id.id' , self.journal_option or 'in', journals))

		moves = list(self.move_ids.mapped('id'))
		len_moves = len(moves or '')
		if len(moves):
			domain.append(('id' ,self.move_option or 'in', moves))

		currencys = list(self.currency_ids.mapped('id'))
		len_currencys = len(currencys or '')
		if len(currencys):
			domain.append(('currency_id.id' ,self.currency_option or 'in', currencys))

			
		return domain

	def file_name(self, file_format):
		if(self.identificador_libro == '080100'):
			nro_de_registros = '1' if len(self.ple_purchase_line_ids)>0 else '0'
		else:
			nro_de_registros = '1' if len(self.ple_purchase_line_no_domiciliados_ids)>0 else '0'

		file_name = "LE%s%s%s00%s%s%s1.%s" % (self.company_id.vat, self._periodo_fiscal(),
								 self.identificador_libro, self.identificador_operaciones, nro_de_registros,
								self.currency_id.code_ple or '1', file_format)
		return file_name

	def _periodo_fiscal(self):
		periodo = "%s%s00" % (self.fiscal_year or 'YYYY', self.fiscal_month or 'MM')
		return periodo

	#####################
	def type_document_parent(self,invoice):
		parent_type=''
		if invoice.reversed_entry_id:
			parent_type= invoice.reversed_entry_id.journal_id.invoice_type_code_id or ''
		return parent_type



	def generar_libro(self):

		registro=[]
		registro_no_domiciliados=[]
		registro_recibo_honorarios=[]

		self.state='open'
		self.ple_purchase_line_ids.unlink()
		self.ple_purchase_line_no_domiciliados_ids.unlink()
		self.ple_purchase_line_recibo_honorarios_ids.unlink()
		
		####################################################
		for line in self._get_datas(self._get_domain()):

			if (str(line.journal_id.invoice_type_code_id or '').strip() in ['02']) or (self.type_document_parent(line) in ['02']):
				registro_recibo_honorarios.append((0,0,{'move_id':line.id}))
			else:
				#str(line.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '').strip() not in  ['0']
				if str(line.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '').strip() not in  ['0'] and\
					(str(line.journal_id.invoice_type_code_id or '').strip() not in ['91','97','98']):
					registro.append((0,0,{'move_id':line.id}))

				elif str(line.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '').strip() in ['0'] and\
					(str(line.journal_id.invoice_type_code_id or '').strip() not in ['00','91','97','98']):
					registro_no_domiciliados.append((0,0,{'move_id':line.id}))
		#####################################################

		self.ple_purchase_line_ids = registro
		self.ple_purchase_line_no_domiciliados_ids=registro_no_domiciliados
		self.ple_purchase_line_recibo_honorarios_ids=registro_recibo_honorarios


	def _init_buffer(self, output):
		# output parametro de buffer que ingresa vacio
		if self.print_format == 'xlsx':
			self._generate_xlsx(output)
		elif self.print_format == 'txt':
			if self.identificador_libro == '080100':
				self._generate_txt(output)
			elif self.identificador_libro == '080200':
				self._generate_txt_no_domiciliados(output)

		return output




	def _convert_object_date(self, date):
		# parametro date que retorna un valor vacio o el formato 01/01/2100 dia/mes/año
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''

	##########################################################################
	def _generate_txt_no_domiciliados(self, output):
		for line in self._get_order_print(self.ple_purchase_line_no_domiciliados_ids) :
			escritura="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n" % (
				self._periodo_fiscal() ,
				line.asiento_contable,
				line.no_domiciliado_m_correlativo_asiento_contable,
				self._convert_object_date(line.fecha_emision_comprobante),
				line.tipo_comprobante or '',
				line.serie_comprobante or '',
				line.numero_comprobante or '',
				format(line.no_domiciliado_valor_adquisiciones,".2f"),
				format(line.no_domiciliado_otros_conceptos_adicionales,".2f"),
				format(line.importe_adquisiciones_registradas,".2f"),
				line.no_domiciliado_tipo_comprobante_credito_fiscal or '',
				line.no_domiciliado_serie_comprobante_credito_fiscal or '',
				line.anio_emision_DUA or '',
				line.no_domiciliado_numero_comprobante_pago_impuesto or '',
				format(line.monto_igv_1,".2f"),
				line.codigo_moneda,
				format(line.tipo_cambio,".3f"),
				line.no_domiciliado_pais_residencia or '',
				line.razon_social or '',
				line.no_domiciliado_domicilio or '',
				line.no_domiciliado_numero_identificacion or '',
				line.no_domiciliado_identificacion_beneficiario or '',
				line.no_domiciliado_razon_social_beneficiario or '',
				line.no_domiciliado_pais_beneficiario or '',
				line.no_domiciliado_vinculo_entre_contribuyente_residente or '',
				format(line.no_domiciliado_renta_bruta,".2f"),
				format(line.no_domiciliado_deduccion_bienes,".2f"),
				format(line.no_domiciliado_renta_neta,".2f"),
				format(line.no_domiciliado_tasa_retencion,".2f"),
				format(line.no_domiciliado_impuesto_retenido,".2f"),
				line.no_domiciliado_convenios or '',
				line.no_domiciliado_exoneracion or '',
				line.no_domiciliado_tipo_renta or '',
				line.no_domiciliado_modalidad_servicio_prestado or '',
				line.no_domiciliado_aplicacion_ley_impuesto_renta or '',
				line.no_domiciliado_oportunidad_anotacion or '') 

			output.write(escritura.encode())

	#######################################################################
	def _generate_txt(self, output):
		for line in self._get_order_print(self.ple_purchase_line_ids) :
			###########################################################
			escritura="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n" % (
				self._periodo_fiscal() ,
				line.asiento_contable,
				line.m_correlativo_asiento_contable,
				self._convert_object_date(line.fecha_emision_comprobante),
				self._convert_object_date(line.fecha_vencimiento),
				line.tipo_comprobante,
				line.serie_comprobante,
				line.anio_emision_DUA or '',
				line.numero_comprobante or '',
				line.operaciones_sin_igv or '',
				line.tipo_documento_proveedor or '',
				line.ruc_dni or '',
				line.razon_social or '',
				format(line.base_imponible_igv_gravadas,".2f"),
				format(line.monto_igv_1,".2f"),
				format(line.base_imponible_igv_no_gravadas,".2f"),
				format(line.monto_igv_2,".2f"),
				format(line.base_imponible_no_igv,".2f"),
				format(line.monto_igv_3,".2f"),
				format(line.valor_no_gravadas,".2f"),
				format(line.isc,".2f"),
				format(line.impuesto_consumo_bolsas_plastico,".2f"),
				format(line.otros_impuestos,".2f"),
				format(line.importe_adquisiciones_registradas,".2f"),
				line.codigo_moneda,
				format(line.tipo_cambio , '.3f'),
				self._convert_object_date(line.fecha_emision_original),
				line.tipo_comprobante_original or '',
				line.serie_comprobante_original or '',
				line.codigo_dep_aduanera or '',
				line.numero_comprobante_original or '',
				self._convert_object_date(line.fecha_detraccion),
				line.numero_detraccion or '',
				line.marca_retencion or '',
				line.clasificacion_bienes or '',
				line.identificacion_contrato or '',
				line.error_1 or '',
				line.error_2 or '',
				line.error_3 or '',
				line.error_4 or '',
				line.indicador_comprobantes or '',
				line.oportunidad_anotacion or '' )
			output.write(escritura.encode())
			####################################################################

	def _generate_xlsx(self, output):
		workbook = xlsxwriter.Workbook(output)
		ws = workbook.add_worksheet('Reporte de Compras')

		titulo1 = workbook.add_format({'font_size': 16, 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo_1 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		# titulo2 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'left':True, 'right':True,'bottom': True, 'top': True, 'bold':True , 'font_name':'Arial'})
		titulo2 = workbook.add_format({'font_size': 8, 'align': 'center','valign': 'vcenter','color':'black', 'text_wrap': True, 'left':True, 'right':True,'bottom': True, 'top': True, 'bold':True , 'font_name':'Arial'})
		#######################################################
		titulo_2 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		
		##################################################################
		titulo5 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap':True, 'font_name':'Arial', 'bold':True})

		titulo6 = workbook.add_format({'font_size': 8, 'align': 'right', 'text_wrap': True, 'top': True, 'bold':True , 'font_name':'Arial'})
		# titulo7 = workbook.add_format({'font_size': 8, 'align': 'rightprinter_xls', 'text_wrap': True, 'left':True, 'right':True,'bottom': True, 'top': True, 'bold':True , 'font_name':'Arial'})

		number_left = workbook.add_format({'font_size': 8, 'align': 'left', 'num_format': '#,##0.00', 'font_name':'Calibri'})
		number_right = workbook.add_format({'font_size': 8, 'align': 'right', 'num_format': '#,##0.00', 'font_name':'Calibri'})
		number_left = workbook.add_format({'font_size': 8, 'align': 'left', 'num_format': '#,##0.00', 'font_name':'Arial'})
		number_right = workbook.add_format({'font_size': 8, 'align': 'right', 'num_format': '#,##0.00', 'font_name':'Arial'})
		number_right_tax_rate = workbook.add_format({'font_size': 8, 'align': 'right', 'num_format': '#,##0.000', 'font_name':'Arial'})
		
		letter1 = workbook.add_format({'font_size': 7, 'align': 'left', 'font_name':'Arial'})
		letter3 = workbook.add_format({'font_size': 7, 'align': 'right','num_format': '#,##0.00', 'font_name':'Arial'})
		letter3_negrita = workbook.add_format({'font_size': 7, 'align': 'right','num_format': '#,##0.00', 'font_name':'Arial','bold': True})

		ws.set_column('A:A', 20.29,letter1)
		ws.set_column('B:B', 20.14,letter1)
		ws.set_column('C:C', 20.71,letter1)
		ws.set_column('D:D', 9.43,letter1)
		ws.set_column('E:E', 9.29,letter1)
		ws.set_column('F:F', 9.29,letter1)
		ws.set_column('G:G', 20.14,letter1)
		ws.set_column('H:H', 8.43,letter1)
		ws.set_column('I:I', 20.71,letter1)
		ws.set_column('J:J', 20.14,letter1)
		ws.set_column('K:K', 8.43,number_right)
		ws.set_column('L:L', 8,number_right)
		ws.set_column('M:M', 11.29,number_right)
		ws.set_column('N:N', 26.86,number_right)
		ws.set_column('O:O',10.43 ,number_right)
		ws.set_column('P:P', 10.14,number_right)
		ws.set_column('Q:Q', 10,number_right)
		
		ws.set_column('R:R', 10.86,number_right)
		ws.set_column('S:S', 10.71,number_right)
		ws.set_column('T:T', 10.86,number_right)
		ws.set_column('U:U', 10.56,letter1)
		ws.set_column('V:V', 10.86,letter1)
		ws.set_column('W:W', 10.86,letter1)
		ws.set_column('X:X', 10.43,number_right_tax_rate)
		ws.set_column('Y:Y', 10.29,letter1)
		ws.set_column('Z:Z', 10.29,letter1)
		ws.set_column('AA:AA',8.81 ,letter1)
		ws.set_column('AB:AB', 10.71,letter1)
		ws.set_column('AC:AC', 10.71,letter1)
		ws.set_column('AD:AD', 10.71,letter1)
		ws.set_column('AE:AE',7.71 ,letter1)

		#titulo2.set_pattern(1)  # This is optional when using a solid fill.
		ws.merge_range('A1:I1','FORMATO 8.1: REGISTRO DE COMPRAS',titulo1)
		
		ws.merge_range('A7:A13','NÚMERO CORRELATIVO DEL REGISTRO O CÓDIGO ÚNICO DE LA OPERACIÓN', titulo2)

		#titulo2.set_pattern(1)  # This is optional when using a solid fill.
	
		ws.merge_range('B7:B13','FECHA DE EMISIÓN DEL COMPROBANTE DE PAGO O DOCUMENTO', titulo2)
		ws.merge_range('C7:C13','FECHA DE VENCIMIENTO O FECHA D PAGO(1)', titulo2)

		
		#titulo2.set_pattern(1)  # This is optional when using a solid fill.
		
		ws.merge_range('D7:F8','COMPROBANTES DE PAGO O DOCUMENTO', titulo2)

		ws.merge_range('D9:D13','TIPO (TABLA 10)', titulo2)
		ws.merge_range('E9:E13','SERIE O CÓDIGO DE LA DEPENDENCIA ADUANERA', titulo2)
		ws.merge_range('F9:F13','AÑO DE EMISIÓN DE LA DUA O DSI', titulo2)

		ws.merge_range('G7:G13','NRO DE COMPROBANTE DE PAGO, DOCUMENTO,NRO DE ORDEN DEL FORMULARIO FÍSICO O VIRTUAL, NRO DE DUA,DSI O LIQUIDACIÓN DE COBRANZA U OTROS DOCUMENTOS EMITIDOS POR SUNAT PARA ACREDITAR EL CRÉDITO FISCAL EN LA IMPORTACIÓN', titulo2)
		ws.merge_range('H7:J8','INFORMACIÓN DEL PROVEEDOR', titulo2)
		ws.merge_range('H9:I9','DOCUMENTO DE IDENTIDAD', titulo2)
		ws.merge_range('H10:H13','TIPO (TABLA 2)', titulo2)
		ws.merge_range('I10:I13','NÚMERO', titulo2)
		ws.merge_range('J9:J13','APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL', titulo2)
		#######################################
		ws.merge_range('K7:L8','ADQUISIONES GRAVADAS DESTINADAS A OPERACIONES GRAVADAS Y/O DE EXPORTACIÓN', titulo2)
		ws.merge_range('K9:K13','BASE IMPONIBLE', titulo2)
		ws.merge_range('L9:L13','IGV', titulo2)

		#######################################
		ws.merge_range('M7:N8','ADQUISICIONES GRAVADAS DESTINADAS A OPERACIONES GRAVADAS Y/O DE EXPORTACIÓN Y A EXPORTACIONES NO GRAVADAS', titulo2)
		ws.merge_range('M9:M13','BASE IMPONIBLE', titulo2)		
		ws.merge_range('N9:N13','IGV', titulo2)
		#############################################

		ws.merge_range('O7:P8','ADQUISICIONES GRAVADAS DESTINADAS A OPERACIONES NO GRAVADAS', titulo2)
		ws.merge_range('O9:O13','BASE IMPONIBLE', titulo2)
		ws.merge_range('P9:P13','IGV', titulo2)

		#titulo2.set_pattern(1)  # This is optional when using a solid fill.
		
		ws.merge_range('Q7:Q13','VALOR DE LAS ADQUISICIONES NO GRAVADAS', titulo2)
		ws.merge_range('R7:R13','ISC', titulo2)
		ws.merge_range('S7:S13','OTROS TRIBUTOS Y CARGOS', titulo2)
		ws.merge_range('T7:T13','IMPORTE TOTAL', titulo2)
		ws.merge_range('U7:U13','NRO DE COMPROBANTE DE PAGO EMITIDO POR SUJETO NO DOMICILIADO (2)', titulo2)
		###########################################################

		ws.merge_range('V7:W8','CONSTANCIA DE DEPÓSITO DE DETRACCIÓN (3)', titulo2)
		ws.merge_range('V9:V13','NÚMERO', titulo2)
		ws.merge_range('W9:W13','FECHA DE EMISIÓN', titulo2)

		ws.merge_range('X7:X13','TIPO DE CAMBIO', titulo2)
		#############################################################
		ws.merge_range('Y7:AB8','REFERENCIA DEL COMPROBANTE DE PAGO O DOCUMENTO ORIGINAL QUE SE MODIFICA', titulo2)
		ws.merge_range('Y9:Y13','FECHA', titulo2)
		ws.merge_range('Z9:Z13','TIPO (TABLA 10)', titulo2)
		ws.merge_range('AA9:AA13','SERIE', titulo2)
		ws.merge_range('AB9:AB13','NRO DEL COMPROBANTE DE PAGO O DOCUMENTO', titulo2)

		ws.write(2,0,'PERIODO:',titulo_1)
		ws.write(3,0,'RUC:',titulo_1)
		ws.merge_range('A5:C5','APELLIDO Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL:',titulo_1)
		ws.write(3,1,self.company_id.vat ,titulo_2)

		ws.write(2,1,self._periodo_fiscal() ,titulo_2)
		################################### DENOMINACION O RAZON SOCIAL
		ws.merge_range('D5:G5',self.company_id.name ,titulo_2)
		
		ws.freeze_panes(13,0)

		fila=12
		total=[0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ]
		#####################
		records_xlsx=[]
		if self.imprimir_recibo_honorarios:
			records_xlsx = self._get_order_print(self.ple_purchase_line_ids + self.ple_purchase_line_no_domiciliados_ids + self.ple_purchase_line_recibo_honorarios_ids)
		else:
			records_xlsx = self._get_order_print(self.ple_purchase_line_ids + self.ple_purchase_line_no_domiciliados_ids)
		#####################
		for line in records_xlsx :
		# for line in self.ple_purchase_line_ids + self.ple_purchase_line_no_domiciliados_ids:
			fila+=1

			ws.write(fila,0, line.asiento_contable)
			ws.write(fila,1,self._convert_object_date(line.fecha_emision_comprobante) or '' )
			
			# if not isinstance(line.date_due,type(None)):
			ws.write(fila,2,self._convert_object_date(line.fecha_vencimiento) or '' )
	
			ws.write(fila,3, line.tipo_comprobante or '')
			###SERIE O CODIGO DE LA DEPENDENCIA ADUANERA (FALTA !!)
			ws.write(fila,4,line.serie_comprobante or '')


			ws.write(fila,5,int(line.anio_emision_DUA) or '')


			ws.write(fila,6,line.numero_comprobante or '')
			ws.write(fila,7,line.tipo_documento_proveedor or '')
			###NUMERO DE DOCUMENTO
			ws.write(fila,8,line.ruc_dni or '')

			#######APELLIDOS Y NOMBRES O RAZON SOCIAL
			ws.write(fila,9, line.razon_social or '')

			#######BASE IMPONIBLE
			ws.write(fila,10,line.base_imponible_igv_gravadas )
			total[0] = total[0] + line.base_imponible_igv_gravadas
			###################IGV
			ws.write(fila,11,line.monto_igv_1 )
			total[1] = total[1] + line.monto_igv_1 
			
			ws.write(fila,12,0 )
			ws.write(fila,13,0 )
			ws.write(fila,14,0 )
			ws.write(fila,15,0)
			#### AQUI VA EL VALOR DE LAS ADQUISIONES NO GRAVADAS !!! ESTE CAMPO DEPENDE DE 
			ws.write(fila,16,line.valor_no_gravadas)
			total[6]= total[6] + line.valor_no_gravadas

			ws.write(fila,17,0)
			ws.write(fila,18,line.otros_impuestos)
			total[8]= total[8] + line.otros_impuestos

			######################IMPORTE TOTAL
			ws.write(fila,19,line.importe_adquisiciones_registradas)
			total[9]= total[9] + line.importe_adquisiciones_registradas
			######################FALTA DETRACCION
			ws.write(fila,21,line.numero_detraccion or '')

			#######################CONSTANCIA DE DETRACCION -- FECHA EMISIÓN
			if len(str(line.fecha_detraccion or '') )!=0 :
				ws.write(fila,22,self._convert_object_date(line.fecha_detraccion) or '')

			###################TIPO DE CAMBIO
			# el formato tiene que ser en la celdas y no alterar el dato
			ws.write(fila,23,line.tipo_cambio)
			
			###################REFERENCIA DEL COMPROBANTE / TIPO (TABLA 10)
			ws.write(fila,24,line.fecha_emision_original or '' )
			ws.write(fila,25,line.tipo_comprobante_original or '')
			ws.write(fila,26,line.serie_comprobante_original or '')
			ws.write(fila,27,line.numero_comprobante_original or '')
			
	
			############ESCRIBIENDO TOTALES !!!!!!

		fila = fila + 1
		ws.write(fila,9,'TOTALES :',letter3_negrita)
		ws.write(fila,10,total[0],letter3_negrita)
		ws.write(fila,11,total[1],letter3_negrita)
		ws.write(fila,12,total[2],letter3_negrita)		
		ws.write(fila,13,total[3],letter3_negrita)
		ws.write(fila,14,total[4],letter3_negrita)
		ws.write(fila,15,total[5],letter3_negrita)
		ws.write(fila,16,total[6],letter3_negrita)
		ws.write(fila,17,total[7],letter3_negrita)
		ws.write(fila,18,total[8],letter3_negrita)
		ws.write(fila,19,total[9],letter3_negrita)
		workbook.close()




