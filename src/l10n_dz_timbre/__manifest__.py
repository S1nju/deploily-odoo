# -*- coding: utf-8 -*-
{
    'name': 'Algeria - Fiscal Timbre',
    'version': '18.0.1.0',
    'category': 'Accounting',
    "website":'https://deploily.cloud',
    'summary': 'This is the module calculate the Fiscal Timbre payments in invoices for cash.',
    'description': """
This is the module to manage the Fiscal Timbre in Odoo.
========================================================================

This module applies to companies based in Algeria.

**Email:** contact@transformatek.dz
""",
    'author': 'Osis + SARL Transformatek',
    'depends': ['sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/timbre_view.xml',
        'views/timbre_invoice_view.xml',
        'views/timbre_invoice_template.xml',
        'data/timbre_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
        'license': 'LGPL-3',

}
