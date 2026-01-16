from odoo import models, fields


class HrEvaluationLine(models.Model):
    _name = 'hr.evaluation.line'
    _description = 'Evaluation Criteria'

    evaluation_id = fields.Many2one('hr.evaluation', string="Evaluation", ondelete='cascade')
    criteria = fields.Char(string="Criteria", required=True)
    rating = fields.Selection([
        ('1', '1 - Poor'),
        ('2', '2 - Fair'),
        ('3', '3 - Good'),
        ('4', '4 - Very Good'),
        ('5', '5 - Excellent')
    ], string="Rating")
    comment = fields.Text(string="Comment")
