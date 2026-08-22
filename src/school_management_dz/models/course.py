from odoo import models, fields, api

class SchoolServiceCategory(models.Model):
    _name = 'school.service.category'
    _description = 'Service Category'

    name = fields.Char('Name', required=True)
    subcategory_ids = fields.One2many('school.service.subcategory', 'category_id', 'Subcategories')

class SchoolServiceSubcategory(models.Model):
    _name = 'school.service.subcategory'
    _description = 'Service Subcategory'

    name = fields.Char('Name', required=True)
    category_id = fields.Many2one('school.service.category', 'Category', required=True)
    course_ids = fields.One2many('school.course', 'subcategory_id', 'Courses')

class SchoolCenter(models.Model):
    _name = 'school.center'
    _description = 'Tutoring Center'

    name = fields.Char('Center Name', required=True)
    address = fields.Text('Address')

class SchoolCourse(models.Model):
    _name = 'school.course'
    _description = 'School Course'
    _inherit = ['website.published.mixin']

    name = fields.Char('Course Name', required=True)
    subcategory_id = fields.Many2one('school.service.subcategory', 'Subcategory', required=True)
    category_id = fields.Many2one('school.service.category', related='subcategory_id.category_id', store=True)
    
    tutor_id = fields.Many2one('hr.employee', 'Tutor', domain="[('is_tutor', '=', True)]")
    recruitment_id = fields.Many2one('hr.applicant', 'Recruitment Link')
    schedule_ids = fields.One2many('school.course.schedule', 'course_id', 'Schedules')
    test_ids = fields.One2many('school.course.test', 'course_id', 'Tests/Assessments')
    session_ids = fields.One2many('school.course.session', 'course_id', string='Sessions')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    center_id = fields.Many2one('school.center', 'Center Location')
    room_id = fields.Many2one('school.room', 'Classroom / Room')
    location = fields.Char('Location Details', help="Extra location details")
    hourly_price = fields.Float('Hourly Price', default=0.0, help="Price per attended hour")
    image_1920 = fields.Image('Image')
    description = fields.Html('Information')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_sessions()
        return records

    def write(self, vals):
        res = super().write(vals)
        # Only sync if fields that affect schedule were changed
        if any(f in vals for f in ['start_date', 'end_date', 'schedule_ids', 'room_id']):
            self._sync_sessions()
        return res

    def _sync_sessions(self):
        from datetime import timedelta
        for course in self:
            if not course.start_date or not course.end_date:
                continue
                
            current_date = course.start_date
            # Fetch existing sessions to prevent exact duplicates
            existing_sessions = self.env['school.course.session'].search([
                ('course_id', '=', course.id)
            ])
            existing_starts = [sess.start_datetime for sess in existing_sessions]
            
            while current_date <= course.end_date:
                wd = str(current_date.weekday())
                schedules = course.schedule_ids.filtered(lambda s: s.weekday == wd)
                
                for sched in schedules:
                    start_h = int(sched.start_time)
                    start_m = int(round((sched.start_time - start_h) * 60))
                    end_h = int(sched.end_time)
                    end_m = int(round((sched.end_time - end_h) * 60))
                    
                    sess_start = current_date.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                    sess_end = current_date.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
                    
                    # Only create if exactly this session start doesn't already exist
                    if sess_start not in existing_starts:
                        self.env['school.course.session'].create({
                            'name': f"{course.name} - {sess_start.strftime('%Y-%m-%d')}",
                            'course_id': course.id,
                            'room_id': course.room_id.id,
                            'start_datetime': sess_start,
                            'end_datetime': sess_end,
                            'date': sess_start.date(),
                        })
                    
                current_date += timedelta(days=1)
