import calendar
from io import BytesIO, StringIO
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import xlsxwriter
from odoo.exceptions import UserError , ValidationError

import logging
_logger=logging.getLogger(__name__)

class PleDiaryAccountingPlan(models.Model):
	_name='ple.diary.accounting.plan'
	_inherit='ple.base'
	_description = "Modulo PLE Libros diario- Plan Contable"
	#5.4 LIBRO DIARIO DE FORMATO SIMPLIFICADO - DETALLE DEL PLAN CONTABLE UTILIZADO (*)


	ple_diary_accounting_plan_line_ids=fields.One2many('ple.diary.accounting.plan.line','ple_diary_accounting_plan_id',string="Libro diario-Plan Contable",readonly=True, states={'draft': [('readonly', False)]})
	
	fiscal_period= fields.Date(string="Día/Mes/Año Fiscal",required= True , readonly=True, states={'draft': [('readonly', False)]})
	identificador_operaciones = fields.Selection(selection=[('0','Cierre de operaciones'),('1','Empresa operativa'),('2','Cierre de libro')],
		string="Identificador de operaciones", required=True, default="1")
	identificador_libro = fields.Selection(selection='available_formats_diary_accounting_plan_sunat', string="Identificador de libro" )
	
	print_order = fields.Selection(default='codigo_cuenta_desagregado')


	@api.onchange('fiscal_period')
	def _onchange_fiscal_period(self):
		for rec in self:
			if rec.fiscal_period:
				rec.fiscal_year=str(rec.fiscal_period.year)
				rec.fiscal_month=str(format(rec.fiscal_period.month,"02"))

	
	def action_print(self):
		
		if ( self.print_format and self.identificador_libro and self.identificador_operaciones) :
			return super(PleDiaryAccountingPlan , self).action_print()
		else:
			raise UserError(_('NO SE PUEDE IMPRIMIR , Los campos: Formato Impresión , Identificador de operaciones y Identificador de libro son obligatorios, llene esos campos !!!'))
	
	def available_formats_diary_accounting_plan_sunat(self):
		formats=[('050300','Libro diario-Plan Contable'),
				('050400','Libro diario simplificado-Plan Contable')
			]
		return formats

	
	def criterios_impresion(self):
		res = [('codigo_cuenta_desagregado','Código Cuenta Desagregado'),('descripcion','Descripción de la Cuenta contable')]
		
		return res


	def _action_confirm_ple(self):
		return True

	
	def _get_datas(self, domain):
		orden=""
		if self.print_order == 'descripcion':
			orden = 'name asc'		
		elif self.print_order == 'codigo_cuenta_desagregado':
			# aux="invoice_id.invoice_number"
			orden =  'code asc '		
		
		return self._get_query_datas('account.account', domain, orden)



	
	def _get_order_print(self , object):

		if self.print_order == 'description': # ORDENAMIENTO POR LA FECHA CONTABLE
			total=sorted(object, key=lambda PleDiaryAccountingPlanLine: PleDiaryAccountingPlanLine.descripcion_cuenta_contable) 
		
		elif self.print_order == 'codigo_cuenta_desagregado':
			total=sorted(object , key=lambda PleDiaryAccountingPlanLine: PleDiaryAccountingPlanLine.codigo_cuenta_desagregado ) # ORDENAMIENTO POR EL CODIGO DE CUENTA DESAGREGADO
		
		return total

	def _get_domain(self): ## DADO QUE SON VALORES QUE NO CAMBIAN PERIODICAMENTE ESTA FUNCION NO SE REQUIERE !!
		domain = []
			# ('date','>=',self._get_star_date()),
			# ('date','<=',self._get_end_date()),
		
			
		return domain


	def file_name(self, file_format):
		nro_de_registros = '1' if len(self.ple_diary_accounting_plan_line_ids)>0 else '0'

		file_name = "LE%s%s%s00%s%s%s1.%s" % (self.company_id.vat, self._periodo_fiscal(),
								 self.identificador_libro, self.identificador_operaciones, nro_de_registros,
								self.currency_id.code_ple or '1', file_format)
		return file_name


	def _periodo_fiscal_line(self):

		periodo = "%s%s%s" % (self.fiscal_period.year or 'YYYY', format(self.fiscal_period.month,"02") or 'MM' , format(self.fiscal_period.day,"02") or 'DD') # , self.fiscal_day or 'DD')

		return periodo


	
	def generar_libro(self):
		
		self.state='open'
		
		self.ple_diary_accounting_plan_line_ids.unlink()
		registro=[]
		k=0
		for line in self._get_datas(self._get_domain()):
			registro.append((0,0,{'account_id':line.id,'codigo_cuenta_desagregado':line.code ,'descripcion_cuenta_contable': line.name} ) )

	
		self.ple_diary_accounting_plan_line_ids = registro ## EN EL MOMENTO DE ASIGNAR REGISTRO AL PUNTERO SE EMPIEZAN A CREAR LOS CAMPOS CORRESPONDIENTES AL MODELO



	
	def _init_buffer(self, output):
		# output parametro de buffer que ingresa vacio
		if self.print_format == 'xlsx':
			self._generate_xlsx(output)
		elif self.print_format == 'txt':
			self._generate_txt(output)
		return output

	def _convert_object_date(self, date):
		# parametro date que retorna un valor vacio o el foramto 01/01/2100 dia/mes/año
		if date:
			return date.strftime('%d/%m/%Y')
		else:
			return ''


	
	def _generate_txt(self, output):
	
		for line in self._get_order_print(self.ple_diary_accounting_plan_line_ids) :
			###########################################################
			escritura="%s|%s|%s|%s|%s|%s|%s|%s|\n" % (
				self._periodo_fiscal_line() ,
				line.codigo_cuenta_desagregado[:24] ,
				line.descripcion_cuenta_contable[:100] ,
				line.codigo_plan_contable ,
				line.descripcion_plan_contable_deudor[:60]  ,
				line.codigo_cuenta_contable_corporativa[:24]  ,
				line.descripcion_cuenta_contable_corporativa[:100] ,
				line.indicador_estado_operacion )
				
			output.write(escritura.encode())
			####################################################################