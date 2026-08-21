from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    parent_activity = fields.Selection([
        ('housewife', 'ربة بيت'),
        ('employee', 'موظف / عامل يومي'),
        ('business_owner', 'صاحب مؤسسة / شركة / جمعية'),
        ('freelancer', 'حرفي / عامل حر'),
    ], string='Current Activity')
    
    mahara_participation = fields.Selection([
        ('yes', 'نعم'),
        ('no', 'لا')
    ], string='Participated in Mahara programs before?')
    
    student_ids = fields.One2many('school.student', 'parent_id', string='Sons / Students')
    
    is_parent_form_filled = fields.Boolean(
        "Parent Form Filled", 
        compute='_compute_is_parent_form_filled', 
        store=True
    )

    @api.depends('parent_activity', 'mahara_participation')
    def _compute_is_parent_form_filled(self):
        for partner in self:
            partner.is_parent_form_filled = bool(partner.parent_activity and partner.mahara_participation)
