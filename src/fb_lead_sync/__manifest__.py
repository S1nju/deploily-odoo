# -*- coding: utf-8 -*-
{
    'name': 'Facebook Lead Sync',
    'version': '18.0.1.0.0',
    'category': 'CRM',
    'summary': 'Sync Facebook Lead Ads form submissions into Odoo CRM leads daily',
    'description': """
        This module connects your Odoo CRM with Facebook Lead Ads.
        - Configure your Facebook API credentials in Settings
        - A daily scheduled job fetches new leads from your Facebook forms
        - Leads are automatically created in the CRM module
    """,
    'author': 'Custom',
    'depends': ['crm', 'mail', 'base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/fb_lead_log_views.xml',
        'views/menu.xml',
        'data/cron_job.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
