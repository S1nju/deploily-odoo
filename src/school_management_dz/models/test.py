from odoo import models, fields

class SchoolCourseTest(models.Model):
    _name = 'school.course.test'
    _description = 'Course Test/Assessment'
    
    name = fields.Char('Question/Test Title', required=True)
    course_id = fields.Many2one('school.course', 'Course', required=True, ondelete='cascade')
    description = fields.Text('Description / Instructions')
