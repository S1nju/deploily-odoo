from odoo import models, fields

class SchoolCourseSession(models.Model):
    _name = 'school.course.session'
    _description = 'Class Session / Report'
    _order = 'date desc, id desc'
    
    name = fields.Char('Session Title', required=True)
    course_id = fields.Many2one('school.course', 'Course', required=True)
    date = fields.Date('Date', default=fields.Date.context_today, required=True)
    report = fields.Html('Session Report / Summary')
