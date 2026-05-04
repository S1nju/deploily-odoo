# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models


class AppointmentSlot(models.Model):
    _name = 'appointment.slot'
    _description = 'Disponibilité / Créneau'
    _order = 'date asc'

    date = fields.Date(string='Date', required=True)
    is_available = fields.Boolean(string='Disponible', default=True)
    note = fields.Char(string='Note (ex: Férié, Congé...)')
    appointment_ids = fields.One2many('appointment.appointment', 'slot_id', string='Rendez-vous')
    appointment_count = fields.Integer(string='Nb RDV', compute='_compute_appointment_count')
    booking_link = fields.Char(string='Lien de réservation', compute='_compute_booking_link', store=False)

    # Token for the global booking page (company-wide, not per slot)
    company_token = fields.Char(string='Token société',
                                default=lambda self: str(uuid.uuid4()))

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = len(rec.appointment_ids)

    def _compute_booking_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            rec.booking_link = f"{base_url}/booking"

    def action_toggle_availability(self):
        self.is_available = not self.is_available

    def action_view_appointments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f'Rendez-vous du {self.date}',
            'res_model': 'appointment.appointment',
            'view_mode': 'list,form',
            'domain': [('date_appointment', '=', self.date)],
            'context': {'default_date_appointment': self.date, 'default_slot_id': self.id},
        }


class AppointmentConfig(models.Model):
    """Stores the global booking page token/link."""
    _name = 'appointment.config'
    _description = 'Configuration Rendez-vous'

    name = fields.Char(default='Configuration', readonly=True)
    booking_token = fields.Char(string='Token', default=lambda self: str(uuid.uuid4()), readonly=True)
    booking_link = fields.Char(string='Lien de réservation', compute='_compute_link')
    active = fields.Boolean(default=True)

    def _compute_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            rec.booking_link = f"{base_url}/booking/{rec.booking_token}"

    def action_regenerate_token(self):
        self.booking_token = str(uuid.uuid4())

    @api.model
    def get_or_create_config(self):
        config = self.search([], limit=1)
        if not config:
            config = self.create({'name': 'Configuration'})
        return config
