# Part of OCA. See LICENSE file for full copyright and licensing details.
{
    "name": "Algerian Payroll Accounting",
    "summary": "Intégration Paie Algérienne avec la Comptabilité",
    "description": """
Algerian Payroll Accounting (Paie DZ + Comptabilité)
=====================================================
Étend le module l10n_dz_payroll avec l'intégration comptable :

- Génération automatique des écritures comptables à la confirmation du bulletin
- Journal de paie mensuel (PC COMPTA)
- Export comptable (PC COMPTA / DFC)
- Comptes débit/crédit par rubrique salariale algérienne
- Compte analytique par contrat
- Interopérabilité avec le module de Budget
- Avis de virement bancaire et CCP CS 102
    """,
    "version": "18.0.1.0.0",
    "category": "Payroll",
    "author": "OCA, Algerian Contributors",
    "website": "https://github.com/OCA/l10n-algeria",
    "license": "LGPL-3",
    "depends": [
        "l10n_dz_payroll",
        "payroll_account",
    ],
    "data": [
        "views/hr_payroll_account_dz_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
