from odoo import models, fields, api

class SchoolAttendance(models.Model):
    _name = 'school.attendance'
    _description = 'Student Attendance'

    name = fields.Char(compute='_compute_name', store=True)
    student_id = fields.Many2one('school.student', 'Student', required=True)

    @api.depends('course_id')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.course_id.name}" if record.course_id else "Attendance"
    course_id = fields.Many2one('school.course', 'Course', required=True)
    date = fields.Date('Date', required=True, default=fields.Date.today)
    hours_attended = fields.Float('Hours Attended')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late')
    ], string='Status', default='pending')
