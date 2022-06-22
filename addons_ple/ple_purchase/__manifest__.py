{
	'name': 'SUNAT PLE-Compras',
	'version': "1.1.0",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['account','ple_base','bo_pe_contabilidad_documents','l10n_pe_detraccion'],
	'description':'''
		Modulo de reportes PLE de Najarro.
			> Compras
		''',
	'data':[
		'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/ple_purchase_view.xml',
		'views/ple_purchase_line_view.xml',
	],
	'installable': True,
    'auto_install': False,
}