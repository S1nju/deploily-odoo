from odoo import models, fields

class SchoolAttendance(models.Model):
    _name = 'school.attendance'
    _description = 'Student Attendance'

    student_id = fields.Many2one('school.student', 'Student', required=True)
    course_id = fields.Many2one('school.course', 'Course', required=True)
    date = fields.Date('Date', required=True, default=fields.Date.today)
    hours_attended = fields.Float('Hours Attended')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late')
    ], string='Status', default='pending')
