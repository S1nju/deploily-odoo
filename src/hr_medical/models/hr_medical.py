from odoo import models, fields


class HrMedical(models.Model):
    _name = 'hr.medical'
    _description = 'Employee Medical Record'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade')
    visit_date = fields.Date(string="Visit Date", required=True)
    doctor = fields.Char(string="Doctor Name")
    clinic = fields.Char(string="Clinic/Hospital")
    diagnosis = fields.Text(string="Diagnosis")
    treatment = fields.Text(string="Treatment")
    notes = fields.Text(string="Notes")
    next_visit = fields.Date(string="Next Visit")
    # Added to satisfy legacy views referencing 'incident_type'
    incident_type = fields.Selection([
        ('work_accident','Accident de Travail'),
        ('occupational_disease','Maladie Professionnelle'),
        ('general_health','Santé Générale')
    ],string="Incident Type")
    attachment_ids = fields.Many2many(
        'ir.attachment', 
    
        string="Attachments"
    )
