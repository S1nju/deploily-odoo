from odoo import models, fields, api

class SchoolAttendance(models.Model):
    _name = 'school.attendance'
    _description = 'Student Attendance'

    name = fields.Char(compute='_compute_name', store=True)
    student_id = fields.Many2one('school.student', 'Student', required=True, ondelete='cascade')

    @api.depends('course_id', 'session_id')
    def _compute_name(self):
        for record in self:
            if record.session_id:
                record.name = f"{record.session_id.name}"
            else:
                record.name = f"{record.course_id.name}" if record.course_id else "Attendance"
                
    course_id = fields.Many2one('school.course', 'Course', required=True, ondelete='cascade')
    session_id = fields.Many2one('school.course.session', 'Session', ondelete='cascade')
    date = fields.Date('Date', required=True, default=fields.Date.today)
    hours_attended = fields.Float('Hours Attended')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late')
    ], string='Status', default='pending')
    center_id = fields.Many2one('school.center', related='course_id.center_id', store=True, string='Center')
    
    # Session Internal Evaluations for Student
    evaluation_punctuality = fields.Selection([
        ('excellent', 'ممتاز'), ('good', 'جيد'), ('average', 'متوسط'), ('weak', 'ضعيف')
    ], string='حرص التلميذ على الحضور في الوقت')
    
    evaluation_focus = fields.Selection([
        ('excellent', 'ممتاز'), ('good', 'جيد'), ('average', 'متوسط'), ('weak', 'ضعيف')
    ], string='اهتمام وتركيز التلميذ في الحصة')
    
    evaluation_interaction = fields.Selection([
        ('excellent', 'ممتاز'), ('good', 'جيد'), ('average', 'متوسط'), ('weak', 'ضعيف')
    ], string='تفاعل التلميذ مع الاستاذ')
    
    evaluation_homework = fields.Selection([
        ('excellent', 'ممتاز'), ('good', 'جيد'), ('average', 'متوسط'), ('weak', 'ضعيف')
    ], string='حرص التلميذ على إنجاز التمارين المنزلية')
