# Part of OCA. See LICENSE file for full copyright and licensing details.
{
    "name": "Algerian Payroll",
    "summary": "Gestion de la Paie conforme à la réglementation algérienne",
    "description": """
Algerian Payroll (Gestion de la Paie - Algérie)
================================================
Ce module gère la paie selon la réglementation algérienne :

- Paramétrage des taux légaux : CNAS, IRG, IEP, SMIG
- Calcul automatique du Brut, Net à payer, Charge patronale
- Cotisations sociales salariales et patronales (CNAS)
- Impôt sur le Revenu Global (IRG) avec barème progressif
- Indemnité d'Expérience Professionnelle (IEP)
- Indemnité de panier, transport, allocations familiales
- Salaire unique
- Bulletin de paie individuel conforme
- Déclaration CNAS mensuelle et annuelle (G50 + G29)
- Déclaration mensuelle et annuelle IRG
- État 301 bis, Journal 104, État des charges
- Journal de paie mensuel
- Fiche salarié complète
    """,
    "version": "18.0.1.0.0",
    "category": "Payroll",
    "author": "OCA, Algerian Contributors",
    "website": "https://github.com/OCA/l10n-algeria",
    "license": "LGPL-3",
    "depends": [
        "payroll",
        "hr",
        "hr_contract",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/l10n_dz_payroll_security.xml",
        "data/l10n_dz_hr_payroll_rate_data.xml",
        "data/l10n_dz_salary_rule_category_data.xml",
        "data/l10n_dz_salary_structure_data.xml",
        "data/l10n_dz_salary_rules_data.xml",
        "views/l10n_dz_hr_payroll_rate_views.xml",
        "views/hr_contract_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_payslip_views.xml",
        "views/res_config_settings_views.xml",
        "views/menus.xml",
        "report/report_payslip_dz2.xml",
        "report/report_payslip_dz2_template.xml",
        "wizard/wizard_attestation_views.xml",
        "report/report_attestation.xml",
        "report/report_attestation_template.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
