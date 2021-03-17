{
    "name": "Generación y Emisión de comprobantes electrónicos XML a SUNAT",
    "author": "Gestión IT",
    "description": "",
    "depends": [
        "base",
        "account",
        "sale", "stock", "account_debit_note"
    ],
    "category": "invoicing",
    "data": [
        'views/product/view_product_uom.xml',
        'views/sale_order/view_sale_order.xml',
        'views/account/view_account_journal.xml',
        'views/account/view_account_move.xml',
        'views/account/view_acc_inv_factura.xml',
        'views/account/view_acc_inv_boleta.xml',
        'views/account/view_acc_inv_nota_credito.xml',
        'views/account/view_acc_inv_nota_debito.xml',
        'views/account/view_acc_summary.xml',
        'views/account/view_acc_com_baja.xml',
        'views/account/view_acc_log_status.xml',
        'views/account/view_account_log_status.xml',
        'views/user/view_users.xml',
        'views/stock/view_stock_warehouse.xml',
        'views/company/view_company.xml',
        'views/reportes/external_layout_background_gestionit.xml',
        'views/reportes/report_invoice_document.xml',
        'data/product_uom.xml',
        'data/tax_group.xml',
        'data/account_journal.xml',
        'security/res_groups.xml'
    ],
    "external_dependencies": {"python": ["signxml"]}
}
