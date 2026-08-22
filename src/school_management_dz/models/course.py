from odoo import models, fields

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

    def _compute_website_url(self):
        super()._compute_website_url()
        for course in self:
            course.website_url = "/course/%s" % course.id

    def action_generate_sessions(self):
        from datetime import timedelta
        for course in self:
            if not course.start_date or not course.end_date:
                continue
                
            current_date = course.start_date
            while current_date <= course.end_date:
                # current_date.weekday() returns 0 for Monday, 6 for Sunday
                wd = str(current_date.weekday())
                
                # Find matching schedules for this weekday
                schedules = course.schedule_ids.filtered(lambda s: s.weekday == wd)
                
                for sched in schedules:
                    start_h = int(sched.start_time)
                    start_m = int(round((sched.start_time - start_h) * 60))
                    end_h = int(sched.end_time)
                    end_m = int(round((sched.end_time - end_h) * 60))
                    
                    sess_start = current_date.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                    sess_end = current_date.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
                    
                    # Create Session
                    self.env['school.course.session'].create({
                        'name': f"{course.name} - {sess_start.strftime('%Y-%m-%d')}",
                        'course_id': course.id,
                        'room_id': course.room_id.id,
                        'start_datetime': sess_start,
                        'end_datetime': sess_end,
                        'date': sess_start.date(),
                    })
                    
                current_date += timedelta(days=1)
