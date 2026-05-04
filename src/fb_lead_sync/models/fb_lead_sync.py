# -*- coding: utf-8 -*-
import logging
import requests
from datetime import datetime, timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

FACEBOOK_GRAPH_URL = 'https://graph.facebook.com/v19.0'


class FbLeadSync(models.Model):
    _name = 'fb.lead.sync'
    _description = 'Facebook Lead Sync Engine'

    @api.model
    def _get_param(self, key):
        """Helper to read system parameters."""
        return self.env['ir.config_parameter'].sudo().get_param(key, default='')

    @api.model
    def sync_facebook_leads(self):
        """
        Main method called by the daily cron job.
        Fetches leads from Facebook Lead Ads and creates them in Odoo CRM.
        """
        _logger.info("=== Facebook Lead Sync: Starting daily sync ===")

        # --- Read credentials from Settings ---
        sync_active = self._get_param('fb_lead_sync.sync_active')
        if not sync_active or sync_active == 'False':
            _logger.info("Facebook Lead Sync is disabled. Skipping.")
            return

        access_token = self._get_param('fb_lead_sync.access_token')
        form_id = self._get_param('fb_lead_sync.form_id')
        default_team_id = self._get_param('fb_lead_sync.default_team_id')
        default_user_id = self._get_param('fb_lead_sync.default_user_id')

        if not access_token or not form_id:
            _logger.warning("Facebook Lead Sync: Missing access token or form ID in settings.")
            self.env['fb.lead.log'].sudo().create({
                'status': 'no_credentials',
                'leads_found': 0,
                'leads_created': 0,
                'leads_skipped': 0,
                'error_message': 'Access Token or Form ID is missing. Please configure them in Settings > Facebook Lead Sync.',
            })
            return

        # --- Fetch leads from Facebook Graph API ---
        # We fetch leads submitted since yesterday (daily sync)
        since_date = int((datetime.now() - timedelta(days=1)).timestamp())

        url = f"{FACEBOOK_GRAPH_URL}/{form_id}/leads"
        params = {
            'access_token': access_token,
            'fields': 'id,created_time,field_data',
            'filtering': f'[{{"field":"time_created","operator":"GREATER_THAN","value":{since_date}}}]',
            'limit': 100,
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            _logger.error("Facebook Lead Sync: API call failed: %s", str(e))
            self.env['fb.lead.log'].sudo().create({
                'status': 'error',
                'leads_found': 0,
                'leads_created': 0,
                'leads_skipped': 0,
                'error_message': f'Facebook API error: {str(e)}',
            })
            return

        fb_leads = data.get('data', [])
        _logger.info("Facebook Lead Sync: Found %d leads from Facebook.", len(fb_leads))

        leads_created = 0
        leads_skipped = 0
        created_lead_ids = []

        # --- Resolve optional defaults ---
        team = False
        if default_team_id:
            team = self.env['crm.team'].sudo().browse(int(default_team_id))

        user = False
        if default_user_id:
            user = self.env['res.users'].sudo().browse(int(default_user_id))

        # --- Process each Facebook lead ---
        for fb_lead in fb_leads:
            fb_lead_id = fb_lead.get('id')
            field_data = fb_lead.get('field_data', [])

            # Parse the field_data list into a dict
            lead_fields = {}
            for field in field_data:
                name = field.get('name', '').lower()
                values = field.get('values', [])
                lead_fields[name] = values[0] if values else ''

            # Extract common fields (Facebook field names may vary by form)
            email = (
                lead_fields.get('email') or
                lead_fields.get('email_address') or
                lead_fields.get('e-mail') or ''
            )
            phone = (
                lead_fields.get('phone_number') or
                lead_fields.get('phone') or
                lead_fields.get('mobile') or ''
            )
            first_name = (
                lead_fields.get('first_name') or
                lead_fields.get('firstname') or ''
            )
            last_name = (
                lead_fields.get('last_name') or
                lead_fields.get('lastname') or ''
            )
            full_name = (
                lead_fields.get('full_name') or
                lead_fields.get('name') or
                f"{first_name} {last_name}".strip() or
                'Facebook Lead'
            )
            city = lead_fields.get('city', '')

            # Check for duplicate: same FB lead ID stored in description/source
            existing = self.env['crm.lead'].sudo().search([
                ('description', 'ilike', f'fb_lead_id:{fb_lead_id}')
            ], limit=1)

            if existing:
                _logger.info("Lead %s already exists, skipping.", fb_lead_id)
                leads_skipped += 1
                continue

            # Build lead values
            lead_vals = {
                'name': f"{full_name} (Facebook Lead)",
                'contact_name': full_name,
                'email_from': email,
                'phone': phone,
                'city': city,
                'type': 'lead',
                'description': (
                    f"Imported from Facebook Lead Ads\n"
                    f"fb_lead_id:{fb_lead_id}\n\n"
                    f"All fields from form:\n" +
                    '\n'.join([f"  {k}: {v}" for k, v in lead_fields.items()])
                ),
                'source_id': self._get_or_create_source('Facebook Lead Ads'),
            }

            if team:
                lead_vals['team_id'] = team.id
            if user:
                lead_vals['user_id'] = user.id

            new_lead = self.env['crm.lead'].sudo().create(lead_vals)
            created_lead_ids.append(new_lead.id)
            leads_created += 1
            _logger.info("Created CRM lead: %s (fb_lead_id: %s)", new_lead.name, fb_lead_id)

        # --- Log the sync result ---
        self.env['fb.lead.log'].sudo().create({
            'status': 'success',
            'leads_found': len(fb_leads),
            'leads_created': leads_created,
            'leads_skipped': leads_skipped,
            'lead_ids': [(6, 0, created_lead_ids)],
            'error_message': f'Sync completed. {leads_created} leads created, {leads_skipped} already existed.',
        })

        _logger.info(
            "=== Facebook Lead Sync: Done. Created: %d, Skipped: %d ===",
            leads_created, leads_skipped
        )

    @api.model
    def _get_or_create_source(self, name):
        """Get or create a UTM source for tracking."""
        Source = self.env['utm.source'].sudo()
        source = Source.search([('name', '=', name)], limit=1)
        if not source:
            source = Source.create({'name': name})
        return source.id
