from odoo import models, fields

class SchoolCourseSchedule(models.Model):
    _name = 'school.course.schedule'
    _description = 'Course Schedule'
    
    course_id = fields.Many2one('school.course', 'Course', required=True, ondelete='cascade')
    weekday = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], string='Day of Week', required=True)
    start_time = fields.Float('Start Time', required=True)
    end_time = fields.Float('End Time', required=True)
