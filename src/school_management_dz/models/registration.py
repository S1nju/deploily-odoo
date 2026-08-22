from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError

class SchoolRegistration(models.Model):
    _name = 'school.registration'
    _description = 'Course Registration'
    
    name = fields.Char('Reference', default='New', readonly=True)
    parent_id = fields.Many2one('res.partner', 'Parent', required=True, ondelete='cascade')
    student_ids = fields.Many2many(
        'school.student', 
        'registration_student_rel', 
        'registration_id', 
        'student_id', 
        'Students'
    )
    course_id = fields.Many2one('school.course', 'Course', required=True, ondelete='cascade')
    center_id = fields.Many2one('school.center', related='course_id.center_id', store=True, string='Center')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('registered', 'Registered'),
        ('paid', 'Paid')
    ], string='Status', default='draft')
    crm_lead_id = fields.Many2one('crm.lead', 'CRM Lead', readonly=True)
    test_answers = fields.Text('Evaluation Test Answers', readonly=True)
    student_info = fields.Text('New Student Info', readonly=True)
    challenge_ids = fields.One2many('school.student.challenge', 'registration_id', 'Competency Challenges')
    
    # helper for UI access to student's uploaded grades
    grades_file = fields.Binary(related='student_ids.grades_file', string='Grades File', readonly=True)
    grades_filename = fields.Char(related='student_ids.grades_filename', string='Grades Filename', readonly=True)

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
                sessions = course.session_ids
                if sessions:
                    Attendance = self.env['school.attendance']
                    for session in sessions:
                        existing = Attendance.search([
                            ('student_id', 'in', reg.student_ids.ids),
                            ('session_id', '=', session.id)
                        ])
                        existing_student_ids = existing.mapped('student_id.id')
                        for student in reg.student_ids:
                            if student.id not in existing_student_ids:
                                Attendance.sudo().create({
                                    'student_id': student.id,
                                    'course_id': course.id,
                                    'session_id': session.id,
                                    'date': session.start_datetime.date() if session.start_datetime else fields.Date.today(),
                                    'state': 'pending'
                                })
        return res

    @api.constrains('student_ids', 'course_id')
    def _check_unique_student_registration(self):
        for reg in self:
            if not reg.course_id or not reg.student_ids:
                continue
            for student in reg.student_ids:
                duplicate = self.env['school.registration'].search([
                    ('id', '!=', reg.id),
                    ('course_id', '=', reg.course_id.id),
                    ('student_ids', 'in', student.id)
                ], limit=1)
                if duplicate:
                    raise ValidationError(f"The student '{student.name}' is already registered for the course '{reg.course_id.name}'.")
