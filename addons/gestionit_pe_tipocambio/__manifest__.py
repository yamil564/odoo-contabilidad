{
    "name": "GIT - Actualización Automática de Tipo de Dólares desde SUNAT",
    "author": "Gestión IT",
    "description": "",
    'depends': [
        "base",
        "account",
        "sale_management", ],
    "category": "Uncategorized",
    "data": [
        'views/res_currency_view.xml',
        'views/account_invoice_form.xml',
        'models/ir_cron.xml'
    ],
    "external_dependencies": {"python": []}
}
