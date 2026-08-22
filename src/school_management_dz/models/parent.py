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

    # New Registration Fields
    custom_first_name = fields.Char('الاسم')
    custom_last_name = fields.Char('اللقب')
    father_name = fields.Char('اسم الأب')
    
    is_whatsapp = fields.Boolean('واتساب')
    is_telegram = fields.Boolean('تيليغرام')
    is_viber = fields.Boolean('فايبر')
    
    neighborhood_name = fields.Char('الحي')
    
    student_ids = fields.One2many('school.student', 'parent_id', string='Sons / Students')
    
    is_parent_form_filled = fields.Boolean(
        "Parent Form Filled", 
        compute='_compute_is_parent_form_filled', 
        store=True
    )
    
    wallet_balance = fields.Float('Wallet Balance', compute='_compute_wallet_balance', store=False)

    def _compute_wallet_balance(self):
        for parent in self:
            # sum all confirmed but unpaid invoices (amount_residual) -> what they owe us
            # sum all payments (or outbound/inbound prepaid)
            # An easier way: just rely on the partner's native credit/debit
            # debit = what we owe them, credit = what they owe us
            parent.wallet_balance = parent.debit - parent.credit

    @api.depends('parent_activity', 'mahara_participation')
    def _compute_is_parent_form_filled(self):
        for partner in self:
            partner.is_parent_form_filled = bool(partner.parent_activity and partner.mahara_participation)
