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

class SchoolCourse(models.Model):
    _name = 'school.course'
    _description = 'School Course'
    _inherit = ['website.published.mixin']

    name = fields.Char('Course Name', required=True)
    subcategory_id = fields.Many2one('school.service.subcategory', 'Subcategory', required=True)
    category_id = fields.Many2one('school.service.category', related='subcategory_id.category_id', store=True)
    
    tutor_id = fields.Many2one('hr.employee', 'Tutor')
    recruitment_id = fields.Many2one('hr.applicant', 'Recruitment Link')
    schedule_ids = fields.One2many('school.course.schedule', 'course_id', 'Schedules')
    test_ids = fields.One2many('school.course.test', 'course_id', 'Tests/Assessments')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    location = fields.Char('Location')
    description = fields.Html('Information')
