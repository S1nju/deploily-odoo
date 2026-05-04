# -*- coding: utf-8 -*-
from odoo import fields, models


class FbLeadLog(models.Model):
    _name = 'fb.lead.log'
    _description = 'Facebook Lead Sync Log'
    _order = 'sync_date desc'

    sync_date = fields.Datetime(string='Sync Date', default=fields.Datetime.now)
    leads_found = fields.Integer(string='Leads Found')
    leads_created = fields.Integer(string='Leads Created')
    leads_skipped = fields.Integer(string='Already Existing (Skipped)')
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error'),
        ('no_credentials', 'Missing Credentials'),
    ], string='Status')
    error_message = fields.Text(string='Error / Notes')
    lead_ids = fields.Many2many('crm.lead', string='Created Leads')
