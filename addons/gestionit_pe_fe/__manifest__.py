{
    "name": "GIT - Facturación electrónica - SUNAT",
    "author": "Gestión IT",
    "description": "Generación y Emisión de comprobantes electrónicos XML a SUNAT",
    "depends": [
        "base",
        "account",
        "sale",
        "sale_management",
        "stock",
        "sale_stock",
        "purchase",
        "l10n_pe",
        "l10n_latam_base",
        "account_tax_python",
        "account_debit_note",
        "gestionit_pe_ubicaciones",
    ],
    # "gestionit_pe_ubicaciones",
    # "gestionit_pe_consulta_ruc_dni",
    # "gestionit_pe_fe_consulta_web",
    # "gestionit_pe_ple",
    # "gestionit_pe_tipocambio",
    # "create_invoice_from_sale"
    "category": "invoicing",
    "data": [
        'security/res_groups.xml',
        'views/account/menu.xml',
        'views/product/view_product_uom.xml',
        'views/product/view_product_product.xml',
        'views/sale_order/view_sale_order.xml',
        'views/catalogs/sunat_catalogs.xml',
        'views/account/view_account_journal.xml',
        'views/account/view_account_move.xml',
        'views/account/view_account_move_line.xml',
        'views/account/view_acc_inv_factura.xml',
        'views/account/view_acc_inv_boleta.xml',
        'views/account/view_acc_inv_nota_credito.xml',
        'views/account/view_acc_inv_nota_debito.xml',
        'views/account/view_acc_summary.xml',
        'views/account/view_acc_com_baja.xml',
        'views/account/view_acc_log_status.xml',
        'views/account/view_account_log_status.xml',
        'views/account/view_acc_mis_comprobantes.xml',
        'views/partner/res_partner_bank.xml',
        'views/partner/res_partner.xml',
        'views/guia_remision/guia_remision_electronica.xml',
        'views/guia_remision/popup_form_seleccion_ubigeo.xml',
        'views/guia_remision/res_partner_destinatario.xml',
        'views/guia_remision/view_catalogo_motivo_traslado.xml',
        'views/guia_remision/view_transporte.xml',
        'views/guia_remision/menu.xml',
        'views/guia_remision/email_template.xml',
        'views/user/view_users.xml',
        'views/stock/view_stock_warehouse.xml',
        'views/company/view_cert_sunat.xml',
        'views/company/view_company.xml',
        'views/reportes/assets.xml',
        'views/reportes/external_layout_background_gestionit.xml',
        'views/reportes/report_invoice_document.xml',
        'views/res_config_settings.xml',
        'reports/report_guia_remision.xml',
        'reports/report.xml',
        'reports/report_saleorder_document.xml',
        'reports/report_purchaseorder_document.xml',
        'reports/paperformat.xml',
        'data/product_uom.xml',
        'data/tax_group.xml',
        'data/account_journal.xml',
        'data/motivo_traslado.xml',
        'data/modalidad_transporte.xml',
        'data/account_tax_data.xml',
        'data/ir_config_parameter.xml',
        'data/res_currency.xml',
        'data/identification_type.xml',
        'data/catalogs.xml',
        'cron/account_move_cron.xml',
        'cron/account_summary_cron.xml',
        'cron/comunicacion_baja_cron.xml',
        'cron/guia_remision_cron.xml',
        'cron/validez_comprobante_cron.xml',
        'assets.xml'
    ],
    # 'application': True,
    "external_dependencies": {"python": ["signxml"]},
    "qweb": ["static/src/xml/qty_at_date.xml"]
}
