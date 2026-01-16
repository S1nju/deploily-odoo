from odoo import models, fields, api


class HrMessionFee(models.Model):
    _name = 'hr.mession.fee'
    _description = 'Mission Fees'

    mission_id = fields.Many2one('hr.mession', string='Mission', required=True, ondelete='cascade')
    designation = fields.Char(string='Designation', required=True)
    unit_value = fields.Float(string='Unit Value', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    number_of_days = fields.Integer(string='Number of Days', default=1)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    observations = fields.Text(string='Observations')

    @api.depends('unit_value', 'number_of_days')
    def _compute_total_amount(self):
        for fee in self:
            fee.total_amount = fee.unit_value * fee.number_of_days
