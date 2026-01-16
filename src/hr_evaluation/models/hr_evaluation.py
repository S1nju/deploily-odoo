from odoo import models, fields


class HrEvaluation(models.Model):
    _name = 'hr.evaluation'
    _description = 'Employee Evaluation'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    evaluation_date = fields.Date(string="Evaluation Date", default=fields.Date.today)
    evaluator_id = fields.Many2one('hr.employee', string="Evaluator")
    rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Below Average'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent')
    ], string="Overall Rating")
    comments = fields.Text(string="Comments")
    line_ids = fields.One2many('hr.evaluation.line', 'evaluation_id', string="Evaluation Lines")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('archived', 'Archived')
    ], string="State", default='draft')
