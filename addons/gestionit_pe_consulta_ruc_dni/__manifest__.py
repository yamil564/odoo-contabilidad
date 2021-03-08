{
    "name": "Generación y Emisión de comprobantes electrónicos XML a SUNAT",
    "author": "Gestión IT",
    "description": "",
    "depends": ["base", "l10n_latam_base", "gestionit_pe_ubicaciones"],
    "data": [
        'data/res_company.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
    ],
    "external_dependencies": {"python": ["signxml"]}
}
