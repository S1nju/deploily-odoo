from odoo import models, fields

class SchoolPayment(models.Model):
    _name = 'school.payment'
    _description = 'Parent Payment'
    _order = 'date desc, id desc'
    
    name = fields.Char('Reference / Receipt', default='New')
    parent_id = fields.Many2one('res.partner', 'Parent', required=True)
    amount = fields.Float('Amount', required=True)
    date = fields.Date('Date', default=fields.Date.context_today, required=True)
    note = fields.Text('Notes')
