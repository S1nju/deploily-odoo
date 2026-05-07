from odoo import models, fields


class HrMedical(models.Model):
    _name = 'hr.medical'
    _description = 'Dossier médical employé'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employé",
        required=True,
        ondelete='cascade'
    )
    visit_date = fields.Date(
        string="Date de visite",
        required=True
    )
    doctor = fields.Char(
        string="Nom du médecin"
    )
    clinic = fields.Char(
        string="Clinique / Hôpital"
    )
    diagnosis = fields.Text(
        string="Diagnostic"
    )
    treatment = fields.Text(
        string="Traitement"
    )
    notes = fields.Text(
        string="Notes"
    )
    next_visit = fields.Date(
        string="Prochaine visite"
    )
    # Type d'incident (compatibilité vues legacy)
    incident_type = fields.Selection([
        ('work_accident', 'Accident de travail'),
        ('occupational_disease', 'Maladie professionnelle'),
        ('general_health', 'Santé générale')
    ], string="Type d’incident")

    attachment_ids = fields.Many2many(
        'ir.attachment',
        string="Pièces jointes"
    )