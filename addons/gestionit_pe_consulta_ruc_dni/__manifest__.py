{
    "name": "GIT - Consulta de datos de clientes",
    "author": "Gestión IT",
    "description": "Consulta y obtención de datos desde RUC o DNI",
    "depends": [
        "base",
        "l10n_latam_base",
        "gestionit_pe_ubicaciones"],
    "data": [
        'data/res_company.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
    ],
    "external_dependencies": {"python": ["signxml"]}
}
