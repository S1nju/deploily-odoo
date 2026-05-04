# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Facebook App credentials
    fb_app_id = fields.Char(
        string='Facebook App ID',
        config_parameter='fb_lead_sync.app_id',
        help='Your Facebook App ID from developers.facebook.com'
    )
    fb_app_secret = fields.Char(
        string='Facebook App Secret',
        config_parameter='fb_lead_sync.app_secret',
        help='Your Facebook App Secret from developers.facebook.com'
    )
    fb_access_token = fields.Char(
        string='Facebook Access Token',
        config_parameter='fb_lead_sync.access_token',
        help='Your long-lived Page Access Token from Facebook'
    )
    fb_ad_account_id = fields.Char(
        string='Ad Account ID',
        config_parameter='fb_lead_sync.ad_account_id',
        help='Your Facebook Ad Account ID (format: act_XXXXXXXXX)'
    )
    fb_form_id = fields.Char(
        string='Lead Form ID',
        config_parameter='fb_lead_sync.form_id',
        help='The ID of the Facebook Lead Ad form to fetch leads from'
    )
    fb_sync_active = fields.Boolean(
        string='Enable Daily Sync',
        config_parameter='fb_lead_sync.sync_active',
        help='Enable or disable the automatic daily sync of Facebook leads'
    )
    fb_default_team_id = fields.Many2one(
        'crm.team',
        string='Default Sales Team',
        config_parameter='fb_lead_sync.default_team_id',
        help='Sales team to assign to synced leads'
    )
    fb_default_user_id = fields.Many2one(
        'res.users',
        string='Default Salesperson',
        config_parameter='fb_lead_sync.default_user_id',
        help='Salesperson to assign to synced leads'
    )
