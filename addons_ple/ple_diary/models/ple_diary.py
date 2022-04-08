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

class PleDiary(models.Model):
	_name='ple.diary'
	_inherit='ple.base'
	_description = "Modulo PLE Libros diary"

	ple_diary_line_ids=fields.One2many('ple.diary.line','ple_diary_id',string="Libro diary",readonly=True, states={'draft': [('readonly', False)]})


	identificador_operaciones = fields.Selection(selection=[('0','Cierre de operaciones'),('1','Empresa operativa'),('2','Cierre de libro')],
		string="Identificador de operaciones", required=True, default="1")
	identificador_libro = fields.Selection(selection='available_formats_diary_sunat', string="Identificador de libro" )
	print_order = fields.Selection(default="codigo_cuenta_desagregado")

	### FILTROS DINÁMICOS
	######################### FILTROS DINAMICOS, NUEVOS CAMPOS AGREGADOS !!!
	partner_ids = fields.Many2many('res.partner','ple_diary_partner_rel','partner_id','ple_diary_id' ,string="Socios")
	options_partner=fields.Selection(selection=options,string="")

	account_ids = fields.Many2many('account.account','ple_diary_account_rel','account_id','ple_diary_id',string='Cuentas')
	options_account=fields.Selection(selection=options,string="")
	
	journal_ids = fields.Many2many('account.journal','ple_diary_journal_rel','journal_id','ple_diary_id',string="Diarios")
	
	options_journal=fields.Selection(selection=options,string="")

	move_ids = fields.Many2many('account.move','ple_diary_move_rel','move_id','ple_diary_id',string='Asientos Contables')
	
	options_move=fields.Selection(selection=options,string="")

	payment_ids = fields.Many2many('account.payment','ple_diary_payment_rel','payment_id','ple_diary_id',string="Pagos")
	
	options_payment=fields.Selection(selection=options,string="")
	
	########################################################

	## BLOQUES DE IMPRESIÓN
	block_counter=fields.Integer(string="Bloque de Impresión N°" , default=0 , readonly=True)
	block_size=fields.Integer(string="Número de Registros por bloque", default=3000)
	##########################
	##buffer para asientos a apuntes

	fecha_impresion=fields.Date(string="Fecha de Impresión manual" , default=datetime(datetime.now().year,datetime.now().month,datetime.now().day).date())
	#################################################
	fecha=fields.Boolean(string="Fecha" ,readonly=True , states={'draft': [('readonly', False)]})
	periodo=fields.Boolean(string="Periodo" ,readonly=True , states={'draft': [('readonly', False)]})

	date_from=fields.Date(string="Desde:" ,readonly=True , states={'draft': [('readonly', False)]})
	date_to=fields.Date(string="Hasta:" ,readonly=True , states={'draft': [('readonly', False)]})

	############## CHECK para indicar si se incluye o no registros anteriores no declarados
	incluir_anteriores_no_declarados = fields.Boolean(string="Incluir registros anteriores no declarados", default=False)

	fin_asiento=fields.Boolean(default=False)
	fin_documento=fields.Boolean(default=False)

	infimo=fields.Integer(default=0, string="Infimo")
	supremo=fields.Integer(default=0,string="Supremo")

	fecha_inicio=''
	fecha_fin=''
	###############################
	_sql_constraints = [
		('fiscal_month', 'unique(fiscal_month,fiscal_year,company_id)',  'Este periodo para el PLE ya existe , revise sus registros de PLE creados!!!'),
	]
	################################################################
	def button_view_tree(self):	
		if self.ple_diary_line_ids:
			diccionario = {
				'name': 'Libro PLE Diario-Mayor-Simplificado',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'ple.diary.line',
				'view_id': False,
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', [i.id for i in self.ple_diary_line_ids] or [])],
				'context':{
					'search_default_filter_cuenta':1}
			}
			return diccionario
	##############################################################
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
	def unlink (self):
		for line in self:
			for line2 in line.ple_diary_line_ids:
				line2.move_line_id.write({'declared_ple_5_1_5_2_6_1':False})
			return super(PleDiary, line).unlink()

	##############################################################################
	def saldo_account_move_in_account_account(self,move_id , code_account):
		return sum(move_id.line_ids.filtered(lambda r:r.account_id.code==code_account).mapped('balance'))

	def account_move_account_account_totales(self):
		## creando matriz de cuentas vs asientos contables !!

		# ACTIVOS
		# PASIVOS
		# GASTOS
		# INGRESOS
		# CUENTAS DE FUNCION DEL GASTO
		asientos_totales = self.ple_diary_line_ids.mapped('move_id')

		codigo_cuentas_activos = sorted(list(self.ple_diary_line_ids.mapped('move_line_id.account_id').filtered(lambda t:t.code[0] in ['1','2','3']).mapped('code')))
		codigo_cuentas_pasivos = sorted(list(self.ple_diary_line_ids.mapped('move_line_id.account_id').filtered(lambda t:t.code[0] in ['4']).mapped('code')))
		codigo_cuentas_gastos = sorted(list(self.ple_diary_line_ids.mapped('move_line_id.account_id').filtered(lambda t:t.code[0] in ['6']).mapped('code')))
		codigo_cuentas_ingresos = sorted(list(self.ple_diary_line_ids.mapped('move_line_id.account_id').filtered(lambda t:t.code[0] in ['7']).mapped('code')))
		codigo_cuentas_funcion_gasto = sorted(list(self.ple_diary_line_ids.mapped('move_line_id.account_id').filtered(lambda t:t.code[0] in ['9']).mapped('code')))
		return [asientos_totales,codigo_cuentas_activos,codigo_cuentas_pasivos,codigo_cuentas_gastos,codigo_cuentas_ingresos,codigo_cuentas_funcion_gasto]

	##############################################################################
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
	###############################################################################

	def reinicializar_parametros_bloque(self):
		self.block_counter=0
		self.fin_asiento=False
		self.fin_documento=False
		self.infimo=0
		self.supremo=0

	def generate_tree_records(self):
		if self.identificador_libro=='050100':
			array_total=[]
			for item in self.ple_diary_line_ids:
				array_total += [(item.move_id.id,item)]

			diccionario_asientos={}
			grupos_de_asientos=groupby(sorted(array_total),lambda x:x[0])

			for k , v in grupos_de_asientos:
				self.diccionario_asientos[k]=[i[1] for i in list(v)]

	def get_asientos_actuales(self):
		return list(set([i.move_id for i in self.ple_diary_line_ids[self.infimo:self.supremo]]))

	def action_print(self):
		if ( self.print_format and self.identificador_libro and self.identificador_operaciones) :
			if self.print_format =='pdf':
				return self.print_quotation()
			elif self.print_format =='xlsx' and self.identificador_libro=='050200':
				raise UserError(_("ESTE FORMATO NO ESTA DISPONIBLE !!"))
			else:
				return super(PleDiary , self).action_print()
		else:
			raise UserError(_('NO SE PUEDE IMPRIMIR , Los campos: Formato Impresión , Identificador de operaciones y Identificador de libro son obligatorios, llene esos campos !!!'))

	def available_formats_diary_sunat(self):
		formats=[('050100','Libro diario'),
				('050200','Libro diario simplificado'),
				('060100','Libro Mayor'),
			]
		return formats
	
	def print_quotation(self):
		if self.identificador_libro=='050100':
			self.infimo=self.supremo
			self.supremo += self.block_size	

			if self.supremo <= len(self.ple_diary_line_ids)-1:
				if self.ple_diary_line_ids[self.supremo-1].move_id.id==self.ple_diary_line_ids[self.supremo].move_id.id:
					self.fin_asiento=False
				else:
					self.fin_asiento=True
			else:
				self.fin_asiento=True
				self.fin_documento=True

			self.block_counter += 1
			return self.env.ref('ple_diary.report_custom_a4').with_context(discard_logo_check=True).report_action(self)
		elif self.identificador_libro == '060100':
			self.infimo=self.supremo
			self.supremo += self.block_size	
			if self.supremo <= len(self.ple_diary_line_ids)-1:
				if self.ple_diary_line_ids[self.supremo-1].move_id.id==self.ple_diary_line_ids[self.supremo].move_id.id:
					self.fin_asiento=False
				else:
					self.fin_asiento=True
			else:
				self.fin_asiento=True
				self.fin_documento=True
			self.block_counter += 1
			self._get_current_accounts()
			return self.env.ref('ple_diary.report_custom_ledger').with_context(discard_logo_check=True).report_action(self)
		elif self.identificador_libro=='050200':
			return self.env.ref('ple_diary.report_custom_a4_simplificado').with_context(discard_logo_check=True).report_action(self)
	#########################################

	def _get_current_accounts(self):
		lines = sorted(self.ple_diary_line_ids , key=lambda PleDiaryLine: (PleDiaryLine.codigo_cuenta_desagregado, PleDiaryLine.asiento_contable, PleDiaryLine.fecha_contable))
		blocks = lines[self.infimo:self.supremo]
		end = self.supremo + 1 <= len(lines) and self.supremo + 1 or (len(lines) - 1)
		if blocks[-1].codigo_cuenta_desagregado_id.id == lines[end].codigo_cuenta_desagregado_id.id:
			if blocks[-1].id != lines[end].id:
				self.supremo = list(map(lambda line: line.codigo_cuenta_desagregado_id.id, lines)).index(blocks[-1].codigo_cuenta_desagregado_id.id)
			else:
				self.supremo =  end + 1



	def criterios_impresion(self):
		res = super(PleDiary, self).criterios_impresion() or []
		res += [('codigo_cuenta_desagregado','Código Cuenta Desagregado')]
		return res


	def _action_confirm_ple(self):  
		for line in self.ple_diary_line_ids:
			if(line.move_line_id.declared_ple_5_1_5_2_6_1 != True):
				super(PleDiary , self)._action_confirm_ple('account.move.line' , line.move_line_id.id ,{'declared_ple_5_1_5_2_6_1':True})
	
	def _get_datas(self, domain):
		orden="move_id asc"
		if self.print_order == 'date':
			orden += ',date asc , account_id asc '		
		elif self.print_order == 'codigo_cuenta_desagregado':
			orden +=  ',account_id asc , date asc '		
		elif self.print_order == 'nro_documento':
			orden += ',account_id asc ,date asc '
		return self._get_query_datas('account.move.line', domain, orden)


	def _get_order_print(self , object):

		if self.print_order == 'date': # ORDENAMIENTO POR LA FECHA CONTABLE
			total=sorted(object, key=lambda PleDiaryLine: (  PleDiaryLine.asiento_contable , PleDiaryLine.codigo_cuenta_desagregado , PleDiaryLine.fecha_contable) )
		elif self.print_order == 'nro_documento':
			total=sorted(object , key=lambda PleDiaryLine: (PleDiaryLine.asiento_contable) ) # ,PlediaryLine.asiento_contable)) #ORDENAMIENTO POR EL NUMERO DEASIENTO CONTABLE
		elif self.print_order == 'codigo_cuenta_desagregado':
			total=sorted(object , key=lambda PleDiaryLine: (PleDiaryLine.asiento_contable , PleDiaryLine.fecha_contable ,  PleDiaryLine.codigo_cuenta_desagregado ) ) # ORDENAMIENTO POR EL CODIGO DE CUENTA DESAGREGADO
		return total

	def _get_domain(self):

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

		domain = [
			('move_id.state','!=','draft'),
			('declared_ple_5_1_5_2_6_1','!=',True),
			('date','>=',self.fecha_inicio),
			('date','<=',self.fecha_fin),
			]

		'''partners=tuple(self.partner_ids.mapped('id'))
		len_partners = len(partners or '')
		if len_partners:
			domain.append(('partner_id.id' ,'in' , partners))

		journals = tuple(self.journal_ids.mapped('id'))
		len_journals = len(journals or '')
		if len(self.journal_ids):
			domain.append(('journal_id.id' ,'in', journals))

		moves = tuple(self.move_ids.mapped('id'))
		len_moves = len(moves or '')
		if len(moves):
			domain.append(('move_id.id' ,'in', moves))


		payments = tuple(self.payment_ids.mapped('id'))
		len_payments = len(payments or '')
		if len(payments):
			domain.append(('payment_id.id' ,'in', payments))


		accounts = tuple(self.account_ids.mapped('id'))
		len_accounts = len(accounts or '')
		if len(accounts):
			domain.append(('account_id.id' ,'in', accounts))'''

		##############
		partners=tuple(self.partner_ids.mapped('id'))
		len_partners = len(partners or '')
		if len_partners:
			domain.append(('partner_id.id' ,self.options_partner or 'in' , partners))

		journals = tuple(self.journal_ids.mapped('id'))
		len_journals = len(journals or '')
		if len(self.journal_ids):
			domain.append(('journal_id.id' ,self.options_journal or 'in', journals))

		moves = tuple(self.move_ids.mapped('id'))
		len_moves = len(moves or '')
		if len(moves):
			domain.append(('move_id.id' ,self.options_move or 'in', moves))


		payments = tuple(self.payment_ids.mapped('id'))
		len_payments = len(payments or '')
		if len(payments):
			domain.append(('payment_id.id' ,self.options_payment or 'in', payments))


		accounts = tuple(self.account_ids.mapped('id'))
		len_accounts = len(accounts or '')
		if len(accounts):
			domain.append(('account_id.id' ,self.options_account or 'in', accounts))
		#########
			
		return domain


	def file_name(self, file_format):
		nro_de_registros = '1' if len(self.ple_diary_line_ids)>0 else '0'
		if self.periodo:
			file_name = "LE%s%s%s00%s%s%s1.%s" % (self.company_id.vat, self._periodo_fiscal(),
									self.identificador_libro, self.identificador_operaciones, nro_de_registros,
									self.currency_id.code_ple or '1', file_format)
		elif self.fecha:
			file_name = "LE%s%s%s00%s%s%s1.%s" % (self.company_id.vat, "%s00" %(self.date_to.strftime('%Y%m')),
									self.identificador_libro, self.identificador_operaciones, nro_de_registros,
									self.currency_id.code_ple or '1', file_format)
		return file_name

	def _periodo_fiscal(self):
		periodo = "%s%s00" % (self.fiscal_year or 'YYYY', self.fiscal_month or 'MM')
		return periodo


	def generar_libro(self):
		self.state='open'
		self.ple_diary_line_ids.unlink()
		registro=[]
		registro_efectivo=[]
		registro_banco=[]
		k=0
		for line in self._get_datas(self._get_domain()):
			registro.append((0,0,{'move_id':line.move_id.id , 'move_line_id':line.id , 'periodo':self._periodo_fiscal()}))
		self.ple_diary_line_ids = registro
		# self.generate_tree_records()



	def _init_buffer(self, output):
		if self.print_format == 'xlsx':
			if self.identificador_libro=='050100':
				self._generate_xlsx(output)
			elif self.identificador_libro=='060100':
				self._generate_ledger_xlsx(output)
			'''elif self.identificador_libro=='050200':
				raise UserError(_("ESTE FORMATO NO ESTA DISPONIBLE"))'''
				#raise UserError(_(salida))

		elif self.print_format == 'txt':
			if self.identificador_libro in ['050200','060100','050100']:
				self._generate_txt(output)
			
		return output

	def _convert_object_date(self, date):
		# parametro date que retorna un valor vacio o el foramto 01/01/2100 dia/mes/año
		if date:
			return date.strftime("%d/%m/%Y")
		else:
			return ''


	def _generate_txt(self, output):
	
		for line in self._get_order_print(self.ple_diary_line_ids) :
			escritura="%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n" % (
				line.periodo_apunte,
				(line.asiento_contable or '')[:40] ,
				(line.m_correlativo_asiento_contable or '')[:10] ,
				(line.codigo_cuenta_desagregado or '')[:24] ,
				(line.codigo_unidad_operacion or '')[:24]  ,
				(line.codigo_centro_costos or '')[:24] ,
				(line.tipo_moneda_origen or '')[:3] ,
				(line.tipo_doc_iden_emisor or '')[:1] ,
				(line.num_doc_iden_emisor or '')[:15] ,
				(line.tipo_comprobante_pago or '')[:2] ,
				(line.num_serie_comprobante_pago or '')[:20] ,
				(line.num_comprobante_pago or '')[:20],
				self._convert_object_date(line.fecha_contable) ,
				self._convert_object_date(line.fecha_vencimiento) ,
				self._convert_object_date(line.fecha_operacion) ,
				(line.glosa or '')[:200] ,
				(line.glosa_referencial or '')[:200],
				format(line.movimientos_debe,".2f") ,
				format(line.movimientos_haber,".2f") ,
				(line.dato_estructurado or '')[:92] ,
				line.indicador_estado_operacion or '' )

			output.write(escritura.encode())

################################
	def _generate_xlsx(self, output):
		workbook = xlsxwriter.Workbook(output)
		ws = workbook.add_worksheet('Libro diario')
		titulo1 = workbook.add_format({'font_size': 16, 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo_1 = workbook.add_format({'font_size': 8, 'align': 'left', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		titulo2 = workbook.add_format({'font_size': 8, 'align': 'center','valign': 'vcenter','color':'black', 'text_wrap': True, 'left':True, 'right':True,'bottom': True, 'top': True, 'bold':True , 'font_name':'Arial'})
		#######################################################
		titulo_2 = workbook.add_format({'font_size': 8, 'align': 'center', 'text_wrap': True, 'bold': True, 'font_name':'Arial'})
		##################################################################
		titulo5 = workbook.add_format({'font_size': 10, 'align': 'left', 'text_wrap':True, 'font_name':'Arial', 'bold':True})

		titulo6 = workbook.add_format({'font_size': 8, 'align': 'right', 'text_wrap': True, 'top': True, 'bold':True , 'font_name':'Arial'})
		number_left = workbook.add_format({'font_size': 8, 'align': 'left', 'num_format': '#,##0.00', 'font_name':'Arial'})
		number_right = workbook.add_format({'font_size': 8, 'align': 'right', 'num_format': '#,##0.00', 'font_name':'Arial'})
		number_right_tax_rate = workbook.add_format({'font_size': 8, 'align': 'right', 'num_format': '#,##0.000', 'font_name':'Arial'})
		
		letter1 = workbook.add_format({'font_size': 7, 'align': 'left', 'font_name':'Arial'})
		letter3 = workbook.add_format({'font_size': 7, 'align': 'right','num_format': '#,##0.00', 'font_name':'Arial'})
		letter3_negrita = workbook.add_format({'font_size': 7, 'align': 'right','num_format': '#,##0.00', 'font_name':'Arial','bold': True})

		ws.set_column('A:A', 2,letter1)
		ws.set_column('B:B', 24,letter1)
		ws.set_column('C:C', 11.5,letter1)
		ws.set_column('D:D', 30,letter1)
		ws.set_column('E:E', 11,letter1)
		ws.set_column('F:F', 13,letter1)
		ws.set_column('G:G', 13,letter1)
		ws.set_column('H:H', 8,letter1)
		ws.set_column('I:I', 30,letter1)
		ws.set_column('J:J', 11.5,number_right)
		ws.set_column('K:K', 11.5,number_right)
		ws.set_column('L:L', 9,number_right)

		ws.merge_range('B1:E1','FORMATO 5.1: LIBRO DIARIO',titulo1)

		ws.merge_range("B7:B8",'NÚMERO CORRELATIVO DEL REGISTRO O CÓDIGO ÚNICO DE LA OPERACIÓN',titulo2)
		ws.merge_range("C7:C8",'FECHA DE LA OPERACIÓN',titulo2)
		ws.merge_range("D7:D8",'GLOSA O DESCRIPCIÓN DE LA OPERACIÓN',titulo2)

		ws.merge_range('E7:G7','REFERENCIA DE LA OPERACIÓN', titulo2)
		ws.write(7,4,'CÓDIGO DEL LIBRO O REGISTRO', titulo2)
		## 7 , 8 , 9 
		ws.write(7,5,'NÚMERO CORRELATIVO', titulo2)
		ws.write(7,6,'NÚMERO DEL DOCUMENTO SUSTENTATORIO', titulo2)

		ws.merge_range('H7:I7','CUENTA CONTABLE ASOCIADA A LA OPERACIÓN', titulo2)
		ws.write(7,7,'CÓDIGO', titulo2)
		ws.write(7,8,'DENOMINACIÓN', titulo2)
		ws.merge_range('J7:K7','MOVIMIENTO', titulo2)
		ws.write(7,9,'DEBE', titulo2)
		ws.write(7,10,'HABER', titulo2)
		

		ws.write(2,1,'PERIODO:',titulo_1)
		ws.write(3,1,'RUC:',titulo_1)
		ws.merge_range('B5:D5','APELLIDO Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL:',titulo_1)
		ws.write(3,2,self.company_id.vat or '',titulo_2)

		ws.write(2,2,self._periodo_fiscal() or '',titulo_2)
		ws.merge_range('E5:I5',self.company_id.name or '',titulo_2)
		
		ws.freeze_panes(9,0)

		fila=8
		total=[0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0 ]

		asiento_contable_inicial=""
		haber_asiento_contable=0
		deber_asiento_contable=0
		total_haber=0
		total_deber=0
		ws.write(8,3,"PERIODO :" + self.fiscal_month)
		for line in  self._get_order_print(self.ple_diary_line_ids) :
			fila += 1
			if(fila > 9 and line.asiento_contable != asiento_contable_inicial ):
				ws.write(fila,8,"TOTAL EN EL RegCtb " + asiento_contable_inicial)
				ws.write(fila,9,deber_asiento_contable)
				ws.write(fila,10,haber_asiento_contable)
				deber_asiento_contable=0
				haber_asiento_contable=0
				fila += 1 
				ws.write(fila,3,"REGISTRO CONTABLE : " + (line.asiento_contable or ''))
				asiento_contable_inicial = line.asiento_contable
				fila += 1
			elif(line.asiento_contable != asiento_contable_inicial ):
				ws.write(fila,3,"REGISTRO CONTABLE : " + (line.asiento_contable or ''))
				asiento_contable_inicial = line.asiento_contable
				fila += 1

			ws.write(fila,1, line.asiento_contable)
			ws.write(fila,2,self._convert_object_date(line.fecha_operacion) or '' )
			ws.write(fila,4, "5")

			ws.write(fila,3,line.glosa or '' )

			ws.write(fila,6, (len(line.num_serie_comprobante_pago or '')!=0)*(str(line.num_serie_comprobante_pago or '') + '-' + str(line.num_comprobante_pago or '')) )
			ws.write(fila,7,line.codigo_cuenta_desagregado or '')
			ws.write(fila,8,line.codigo_cuenta_desagregado_id.name or '')
			ws.write(fila,9,line.movimientos_debe)
			ws.write(fila,10,line.movimientos_haber)
			haber_asiento_contable += line.movimientos_haber
			deber_asiento_contable += line.movimientos_debe
			total_haber += line.movimientos_haber
			total_deber += line.movimientos_debe
		########### ULTIMO ASIENTO
		fila += 1 
		ws.write(fila,8,"TOTAL EN EL RegCtb " + asiento_contable_inicial)
		ws.write(fila,9,deber_asiento_contable)
		ws.write(fila,10,haber_asiento_contable)
		##########################
		fila += 1
		ws.write(fila , 8,"TOTAL EN EL PERIODO " + self.fiscal_month)
		ws.write(fila  , 9 ,  total_deber)
		ws.write(fila  , 10 ,  total_haber)	
		workbook.close()

	##################
	################# PLE LIBRO MAYOR


	def get_initial_values(self):
		lines = self.env['account.move.line'].search([('date','<',"%s-%s-01" %(self.fiscal_year, self.fiscal_month))])
		account_dic = {}
		for line in lines:
			account_dic.setdefault(line.account_id,[0.0,0.0])
			account_dic[line.account_id][0] += line.debit
			account_dic[line.account_id][1] += line.credit
		return account_dic

	##############
	'''invoice_type_code = fields.Selection(selection=[('00', 'Otros'),
                                                    ('01', 'Factura'),
                                                    ('03', 'Boleta'),
                                                    ('07', 'Nota de crédito'),
                                                    ('08', 'Nota de débito')],
                                         string="Tipo de Comprobante",
                                         readonly=True
                                         )
	###########'''
	## subir al repo fe_gestion_it con la carpeta addons_ple !!
	########
	def get_initial_values_sql(self):
		fecha_inicial = ''

		if self.periodo:
			fecha_inicial = "%s-%s-01" %(self.fiscal_year, self.fiscal_month)
		elif self.fecha:
			fecha_inicial = self.date_from.strftime("%Y-%m-%d")

		query="""select aml.account_id,acac.code,acac.name 
			sum(aml.balance) from 
			account_move_line as aml join account_account acac on acac.id=aml.account_id 
			where aml.date < '%s' group by aml.account_id""" %(fecha_inicial)


	def _generate_ledger_xlsx(self, output):
		workbook = xlsxwriter.Workbook(output)
		ws = workbook.add_worksheet('Libro Mayor')
		titulo_1_0 = workbook.add_format({'font_size': 10, 'font_name':'Arial'})
		titulo_1 = workbook.add_format({'font_size': 8, 'font_name':'Arial'})
		titulo_2 = workbook.add_format({ 'font_size': 8, 'font_name':'Arial', 'bold': True, 'align': 'center', 'valign': 'center', 'border': 1})
		titulo_3 = workbook.add_format({ 'font_size': 8, 'font_name':'Arial', 'bold': True})
		ws.set_column('A:A', 13,titulo_1)
		ws.set_column('B:B', 16,titulo_1)
		ws.set_column('C:C', 30,titulo_1)
		ws.set_column('G:G', 16,titulo_1)
		ws.set_column('H:H', 16,titulo_1)
		ws.set_row(5, 20,titulo_1)
		ws.write(0,0,'Formato 6.1', titulo_1)
		ws.write(0,1,'Libro Mayor', titulo_1_0)
		ws.write(1,0,'Periodo', titulo_1)
		ws.write(1,1,self._periodo_fiscal(), titulo_1)
		ws.write(2,0,'RUC', titulo_1)
		ws.write(2,1,self.company_id.vat, titulo_1)
		ws.write(3,0,'Razón Social', titulo_1)
		ws.write(3,1,self.company_id.name, titulo_1)
		ws.write(4,0,'Expresado en', titulo_1)
		ws.write(5,0,'FECHA',titulo_2)
		ws.write(5,1,'NÚMERO',titulo_2)
		ws.write(5,2,'DESCRIPCIÓN DE LA OPERACIÓN',titulo_2)
		ws.merge_range('D6:F6','DOCUMENTO REFERENCIA',titulo_2)
		ws.write(5,6,'CÓDIGO',titulo_2)
		ws.write(5,7,'MOVIMIENTO',titulo_2)
		ws.write(5,8,'',titulo_2)
		ws.write(6,0,'OPERACIÓN',titulo_2)
		ws.write(6,1,'COMPROBANTE',titulo_2)
		ws.write(6,2,'',titulo_2)
		ws.write(6,3,'TD',titulo_2)
		ws.write(6,4,'NÚMERO',titulo_2)
		ws.write(6,5,'FECHA',titulo_2)
		ws.write(6,6,'ANEXO',titulo_2)
		ws.write(6,7,'DEBE',titulo_2)
		ws.write(6,8,'HABER',titulo_2)
		row = 7
		initial_accounting_entry = ''
		debe = 0
		credit = 0
		lines = sorted(self.ple_diary_line_ids , key=lambda PleDiaryLine: (PleDiaryLine.codigo_cuenta_desagregado, PleDiaryLine.asiento_contable, PleDiaryLine.fecha_contable))
		initial_values = self.get_initial_values()

		def total_balances(row):
			ws.write(row,3,'TOTAL MOVIMIENTO CUENTA',titulo_1)
			ws.write(row,7,debe,titulo_1)
			ws.write(row,8,credit,titulo_1)
			row += 1
			ws.write(row,3,'SALDO ACTUAL',titulo_1)
			current_balance = debe + (previous_balance if previous_balance else 0) - credit
			if current_balance >= 0:
				ws.write(row,7,abs(round(current_balance,1)),titulo_1)
			else:
				ws.write(row,8,abs(round(current_balance,1)),titulo_1)
			return row
		
		previous_balance = False
		for line in lines:
			if line.codigo_cuenta_desagregado_id.id != initial_accounting_entry:
				if row > 7:
					row = total_balances(row)
					debe = 0
					credit = 0
					row += 1

				initial_accounting_entry = line.codigo_cuenta_desagregado_id.id
				ws.write(row,0,line.codigo_cuenta_desagregado_id.code, titulo_3)
				ws.write(row,1,line.codigo_cuenta_desagregado_id.name, titulo_3)
				row += 1
				ws.write(row,3,'SALDO ANTERIOR', titulo_1)
				previous_balance = initial_values.get(line.codigo_cuenta_desagregado_id, False)

				if previous_balance:
					previous_balance = previous_balance[0] - previous_balance[1]
					if previous_balance >= 0:
						ws.write(row,7,abs(round(previous_balance,1)) or '', titulo_1)
					else:
						ws.write(row,8,abs(round(previous_balance,1)) or '', titulo_1)
				else:
					ws.write(row,8,'', titulo_1)
				row += 1

			ws.write(row,0,self._convert_object_date(line.fecha_operacion or ''),titulo_1)
			ws.write(row,1,line.move_id.name or '',titulo_1)
			ws.write(row,2,line.glosa or '',titulo_1)
			ws.write(row,3,line.tipo_comprobante_pago or '',titulo_1)
			ws.write(row,4,"%s-%s"%(line.num_serie_comprobante_pago or "", line.num_comprobante_pago or "") or '',titulo_1)
			ws.write(row,5,self._convert_object_date(line.fecha_contable or ''),titulo_1)
			ws.write(row,6,line.num_doc_iden_emisor or '',titulo_1)
			ws.write(row,7,line.movimientos_debe or '',titulo_1)
			ws.write(row,8,line.movimientos_haber or '',titulo_1)
			debe += line.movimientos_debe
			credit += line.movimientos_haber
			row += 1
			if line == lines[-1]:
				row = total_balances(row)
				row += 1
				ws.write(row,3,'TOTAL GENERAL',titulo_1)
				ws.write(row,7,round(sum([i.movimientos_debe for i in lines]),2),titulo_1)
				ws.write(row,8,round(sum([i.movimientos_haber for i in lines]),2),titulo_1)
		workbook.close()


	def is_menor(self,a,b):
		return a<b