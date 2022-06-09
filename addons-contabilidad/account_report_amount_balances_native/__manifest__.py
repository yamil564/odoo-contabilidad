{
	'name': 'Balance de Sumas y Saldos Nativo',
	'version': "1.0.0",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['account','account_element','report_formats','unique_library_accounting_queries'],
	'description':'''
		Modulo de Balance de Sumas y Saldos Nativo.
			> Balance de Sumas y Saldos Nativo
		''',
	'data':[
		'security/ir.model.access.csv',
		'views/report_amount_balances_native_view.xml',
		'data/balance.category.column.native.csv',
	],
	'installable': True,
    'auto_install': False,
}
