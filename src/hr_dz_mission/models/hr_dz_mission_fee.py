from odoo import models, fields, api


class HrMessionFee(models.Model):
    _name = 'hr.mession.fee'
    _description = 'Frais de mission'

    mission_id = fields.Many2one('hr.mession', string='Mission', required=True, ondelete='cascade')
    designation = fields.Char(string='Désignation', required=True)
    unit_value = fields.Float(string='Valeur unitaire', required=True)
    currency_id = fields.Many2one('res.currency', string='Devise', required=True, default=lambda self: self.env.company.currency_id)
    number_of_days = fields.Integer(string='Nombre de jours', default=1)
    total_amount = fields.Float(string='Montant total', compute='_compute_total_amount', store=True)
    observations = fields.Text(string='Observations')

    @api.depends('unit_value', 'number_of_days')
    def _compute_total_amount(self):
        for fee in self:
            fee.total_amount = fee.unit_value * fee.number_of_days
