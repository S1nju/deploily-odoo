from odoo import models, fields, api

class SchoolStudentChallenge(models.Model):
    _name = 'school.student.challenge'
    _description = 'Student Competency Challenge'
    
    registration_id = fields.Many2one('school.registration', 'Registration', required=True, ondelete='cascade')
    name = fields.Char('Competency / Challenge', required=True)
    state = fields.Selection([
        ('ongoing', 'Ongoing / Needs Tutoring'),
        ('passed', 'Passed')
    ], string='Status', default='ongoing')
    date_evaluated = fields.Date('Date Evaluated')
