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
        'views/product/view_product_uom.xml',
        'views/sale_order/view_sale_order.xml',
        # 'views/partner/view_partner.xml',
        'views/account/view_account_journal.xml',
        'views/account/view_account_move.xml',
        # 'security/res_groups.xml',
        'data/product_uom.xml',
        'data/tax_group.xml',
        'data/account_journal.xml',
    ],
    "external_dependencies": {"python": ["signxml"]}
}
