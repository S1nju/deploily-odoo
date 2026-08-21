from odoo import models, fields, api
from datetime import timedelta

class SchoolRegistration(models.Model):
    _name = 'school.registration'
    _description = 'Course Registration'
    
    name = fields.Char('Reference', default='New', readonly=True)
    parent_id = fields.Many2one('res.partner', 'Parent', required=True)
    student_ids = fields.Many2many(
        'school.student', 
        'registration_student_rel', 
        'registration_id', 
        'student_id', 
        'Students'
    )
    course_id = fields.Many2one('school.course', 'Course', required=True)
    center_id = fields.Many2one('school.center', related='course_id.center_id', store=True, string='Center')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('registered', 'Registered'),
        ('paid', 'Paid')
    ], string='Status', default='draft')
    crm_lead_id = fields.Many2one('crm.lead', 'CRM Lead', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                seq = self.env['ir.sequence'].next_by_code('school.registration.seq')
                vals['name'] = seq if seq else 'New'
        return super(SchoolRegistration, self).create(vals_list)

    def write(self, vals):
        res = super(SchoolRegistration, self).write(vals)
        if vals.get('state') == 'paid':
            for reg in self:
                course = reg.course_id
                start = course.start_date.date() if course.start_date else fields.Date.today()
                end = course.end_date.date() if course.end_date else start + timedelta(days=30)
                
                schedules = course.schedule_ids
                if schedules:
                    valid_weekdays = [int(s.weekday) for s in schedules]
                    Attendance = self.env['school.attendance']
                    current_date = start
                    while current_date <= end:
                        if current_date.weekday() in valid_weekdays:
                            existing = Attendance.search([
                                ('student_id', 'in', reg.student_ids.ids),
                                ('course_id', '=', course.id),
                                ('date', '=', current_date)
                            ])
                            existing_student_ids = existing.mapped('student_id.id')
                            for student in reg.student_ids:
                                if student.id not in existing_student_ids:
                                    Attendance.sudo().create({
                                        'student_id': student.id,
                                        'course_id': course.id,
                                        'date': current_date,
                                        'state': 'pending'
                                    })
                        current_date += timedelta(days=1)
        return res
