from odoo import models, fields
class HrMedical(models.Model):
    _name = 'hr.medical'
    _description = 'Suivi Social et Médical'

    employee_id = fields.Many2one('hr.employee', string="Employé")
    incident_type = fields.Selection([
        ('at', 'Accident de travail'),
        ('maladie', 'Congé Maladie'),
        ('visite', 'Visite Médicale')
    ], string="Type d'évènement")
    date_event = fields.Date(string="Date")
    description = fields.Text(string="Description / Diagnostic")
    is_covered = fields.Boolean(string="Prise en charge CNAS", default=False)