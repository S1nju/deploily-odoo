from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SchoolCourseSession(models.Model):
    _name = 'school.course.session'
    _description = 'Class Session / Report'
    _order = 'date desc, id desc'
    
    name = fields.Char('Session Title', required=True)
    course_id = fields.Many2one('school.course', 'Course', required=True, ondelete='cascade')
    date = fields.Date('Date', default=fields.Date.context_today)
    
    start_datetime = fields.Datetime('Start Time', required=True, default=fields.Datetime.now)
    end_datetime = fields.Datetime('End Time', required=True, default=fields.Datetime.now)
    room_id = fields.Many2one('school.room', 'Classroom')
    center_id = fields.Many2one('school.center', related='course_id.center_id', store=True)
    
    @api.constrains('start_datetime', 'end_datetime', 'room_id')
    def _check_room_overlap(self):
        for session in self:
            if session.room_id and session.start_datetime and session.end_datetime:
                overlapping = self.search([
                    ('id', '!=', session.id),
                    ('room_id', '=', session.room_id.id),
                    ('start_datetime', '<', session.end_datetime),
                    ('end_datetime', '>', session.start_datetime)
                ], limit=1)
                if overlapping:
                    raise ValidationError(f"Room '{session.room_id.name}' is already booked for another session ({overlapping.name}) during this time period.")
    
    test_ids = fields.Many2many('school.course.test', string='Tests Conducted')
    
    def action_open_scanner_for_session(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/school/attendance/scanner?session_id={self.id}',
            'target': 'new',
        }
    
    # Internal Tutor Report Fields
    door_opened_on_time = fields.Boolean('هل تم فتح الباب في الوقت ؟', default=False)
    room_tidy = fields.Boolean('هل وجدت القاعة مرتبة ؟', default=False)
    
    class_type = fields.Selection([
        ('review', 'مراجعة الدروس السابقة'),
        ('exercises', 'حل التمارين'),
        ('exam_prep', 'التحضير للامتحان'),
    ], string='ماهو نوع الحصة ؟')
    
    # Challenges
    ch_time = fields.Boolean('صعوبة إدارة الوقت')
    ch_resources = fields.Boolean('وسائل / تجهيزات / موارد ناقصة')
    ch_tech = fields.Boolean('مشاكل تقنية')
    ch_subject = fields.Boolean('صعوبات في الموضوع')
    ch_levels = fields.Boolean('تفاوت مستويات الطلاب')
    ch_crowd = fields.Boolean('عدد كبير من الطلاب')
    ch_interaction = fields.Boolean('عدم تفاعل التلاميذ')
    ch_discipline = fields.Boolean('قلة انضباط التلاميذ')
    ch_late = fields.Boolean('تأخر التلاميذ في دخول القسم')
    ch_focus = fields.Boolean('قلة تركيز الطلاب')
    ch_prep = fields.Boolean('عدم التحضير المسبق من قبل الطلاب')
    ch_none = fields.Boolean('لا توجد')
    ch_other = fields.Char('أخرى (مجال مفتوح للكتابة)')
    
    execution_percentage = fields.Selection([
        ('25', '25 %'),
        ('50', '50 %'),
        ('75', '75 %'),
        ('100', '100 %'),
    ], string='نسبة تنفيذ النقاط والأنشطة المخططة للحصة')

    # Parent Visible Field
    report = fields.Html('Public Summary (Visible to Parents)')
