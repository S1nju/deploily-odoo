from asyncio import exceptions
from datetime import datetime
from odoo import models, fields,api
from odoo.exceptions import ValidationError

class HrMession(models.Model):
    _name = 'hr.mession'
    _description = 'Gestion des Missions'

    name = fields.Char(string="Objet de la mission", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employé")
    destination = fields.Char(string="Destination")
    date_start = fields.Date(string="Date de départ")
    date_end = fields.Date(string="Date de retour")
    mission_type = fields.Selection([
        ('national', 'National'),
        ('international', 'Étranger')
    ], string="Type de mission")
    mission_car = fields.Selection([('pc', 'voiture personnelle'), ('cc', 'voiture commune'),
                                    ('plane', 'Avion'), ('boat', 'Bateau'),
                                    ('other', 'Autre')], string="Locomotion")
    
    fee_ids = fields.One2many('hr.mession.fee', 'mission_id', string="Frais de mission")
    fee_amount = fields.Float(string="Total Frais", compute='_compute_fee_amount', store=True)
    mission_start_date = fields.Datetime(string="Date et heure de début", required=True)
    mission_end_date = fields.Datetime(string="Date et heure de fin", required=True)
    mission_duration = fields.Char(string="Durée de la mission", readonly=True)
    mession_real_start_date = fields.Datetime(string="Date et heure de début réelle")
    mession_real_end_date = fields.Datetime(string="Date et heure de fin réelle")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('done', 'Clôturé')
    ], string="Statut",default='draft')
    mission_notes = fields.Text(string='Notes')
    
    @api.depends('fee_ids.total_amount')
    def _compute_fee_amount(self):
        for mission in self:
            mission.fee_amount = sum(mission.fee_ids.mapped('total_amount'))
    
    @api.constrains('mission_start_date', 'mission_end_date')
    def _check_dates_and_compute_duration(self):
        for rec in self:
            if rec.mission_start_date and rec.mission_end_date:

                today = datetime.now()

                # Start date must not be in the past
                if rec.mission_start_date < today:
                    raise ValidationError(
                        "La date de début de mission doit être supérieure ou égale à la date actuelle."
                    )

                # End date validation
                if rec.mission_end_date <= rec.mission_start_date:
                    raise ValidationError(
                        "La date de fin de mission doit être supérieure à la date de début."
                    )

                # Compute duration
                delta = rec.mission_end_date - rec.mission_start_date
                rec.mission_duration = str(delta)
                    
    def action_approve(self):
        for mission in self:
            mission.state = 'approved'

    def action_reject(self):
        for mission in self:
            mission.state = 'rejected'

    def action_reset_draft(self):
        for mission in self:
            mission.state = 'draft'

    def action_mark_done(self):
        for mission in self:
            mission.state = 'done'