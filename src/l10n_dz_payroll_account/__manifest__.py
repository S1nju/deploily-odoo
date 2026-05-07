# Part of OCA. See LICENSE file for full copyright and licensing details.
{
    "name": "Algerian Payroll Accounting",
    "summary": "Integration complete Paie Algerienne - Comptabilite SCF - G50 - Fiche Paie",
    "website":'https://deploily.cloud',
    "version": "18.0.1.0.0",
    "category": "Payroll",
    "author": "OCA, Algerian Contributors + SARL Transformatek",
    "license": "LGPL-3",
    "depends": [
        "l10n_dz_payroll",
        "payroll_account",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/account_mapping_data.xml",
        "views/hr_payroll_account_dz_views.xml",
        "report/report_grand_livre.xml",
        "report/report_grand_livre_template.xml",
        "report/report_g50.xml",
        "report/report_g50_template.xml",
        "wizard/wizard_g50_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "post_migrate": "post_migrate_hook",
        'license': 'LGPL-3',

}
