from odoo import models, fields, api

class SchoolStudent(models.Model):
    _name = 'school.student'
    _description = 'Student'

    name = fields.Char('Name', required=True)
    parent_id = fields.Many2one('res.partner', 'Parent', required=True)
    barcode = fields.Char('Barcode (Legacy)', readonly=True)
    qr_code = fields.Char('QR Code', readonly=True)
    image_1920 = fields.Image('Image')
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
