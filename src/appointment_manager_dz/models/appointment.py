# -*- coding: utf-8 -*-
import uuid
from odoo import api, fields, models


class Appointment(models.Model):
    _name = 'appointment.appointment'
    _description = 'Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_appointment desc'

    name = fields.Char(string='Référence', required=True, copy=False,
                       default=lambda self: 'Nouveau')
    client_name = fields.Char(string='Nom du client', required=True, tracking=True)
    client_email = fields.Char(string='Email', required=True, tracking=True)
    client_phone = fields.Char(string='Téléphone', tracking=True)
    client_company = fields.Char(string='Société', tracking=True)
    reason = fields.Text(string='Raison / Message', tracking=True)

    date_appointment = fields.Date(string='Date du rendez-vous', required=True, tracking=True)
    time_appointment = fields.Float(string='Heure', tracking=True)

    state = fields.Selection([
        ('new', 'Nouveau'),
        ('confirmed', 'Confirmé'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='Statut', default='new', tracking=True)

    crm_lead_id = fields.Many2one('crm.lead', string='Opportunité CRM', readonly=True)
    booking_token = fields.Char(string='Token', default=lambda self: str(uuid.uuid4()), readonly=True)

    slot_id = fields.Many2one('appointment.slot', string='Créneau')
    user_id = fields.Many2one('res.users', string='Responsable',
                              default=lambda self: self.env.user)
    notes = fields.Text(string='Notes internes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('appointment.appointment') or 'RDV/0001'
        records = super().create(vals_list)
        for record in records:
            record._create_crm_opportunity()
            record._send_confirmation_email()
        return records

    def _create_crm_opportunity(self):
        """Create a CRM opportunity linked to this appointment."""
        lead_vals = {
            'name': f"RDV - {self.client_name} - {self.date_appointment}",
            'contact_name': self.client_name,
            'email_from': self.client_email,
            'phone': self.client_phone,
            'partner_name': self.client_company or self.client_name,
            'type': 'opportunity',
            'description': (
                f"Rendez-vous créé depuis le formulaire de réservation en ligne.\n\n"
                f"Date: {self.date_appointment}\n"
                f"Client: {self.client_name}\n"
                f"Email: {self.client_email}\n"
                f"Téléphone: {self.client_phone or '-'}\n"
                f"Société: {self.client_company or '-'}\n\n"
                f"Raison / Message:\n{self.reason or '-'}"
            ),
        }
        lead = self.env['crm.lead'].sudo().create(lead_vals)
        self.crm_lead_id = lead.id

    def _send_confirmation_email(self):
        """Send confirmation email to the client."""
        template = self.env.ref('appointment_manager_dz.email_template_appointment_confirmation', raise_if_not_found=False)
        if template and self.client_email:
            template.sudo().send_mail(self.id, force_send=True)

    def action_confirm(self):
        self.state = 'confirmed'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_view_crm(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Opportunité',
            'res_model': 'crm.lead',
            'res_id': self.crm_lead_id.id,
            'view_mode': 'form',
        }
