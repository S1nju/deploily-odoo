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
            # Money the parent owes us (Unpaid Invoices)
            invoices = self.env['account.move'].search([
                ('partner_id', '=', parent.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial', 'in_payment'])
            ])
            owed = sum(invoices.mapped('amount_residual'))
            
            # Prepaid money the parent gave us (Unreconciled inbound payments)
            payments = self.env['account.payment'].search([
                ('partner_id', '=', parent.id),
                ('payment_type', '=', 'inbound'),
                ('state', '=', 'posted'),
                ('is_reconciled', '=', False)
            ])
            # Assuming these are advance payments, they act as positive credit
            prepaid = sum(p.amount for p in payments if not p.is_reconciled)

            # E.g. If they owe 1000 and prepaid 200, wallet_balance is negative 800 (deficit) or positive depending on context.
            # Usually if it's highlighted in red when < 0, then a positive wallet means they have money, negative means they owe money.
            # Let's set it so: wallet_balance = Prepaid - Owed. So if they owe 5000, wallet is -5000.
            parent.wallet_balance = prepaid - owed

    @api.depends('parent_activity', 'mahara_participation')
    def _compute_is_parent_form_filled(self):
        for partner in self:
            partner.is_parent_form_filled = bool(partner.parent_activity and partner.mahara_participation)
