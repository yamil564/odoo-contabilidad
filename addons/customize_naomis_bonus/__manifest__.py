{
    "name": "Customize - Naomis bonus",
    "author": "",
    "description": "Bonificaciones en las órdenes de venta",
    "depends": ["base", "sales_team", "sale_management", "account", "purchase", "stock"],
    "category": "sale",
    "data": [
        'security/res_groups.xml',
        'views/view_bonus_rules.xml',
        'views/view_sale_order.xml',
        'views/view_product_inherit.xml',
    ]
}
