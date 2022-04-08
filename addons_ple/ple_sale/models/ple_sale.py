import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError

import logging
_logger=logging.getLogger(__name__)

options = [('in','Esta en'),('not in','No esta en')]

class PleSale(models.Model):
	_name='ple.sale'
	_inherit='ple.base'
	_description = "Modulo PLE Libros de Ventas"

	ple_sale_line_ids=fields.One2many('ple.sale.line','ple_sale_id',string="Registros de venta")

	identificador_operaciones = fields.Selection(selection=[('0','Cierre de operaciones'),('1','Empresa operativa'),('2','Cierre de libro')],
		string="Identificador de operaciones",required=True,default="1")
	identificador_libro=fields.Selection(selection='available_formats_sale_sunat', string="Identificador del Libro")
	

	partner_ids = fields.Many2many('res.partner','ple_sale_partner_rel','partner_id','ple_sale_id_1' ,string="Socio" ,readonly=True , states={'draft': [('readonly', False)]})
	account_ids = fields.Many2many('account.account','ple_sale_account_rel','account_id','ple_sale_id_2',string='Cuenta',domain="[('internal_type', '=', 'receivable'),('deprecated','=',False)]" ,readonly=True , states={'draft': [('readonly', False)]})
	journal_ids = fields.Many2many('account.journal','ple_sale_journal_rel','journal_id','ple_sale_id_3',string="Diario" ,readonly=True , states={'draft': [('readonly', False)]})
	move_ids = fields.Many2many('account.move','ple_sale_move_rel','move_id','ple_sale_id_4',string='Factura' ,readonly=True , states={'draft': [('readonly', False)]})
	currency_ids = fields.Many2many('res.currency','ple_sale_currency_rel','currency_id','ple_sale_id_6', string="Moneda" ,readonly=True , states={'draft': [('readonly', False)]})

	####### Select Option Filter
	partner_option=fields.Selection(selection=options , string="",readonly=True , states={'draft': [('readonly', False)]})
	account_option=fields.Selection(selection=options , string="",readonly=True , states={'draft': [('readonly', False)]})
	journal_option=fields.Selection(selection=options , string="",readonly=True , states={'draft': [('readonly', False)]})
	move_option=fields.Selection(selection=options , string="",readonly=True , states={'draft': [('readonly', False)]})
	currency_option=fields.Selection(selection=options , string="",readonly=True , states={'draft': [('readonly', False)]})
	#######################

	fecha=fields.Boolean(string="Fecha" ,readonly=True , states={'draft': [('readonly', False)]})
	periodo=fields.Boolean(string="Periodo" ,readonly=True , states={'draft': [('readonly', False)]})

	date_from=fields.Date(string="Desde:" ,readonly=True , states={'draft': [('readonly', False)]})
	date_to=fields.Date(string="Hasta:" ,readonly=True , states={'draft': [('readonly', False)]})

	fecha_inicio=''
	fecha_fin=''

	############## CHECK para indicar si se incluye o no registros anteriores no declarados
	
	incluir_anteriores_no_declarados = fields.Boolean(string="Incluir registros anteriores no declarados", default=False)

	###############################
	_sql_constraints = [
		('fiscal_month', 'unique(fiscal_month,fiscal_year,company_id)',  'Este periodo para el PLE ya existe , revise sus registros de PLE creados!!!'),
	]

	######################################
	def button_view_tree_ple_sale_lines(self):
		self.ensure_one()
		view = self.env.ref('ple_sale.view_ple_sale_line_tree')
		if self.ple_sale_line_ids:
			diccionario = {
				'name': 'Libro PLE Ventas',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'ple.sale.line',
				'view_id': view.id,
				'views': [(view.id,'tree')],
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [i.id for i in self.ple_sale_line_ids] or [])],
				'context':{
					'search_default_filter_cliente':1,
					'search_default_filter_tipo_comprobante':1,
					}
			}
			return diccionario
	###########################################


	def name_get(self):
		result = []
		for ple in self:
			if ple.periodo:
				result.append((ple.id, ple._periodo_fiscal() or 'New'))
			elif ple.fecha:
				result.append((ple.id,"%s-%s"%(self._convert_object_date(ple.date_from),self._convert_object_date(ple.date_to)) or 'New'))
			else:
				result.append((ple.id,'New'))
		return result

	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		if self.periodo:
			recs = self.search([('fiscal_month', operator, name),('fiscal_year', operator, name)] + args, limit=limit)
		elif self.fecha:
			recs = self.search([('date_from', operator, name),('date_to', operator, name)] + args, limit=limit)
		return recs.name_get()
	###############################################

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

	def unlink (self):
		for line in self:
			for line2 in line.ple_sale_line_ids:
				line2.invoice_id.write({'declared_ple':False})
			return super(PleSale, line).unlink()



	def action_print(self):
		if ( self.print_format and self.identificador_libro and self.identificador_operaciones) :
			if self.print_format == 'pdf' :
				return self.env.ref('ple_sale.report_custom_a4').with_context(discard_logo_check=True).report_action(self)
			else:
				return super(PleSale , self).action_print()
		else:
			raise UserError(_('NO SE PUEDE IMPRIMIR , Los campos: Formato Impresión , Identificador de operaciones y Identificador de libro son obligatorios, llene esos campos !!!'))


	def available_formats_sale_sunat(self):
		formats=[('140100','Registros de Ventas e Ingresos')
			]
		return formats
	
	def criterios_impresion(self):
		res = super(PleSale, self).criterios_impresion() or []
		res += [('invoice_number',u'N° de documento'),('num_serie',u'N° de serie'),('table10_id','Tipo de documento')]
		return res


	def _action_confirm_ple(self):
		array_id=[]
		for line in self.ple_sale_line_ids :
			array_id.append(line.invoice_id.id)
		super(PleSale ,self)._action_confirm_ple('account.move' ,array_id,{'declared_ple':True})

	def _get_datas(self, domain):
		# orden= []

		return self._get_query_datas('account.move', domain, "invoice_date asc , name asc")


	##############################################
	def _get_domain(self):
		#####################
		if self.fecha:
			if self.incluir_anteriores_no_declarados:
				self.fecha_inicio="%s-01-01" %(self.fiscal_year)
				self.fecha_fin=self.date_to
			else:
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

		domain = [
			('date','>=',self.fecha_inicio),
			('date','<=',self.fecha_fin),
			('type','in',['out_invoice','out_refund']),
			('state','not in',['draft'])
			]


		partners=tuple(self.partner_ids.mapped('id'))
		len_partners = len(partners or '')
		if len_partners:
			domain.append(('partner_id.id' , self.partner_option or 'in', partners))

		journals = tuple(self.journal_ids.mapped('id'))
		len_journals = len(journals or '')
		if len(self.journal_ids):
			domain.append(('journal_id.id' ,self.journal_option or 'in', journals))

		moves = tuple(self.move_ids.mapped('id'))
		len_moves = len(moves or '')
		if len(moves):
			domain.append(('id' ,self.move_option or 'in', moves))

		currencys = tuple(self.currency_ids.mapped('id'))
		len_currencys = len(currencys or '')
		if len(currencys):
			domain.append(('currency_id.id' ,self.currency_option or 'in', currencys))


		accounts = tuple(self.account_ids.mapped('id'))
		len_accounts = len(accounts or '')
		if len(accounts):
			domain.append(('account_id.id' ,self.account_option or 'in', accounts))
			
		return domain


	def file_name(self, file_format):
		
		nro_de_registros = '1' if len(self.ple_sale_line_ids)>0 else '0' 

		if self.periodo:
			file_name = "LE%s%s%s00%s%s%s1.%s" % (self.company_id.vat, self._periodo_fiscal(),
									self.identificador_libro, self.identificador_operaciones, nro_de_registros,
									self.currency_id.code_ple or '1', file_format)
		elif self.fecha:
			file_name = "LE%s%s%s00%s%s%s1.%s" % (self.company_id.vat, "%s00" %(self.date_to.strftime('%Y%m')),
									self.identificador_libro, self.identificador_operaciones, nro_de_registros,
									self.currency_id.code_ple or '1', file_format)

		return file_name


	def generar_libro(self):
		registro=[]
		
		self.state='open'
		self.ple_sale_line_ids.unlink()
		for line in self._get_datas(self._get_domain()):
			#if ((line.prefix_code and line.invoice_number) or line.document_id):
			registro.append((0,0,{'invoice_id':line.id}))
		self.ple_sale_line_ids = registro

	def _init_buffer(self, output):
		if self.print_format == 'xlsx':
			self._generate_xlsx(output)
		elif self.print_format == 'txt':
			self._generate_txt(output)
		return output


	###############################
	def _generate_txt(self, output):
		# for line in self._get_order_print(self.ple_sale_line_ids):
		for line in self.ple_sale_line_ids:
			escritura="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n" % (
						self._periodo_fiscal(),
						line.asiento_contable or '',
						line.m_correlativo_asiento_contable or '',
						self._convert_object_date(line.fecha_emision_comprobante),
						self._convert_object_date(line.fecha_vencimiento),
						line.tipo_comprobante or '',
						line.serie_comprobante or '',
						line.numero_comprobante or '',
						'',
						line.tipo_documento_cliente or '',
						line.numero_documento_cliente or '',
						line.razon_social or '',
						format(line.ventas_valor_facturado_exportacion,".2f"),
						format(line.ventas_base_imponible_operacion_gravada,".2f"),
						format(line.ventas_descuento_base_imponible,".2f"),
						format(line.ventas_igv,".2f"),
						format(line.ventas_descuento_igv,".2f"),
						format(line.ventas_importe_operacion_exonerada,".2f"),
						format(line.ventas_importe_operacion_inafecta,".2f"),
						format(line.isc,".2f"),
						format(line.ventas_base_imponible_arroz_pilado,".2f"),
						format(line.ventas_impuesto_arroz_pilado,".2f"),
						format(line.impuesto_consumo_bolsas_plastico,".2f"),
						format(line.otros_impuestos,".2f"),
						format(line.importe_total_comprobante,".2f"),
						line.codigo_moneda,
						format(line.tipo_cambio,".3f"),
						self._convert_object_date(line.fecha_emision_original),
						line.tipo_comprobante_original or '',
						line.serie_comprobante_original or '',
						line.numero_comprobante_original or '',
						line.ventas_identificacion_contrato_operadores or '',
						line.error_1 or '',
						line.ventas_indicador_comprobantes_medios_pago or '',
						line.oportunidad_anotacion)
			output.write(escritura.encode())


	def _convert_object_date(self, date):
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''

	############################################################################################ 

	meses={
	'01':'Enero',
	'02':'Febrero',
	'03':'Marzo',
	'04':'Abril',
	'05':'Mayo',
	'06':'Junio',
	'07':'Julio',
	'08':'Agosto',
	'09':'Septiembre',
	'10':'Octubre',
	'11':'Noviembre',
	'12':'Diciembre'
	}

	########################################################
	def _generate_xlsx(self, output):

		workbook = xlsxwriter.Workbook(output)
		ws = workbook.add_worksheet('reporte de ventas')

		titulo1 = workbook.add_format({'font_size': 16, 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo_1 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo_2 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo2 = workbook.add_format({'font_size': 8, 'align': 'center','valign': 'vcenter','color':'black', 'text_wrap': True, 'left':True, 'right':True,'bottom': True, 'top': True, 'bold':True , 'font_name':'Arial'})
		titulo3 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo4 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo5 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap':True, 'font_name':'Arial', 'bold':True})
		titulo6 = workbook.add_format({'font_size': 8, 'align': 'center','valign': 'vcenter', 'text_wrap': True, 'top': True, 'bold':True , 'font_name':'Arial'})
		titulo7 = workbook.add_format({'font_size': 8, 'align': 'center','valign': 'vcenter'})


		number_left = workbook.add_format({'font_size': 8, 'align': 'left', 'num_format': '#,##0.00', 'font_name':'Arial'})
		number_right = workbook.add_format({'font_size': 8, 'align': 'right', 'num_format': '#,##0.00', 'font_name':'Arial'})
		
		letter1 = workbook.add_format({'font_size': 7, 'align': 'left', 'font_name':'Arial'})
		letter3 = workbook.add_format({'font_size': 7, 'align': 'right','num_format': '#,##0.00', 'font_name':'Arial'})
		letter3_negrita = workbook.add_format({'font_size': 7, 'align': 'right','num_format': '#,##0.00', 'font_name':'Arial','bold': True})

		titulo_ruc_per_mes = workbook.add_format({'font_size': 13, 'align': 'left', 'text_wrap':False, 'bold': True, 'font_name':'Calibri'})

		ws.set_column('A:A', 1,letter3)
		ws.set_column('B:B', 10,letter1)
		ws.set_column('C:C', 12,letter1)
		ws.set_column('D:D', 8,letter1)
		ws.set_column('E:E', 8,letter1)
		ws.set_column('F:F', 12,letter3)
		ws.set_column('G:J', 8,letter3)
		ws.set_column('G:G', 8,letter3)
		ws.set_column('H:H', 13,letter1)
		ws.set_column('I:I', 13,letter1)
		ws.set_column('J:J', 13,letter1)
		ws.set_column('K:K', 10,number_right)
		ws.set_column('L:L', 10,number_right)
		ws.set_column('M:M', 14,number_right)
		ws.set_column('N:N', 14,number_right)
		ws.set_column('O:O', 8,number_right)
		ws.set_column('P:P', 8,number_right)
		ws.set_column('Q:Q', 12,number_right)
		ws.set_column('R:R', 12,number_right)
		ws.set_column('S:S', 12,letter3)
		ws.set_column('T:T', 12,letter3)
		ws.set_column('U:X', 12,letter3)
		ws.set_column('V:Y', 12,letter3)
		ws.set_column('W:W', 14,letter3)
		ws.set_column('Z:Z', 12,letter3)
		ws.set_column('AA:AA', 8,letter3)
		ws.set_column('AB:AB', 8,letter3)
		ws.set_column('AC:AC', 8,letter3)
		ws.set_column('AD:AD', 8,letter3)
		ws.set_column('AE:AE', 8,letter3)
		ws.set_column('AF:AF', 12,letter3)
		ws.set_column('AG:AG', 12,letter3)
		ws.set_column('AH:AH', 12,letter3)
		ws.set_column('AI:AI', 12,letter3)
		ws.set_column('AJ:AJ', 8,letter3)


		users = self.env['res.users'].browse(self._uid)


		ws.merge_range('A1:I1','FORMATO 14.1: REGISTRO DE VENTAS E INGRESOS', titulo1)
		
		ws.write(1,1,'PERIODO',titulo_1)
		ws.write(1,2,self._periodo_fiscal() ,titulo_2)
		

		ws.write(2,1,'RUC :',titulo_1)
		ws.write(2,2,users.company_id.vat or '',titulo_2)
		
		ws.merge_range('B4:F4','APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL:', titulo_1)
		ws.write(3,6,users.company_id.name,titulo_2)
		ws.merge_range('G4:J4',users.company_id.name, titulo_2)

				
		ws.merge_range('B6:B11','NÚMERO CORRELATIVO DEL REGISTRO O CÓDIGO UNICO DE LA OPERACIÓN', titulo2)
		ws.merge_range('C6:C11','FECHA DE EMISION DEL COMPROBANTE DE PAGO O DOCUMENTO', titulo2)
		ws.merge_range('D6:D11','FECHA DE VENCIMIENTO Y/O PAGO', titulo2)

		ws.merge_range('E6:G7','COMPROBANTE DE PAGO O DOCUMENTO', titulo2)

		ws.merge_range('E8:E11','TIPO TABLA 10', titulo2)
		ws.merge_range('F8:F11','Nº SERIE O Nº DE LA SERIE DE LA MAQUINA REGISTRADORA', titulo2)
		ws.merge_range('G8:G11','NÚMERO', titulo2)

		ws.merge_range('H6:J7','INFORMACIÓN DEL CLIENTE', titulo2)

		ws.merge_range('H8:I9','DOCUMENTO DE IDENTIDAD', titulo2)
		ws.merge_range('H10:H11','TIPO (TABLA 2)', titulo2)
		ws.merge_range('I10:I11','NUMERO)', titulo2)
		
		ws.merge_range('J8:J11','APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL', titulo2)

		ws.merge_range('K6:K11','VALOR FACTURADO DE LA EXPORTACION', titulo2)
		ws.merge_range('L6:L11','BASE IMPONIBLE DE LA OPERACIÓN GRAVADA', titulo2)
		

		ws.merge_range('M6:N7','IMPORTE TOTAL DE LA OPERACIÓN EXONERADA O INAFECTO', titulo2)
		ws.merge_range('M8:M11','EXONERADA', titulo2)
		ws.merge_range('N8:N11','INAFECTA', titulo2)

		ws.merge_range('O6:O11','ISC', titulo2)
		ws.merge_range('P6:P11','IGV Y/O IPM', titulo2)
		ws.merge_range('Q6:Q11','OTRO TRIBUTOS Y CARGOS QUE NO FORMAN PARTE DE LA BASE IMPONIBLE', titulo2)
		ws.merge_range('R6:R11','IMPORTE TOTAL DEL COMPROBANTE DE PAGO', titulo2)
		ws.merge_range('S6:S11','TIPO DE CAMBIO', titulo2)
	
		ws.merge_range('T5:W5','SOLO NOTAS DE CREDITO/DEBITO', titulo7)
		ws.merge_range('T6:W7','REFERENCIA DEL COMPROBANTE DE PAGO O DOCUMENTO ORIGINAL QUE SE MODIFICA', titulo2)
		ws.merge_range('T8:T11','FECHA', titulo2)
		ws.merge_range('U8:U11','TIPO (TABLA 10)', titulo2)
		ws.merge_range('V8:V11','SERIE', titulo2)
		ws.merge_range('W8:W11','Nº DEL COMPROBANTE DE PAGO	O DOCUMENTO', titulo2)


		ws.freeze_panes(11,0)

		fila = 10

		total = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
		
		for line in self.ple_sale_line_ids:

			fila +=1

			ws.write(fila,1, line.asiento_contable)
			ws.write(fila,2,self._convert_object_date(line.fecha_emision_comprobante) or '' )
			
			ws.write(fila,3,self._convert_object_date(line.fecha_vencimiento) or '' )
	
			ws.write(fila,4, line.tipo_comprobante or '')
			###SERIE O CODIGO DE LA DEPENDENCIA ADUANERA (FALTA !!)
			ws.write(fila,5,line.serie_comprobante or '')
		
			ws.write(fila,6,line.numero_comprobante or '')
			ws.write(fila,7,line.tipo_documento_cliente or '')
			ws.write(fila,8,line.numero_documento_cliente or '')

			ws.write(fila,9, line.razon_social or '')
			ws.write(fila,10,line.ventas_valor_facturado_exportacion)
			total[0] = total[0] + line.ventas_valor_facturado_exportacion
			###################IGV
			ws.write(fila,11,line.ventas_base_imponible_operacion_gravada)
			total[1] = total[1] + line.ventas_base_imponible_operacion_gravada

			ws.write(fila,12,line.ventas_importe_operacion_exonerada)
			total[2] = total[2] + line.ventas_importe_operacion_exonerada

			ws.write(fila,13,line.ventas_importe_operacion_inafecta)
			total[3] = total[3] + line.ventas_importe_operacion_inafecta

			ws.write(fila,14,line.isc)
			total[4] = total[4] + line.isc

			ws.write(fila,15,line.ventas_igv)
			total[5] = total[5] + line.ventas_igv

			ws.write(fila,16,line.otros_impuestos)
			total[6] = total[6] + line.otros_impuestos

			ws.write(fila,17,line.importe_total_comprobante)
			total[7] = total[7] + line.importe_total_comprobante
			
			ws.write(fila,18,format(line.tipo_cambio,".3f"))
			
			###################REFERENCIA DEL COMPROBANTE / TIPO (TABLA 10)
			ws.write(fila,24-5,self._convert_object_date(line.fecha_emision_original) or '' )
			ws.write(fila,25-5,line.tipo_comprobante_original or '')
			ws.write(fila,26-5,line.serie_comprobante_original or '')
			ws.write(fila,27-5,line.numero_comprobante_original or '')
			
	
			############ESCRIBIENDO TOTALES !!!!!!
		fila += 1
		ws.write(fila,9,'TOTALES :',letter3_negrita)
		ws.write(fila,10,total[0],letter3_negrita)
		ws.write(fila,11,total[1],letter3_negrita)
		ws.write(fila,12,total[2],letter3_negrita)		
		ws.write(fila,13,total[3],letter3_negrita)
		ws.write(fila,14,total[4],letter3_negrita)
		ws.write(fila,15,total[5],letter3_negrita)
		ws.write(fila,16,total[6],letter3_negrita)
		ws.write(fila,17,total[7],letter3_negrita)
		workbook.close()

	#######################################################

	meses={
	'01':'Enero',
	'02':'Febrero',
	'03':'Marzo',
	'04':'Abril',
	'05':'Mayo',
	'06':'Junio',
	'07':'Julio',
	'08':'Agosto',
	'09':'Septiembre',
	'10':'Octubre',
	'11':'Noviembre',
	'12':'Diciembre'
	}


	def _convert_currency(self, inv, valor):
		amount = valor
		if inv.currency_id and inv.company_id and inv.currency_id != inv.company_id.currency_id:
			currency_id = inv.currency_id
			amount = currency_id._convert(valor, inv.company_id.currency_id, inv.company_id, inv.invoice_date or inv.date)
		return amount

	def _data_ple_sale_head(self):
		users = self.env['res.users'].browse(self._uid)
		return [self.meses[self.fiscal_month] , self.fiscal_year , users.company_id.vat or '' , users.company_id.name or '', users.company_id.currency_id.name or '']