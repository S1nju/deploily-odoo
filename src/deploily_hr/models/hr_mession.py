from odoo import models, fields

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
    mission_scale_id = fields.Many2one('hr.mession.scale', string="Barème", 
                                       domain="[('mission_type', '=', mission_type)]")
    
    fee_amount = fields.Float(string="Total Frais", compute="_compute_fees")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('done', 'Clôturé')
    ], default='draft')

    def _compute_fees(self):
        for mission in self:
            mission.fee_amount = 0.0
            if mission.mission_scale_id and mission.date_start and mission.date_end:
                # Use selected mission scale
                scale = mission.mission_scale_id
                
                # Calculate number of days
                delta = mission.date_end - mission.date_start
                num_days = delta.days + 1  # Include both start and end dates
                
                # Calculate total fees
                if not scale.is_covered:
                    mission.fee_amount = scale.daily_amount * num_days

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