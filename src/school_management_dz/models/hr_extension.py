from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    center_id = fields.Many2one('school.center', 'Center')

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    center_id = fields.Many2one('school.center', 'Center')
