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
    
    payment_ids = fields.One2many('school.payment', 'parent_id', string='Payments')
    wallet_balance = fields.Float('Wallet Balance', compute='_compute_wallet_balance', store=True)

    @api.depends('payment_ids.amount', 'student_ids.attendance_ids.state', 'student_ids.attendance_ids.hours_attended', 'student_ids.attendance_ids.course_id.hourly_price')
    def _compute_wallet_balance(self):
        for parent in self:
            total_paid = sum(parent.payment_ids.mapped('amount'))
            
            total_consumed = 0.0
            for student in parent.student_ids:
                attended = student.attendance_ids.filtered(lambda a: a.state == 'present')
                for acc in attended:
                    hours = acc.hours_attended or 1.0
                    total_consumed += (acc.course_id.hourly_price * hours)
            
            parent.wallet_balance = total_paid - total_consumed

    @api.depends('parent_activity', 'mahara_participation')
    def _compute_is_parent_form_filled(self):
        for partner in self:
            partner.is_parent_form_filled = bool(partner.parent_activity and partner.mahara_participation)
