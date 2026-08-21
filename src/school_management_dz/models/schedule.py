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

    weekday_string = fields.Char(compute='_compute_time_display')
    time_string = fields.Char(compute='_compute_time_display')

    def _compute_time_display(self):
        weekdays = dict(self._fields['weekday'].selection)
        for record in self:
            record.weekday_string = weekdays.get(record.weekday, '')
            start_h = int(record.start_time)
            start_m = int(round((record.start_time - start_h) * 60))
            end_h = int(record.end_time)
            end_m = int(round((record.end_time - end_h) * 60))
            record.time_string = f"{start_h:02d}:{start_m:02d} - {end_h:02d}:{end_m:02d}"
