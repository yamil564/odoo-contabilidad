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
        'views/sale_order/view_sale_order.xml'
    ],
    "external_dependencies": {"python": ["signxml"]}
}
