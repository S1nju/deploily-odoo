#!/usr/bin/env python3
import odoo
from odoo import api, SUPERUSER_ID

config = odoo.tools.config
config.parse_config(['-c', '/etc/odoo/odoo.conf'])

with odoo.api.Environment.manage():
    with odoo.registry('odoo').cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Find and uninstall hr_dz module
        module = env['ir.module.module'].search([('name', '=', 'hr_dz')])
        if module and module.state == 'installed':
            print(f"Uninstalling module: {module.name}")
            module.button_immediate_uninstall()
            print("Module uninstalled successfully")
        else:
            print(f"Module hr_dz not found or not installed. State: {module.state if module else 'not found'}")
        
        cr.commit()
