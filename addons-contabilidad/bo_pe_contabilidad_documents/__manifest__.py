{
	'name': 'Configuraciones de Contabilidad en Moneda Extranjera',
	'version': "1.1.0",
	'author': 'Franco Najarro',
	'website':'',
	'category':'',
	'depends':['account','purchase','sale','gestionit_pe_fe'],
	'description':'''
		Configuraciones de Contabilidad en Moneda Extranjera.
			> Configuraciones de Contabilidad en Moneda Extranjera
		''',
	'data':[
		'views/res_config_settings_view.xml',
		'views/res_partner_view.xml',
		'views/account_move_view.xml',
	],
	'installable': True,
    'auto_install': False,
}