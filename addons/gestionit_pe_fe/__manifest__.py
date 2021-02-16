{
    "name": "Generación y Emisión de comprobantes electrónicos XML a SUNAT",
    "author": "Gestión IT",
    "description": "",
    "depends": [
        "base",
        "account",
        "sale"
    ],
    "category": "invoicing",
    "data": [
        #  'data/tipo_afectacion.xml',
        'data/product_uom.xml',
        'views/product/view_product_uom.xml',
        'views/sale_order/view_sale_order.xml',
        'views/partner/view_partner.xml',
        'views/account/view_account_tax.xml',
        'views/account/view_account_journal.xml',
        'security/res_groups.xml'
    ],
    "external_dependencies": {"python": ["signxml"]}
}
