from odoo import models, fields


class HrEvaluationLine(models.Model):
    _name = 'hr.evaluation.line'
    _description = 'Critères d’évaluation'

    evaluation_id = fields.Many2one(
        'hr.evaluation',
        string="Évaluation",
        ondelete='cascade'
    )

    criteria = fields.Char(
        string="Critère",
        required=True
    )

    rating = fields.Selection([
        ('1', '1 - Insuffisant'),
        ('2', '2 - Passable'),
        ('3', '3 - Bien'),
        ('4', '4 - Très bien'),
        ('5', '5 - Excellent')
    ], string="Note")

    comment = fields.Text(
        string="Commentaire"
    )