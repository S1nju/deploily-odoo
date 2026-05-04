# -*- coding: utf-8 -*-
{
    'name': 'Algeria - Amount to Text',
    'version': '18.0.1.0',
    'category': 'Accounting',
    'website': 'https://transformatek.dz/',
    'summary': 'This is the module print amount to Text in the Orders and Invoices reports.',
    'description': """
This is the module print amount to Text in the purchase reports.
========================================================================

This module applies to companies based in Algeria.

**Email:** contact@transformatek.dz
""",
    'author': 'Osis + TransformaTek',
    'depends': ['purchase', 'sale', 'account'],
    'data': [
        'reports/orders_invoice_reports.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
