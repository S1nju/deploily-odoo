from odoo import models, fields

class RhMission(models.Model):
    _name = 'rh.mission'
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
    
    fee_amount = fields.Float(string="Total Frais", compute="_compute_fees")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('approved', 'Approuvé'),
        ('done', 'Clôturé')
    ], default='draft')

    def _compute_fees(self):
        # Logique de calcul basée sur le "Mission Scale"
        for mission in self:
            # Calcul automatique ici
            mission.fee_amount = 0.0

