from odoo import models, fields, api

class SchoolStudent(models.Model):
    _name = 'school.student'
    _description = 'Student'

    _sql_constraints = [
        ('unique_name_per_parent', 'UNIQUE(name, parent_id)', 'A father cannot have two sons with the same name!')
    ]

    name = fields.Char('Name', required=True)
    parent_id = fields.Many2one('res.partner', 'Parent', required=True)
    qr_code = fields.Char('QR Code')
    image_1920 = fields.Image('Image')
    
    # Detailed Form Fields
    custom_first_name = fields.Char('الاسم')
    custom_last_name = fields.Char('اللقب')
    father_name = fields.Char('اسم الأب')
    birth_date = fields.Date('تاريخ الميلاد')
    quranic_school = fields.Char('المدرسة القرآنية')
    neighborhood = fields.Char('الحي')
    family_status = fields.Selection([
        ('both', 'الأب والأم معاً'),
        ('mother', 'الأم فقط'),
        ('father', 'الأب فقط'),
        ('guardian', 'وصي قانوني / أحد أفراد العائلة'),
    ], string='الوضع العائلي / إقامة التلميذ')
    
    relationship = fields.Selection([
        ('father', 'أب'),
        ('mother', 'أم'),
        ('guardian', 'وكيل'),
        ('family', 'أحد أفراد العائلة'),
        ('self', 'أنا هو المعني - الطالب (ة)'),
    ], string='Relationship to Participant')
    attendance_ids = fields.One2many('school.attendance', 'student_id', 'Attendance')
    
    registration_ids = fields.Many2many(
        'school.registration', 
        'registration_student_rel', 
        'student_id', 
        'registration_id', 
        'Registrations'
    )
    center_ids = fields.Many2many('school.center', compute='_compute_center_ids', store=True, string='Centers')
    wallet_balance = fields.Float(related='parent_id.wallet_balance', store=True, string='Parent Wallet')
    
    grades_file = fields.Binary('Previous Grades File')
    grades_filename = fields.Char('Grades Filename')

    @api.depends('registration_ids.center_id')
    def _compute_center_ids(self):
        for student in self:
            student.center_ids = student.registration_ids.mapped('center_id')

    @api.model_create_multi
    def create(self, vals_list):
        records = super(SchoolStudent, self).create(vals_list)
        for record in records:
            if not record.qr_code:
                record.qr_code = f"STD-{record.id:06d}"
        return records
