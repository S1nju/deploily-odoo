# -*- coding: utf-8 -*-
{
    'name': 'Trésorerie Pro',
    'version': '18.0.1.1.0',
    'summary': 'Gestion prévisionnelle de la trésorerie',
    'category': 'Accounting',
    'author': 'SARL Transformatek',
    'website':"https://deploily.cloud",
    'depends': ['base', 'account', 'mail'],
    'data': [
        'security/tresorerie_security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/cron_data.xml',
        'views/compte_tresorerie_views.xml',
        'views/flux_tresorerie_views.xml',
        'views/dashboard_views.xml',
        'wizards/wizard_recurrence_views.xml',
        'views/menu_item.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
