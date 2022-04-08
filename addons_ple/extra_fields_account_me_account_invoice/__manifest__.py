{
    'name': 'Campos cuentas ME en configuracion',
    'version': '1.0.0',
    'category': '',
    'license': 'AGPL-3',
    'summary': "Cuentas ME en configuración",
    'author': "Franco N.",
    'website': '',
    'depends': ['sale','account'],
    'data': [
        'data/account_data.xml',
        'views/res_partner_view.xml',
        'views/res_config_settings_view.xml',
        ],
    'installable': True,
    'autoinstall': False,
    'post_init_hook': '_configure_account_me',
}
