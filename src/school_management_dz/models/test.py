from odoo import models, fields

class SchoolCourseTest(models.Model):
    _name = 'school.course.test'
    _description = 'Course Test/Assessment'
    
    name = fields.Char('Question/Test Title', required=True)
    course_id = fields.Many2one('school.course', 'Course', required=True, ondelete='cascade')
    description = fields.Text('Description / Instructions')
    question_ids = fields.One2many('school.course.test.question', 'test_id', string='Questions')

class SchoolCourseTestQuestion(models.Model):
    _name = 'school.course.test.question'
    _description = 'Course Test Question'
    _order = 'sequence, id'
    
    test_id = fields.Many2one('school.course.test', required=True, ondelete='cascade')
    name = fields.Char('Question', required=True)
    question_type = fields.Selection([('text', 'Text/Paragraph Answer'), ('boolean', 'Yes/No')], default='text', string='Type')
    sequence = fields.Integer('Sequence', default=10)
