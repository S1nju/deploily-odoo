# -*- coding: utf-8 -*-
{
    'name': 'Appointment Manager Dz',
    'version': '18.0.1.0.0',
    'category': 'CRM',
    'website': 'https://deploily.cloud',
    'summary': 'Manage appointments with calendar, booking links, and CRM integration',
    'author': 'SARL Transformatek',
    'depends': ['crm', 'mail', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/appointment_views.xml',
        'views/appointment_slot_views.xml',
        'views/appointment_calendar_views.xml',
        'views/menu.xml',
        'data/mail_template.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
