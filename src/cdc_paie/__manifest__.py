# -*- coding: utf-8 -*-
{
    'name': 'CDC Gestion de la Paie',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Module de gestion de la paie conforme à la réglementation algérienne',
    'description': """
        Module de Gestion de la Paie - CDC ERP 026-2025
        ================================================
        Conforme à la réglementation algérienne :
        - Paramétrage de la paie (SMIG, CNAS, IRG)
        - Fiche salarié
        - Calcul de la paie (Brut, Net, IEP, indemnités)
        - Bulletin de paie individuel
        - Déclaration CNAS (G50, G29)
        - Déclaration IRG
        - Reporting complet (ATS, CNR, DFC, etc.)
        - Tableaux de bord
        - Interopérabilité avec Comptabilité (PC COMPTA)
        - Export CCP / Virement bancaire
    """,
    'author': 'CDC ERP',
    'depends': [
        'base',
        'hr',
        'hr_contract',
        'mail',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/paie_data.xml',
        'views/parametrage_views.xml',
        'views/employe_views.xml',
        'views/rubrique_views.xml',
        'views/bulletin_views.xml',
        'views/declaration_views.xml',
        'views/reporting_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
        'report/bulletin_report.xml',
        'report/bulletin_report_template.xml',
        'report/cnas_report.xml',
        'report/irg_report.xml',
        'views/wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cdc_paie/static/description/dashboard.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
