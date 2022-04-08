
{
    'name': 'Recibo por honorarios',
    "summary": "Recibo por honorarios",
    'version': '1.0.0',
    'category': '',
    'license': 'AGPL-3',
    'author': "Franco Najarro",
    'mail': '',
    'website': '',
    'depends': ['account','factiva_cpe'],
    'data': [
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml',
        'views/account_journal_view.xml',
    ],
    'active': False,
    'installable': True
}
