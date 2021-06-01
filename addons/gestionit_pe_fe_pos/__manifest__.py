{
    "name":"POS Facturación Electrónica",
    "depends":['base','point_of_sale','gestionit_pe_fe','gestionit_pe_ubicaciones','l10n_latam_base'],
    "data":[
        "assets.xml",
        "views/pos_config.xml",
        "views/pos_order.xml",
        "data/report_pos.xml"
    ],
    "qweb":[
        "static/src/xml/show_journals.xml",
        "static/src/xml/client_screen.xml",
        "static/src/xml/payment_screen.xml",
        "static/src/xml/order_receipt.xml"
    ]
}